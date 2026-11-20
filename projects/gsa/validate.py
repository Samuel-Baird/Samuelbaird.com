#!/usr/bin/env python3
"""GSA candidate file validation. Standard library plus external CLI tools
(ClamAV or another configured scanner, poppler, qpdf, ffprobe for media).

The report separates AUTOMATED CHECKS (machine-verifiable; a failure or a tool
error blocks) from STAFF JUDGMENT items the tools cannot decide. A passing
automated verdict is never an approval. PDFs are also classified as scan,
born-digital or likely ebook conversion and given a ranking score, because the
owner prefers scans and original PDFs over EPUB-converted PDFs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import shlex
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys

STAFF_JUDGMENT = (
    ('bibliographic_match', 'Title, author, edition, year and language match the request and the reviewed source'),
    ('first_and_last_pages', 'First pages (title, copyright) and last pages (index, back matter) are present and legible'),
    ('body_spot_check', 'Body spot-checked for missing, duplicated, blank, cropped or out-of-order pages'),
    ('completeness', 'Whole work present (all volumes/parts); not an excerpt or sample'),
    ('filename_and_destination', 'Filename follows the volunteer manual and the destination shelf is right'),
    ('format_preference', 'If flagged as an ebook conversion, look for a scan or original PDF before accepting'),
)

SIGNATURES = {
    '.pdf': lambda m: m.startswith(b'%PDF-'),
    '.mp3': lambda m: m.startswith(b'ID3') or (len(m) > 1 and m[0] == 0xFF and m[1] & 0xE0 == 0xE0),
    '.mp4': lambda m: m[4:8] == b'ftyp',
}
FOREIGN = (  # content that must never hide behind an allowed extension
    (b'MZ', 'windows_executable'), (b'\x7fELF', 'elf_executable'),
    (b'\xcf\xfa\xed\xfe', 'macho_executable'), (b'\xca\xfe\xba\xbe', 'macho_universal'),
    (b'PK\x03\x04', 'zip_container'), (b'Rar!', 'rar_archive'), (b'7z\xbc\xaf', '7z_archive'),
    (b'#!', 'script'), (b'<html', 'html'), (b'<!DOCTYPE', 'html'), (b'AT&TFORM', 'djvu'),
)

EBOOK_PRODUCERS = re.compile(
    r'calibre|ebook-convert|adobe digital editions|kindle|kindlegen|readium|epub|mobipocket|'
    r'sigil|apple books|ibooks|kobo|fbreader|pandoc|wkhtmltopdf|weasyprint|prince', re.I)
SCAN_PRODUCERS = re.compile(
    r'abbyy|finereader|paper capture|scansnap|tesseract|ocrmypdf|internet archive|'
    r'luratech|kofax|omnipage|readiris|capture|scanner|xerox|canon|ricoh|konica|sharp|epson|'
    r'hp digital sending|djvu|bookscan|scantailor|img2pdf', re.I)
OCR_FONTS = re.compile(r'glyphless|invisible|ocr|hiddenhorzocr', re.I)
EBOOK_FILENAME = re.compile(r'epub|mobi|azw|kindle|calibre', re.I)

BASE_SCORE = {'scan': 80, 'born_digital': 80, 'mixed': 60, 'unknown': 40, 'likely_ebook_conversion': 15}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _run(cmd, run, timeout=300):
    try:
        r = run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return None, '', f'{cmd[0]} not installed'
    except subprocess.TimeoutExpired:
        return None, '', f'{cmd[0]} timed out'
    return r.returncode, r.stdout, r.stderr


def check(status, detail, **extra):
    return dict(status=status, detail=detail, **extra)


# ---------------------------------------------------------------- generic checks

def check_signature(path):
    with Path(path).open('rb') as f:
        magic = f.read(64)
    ext = Path(path).suffix.lower()
    for prefix, kind in FOREIGN:
        if magic.lstrip()[:len(prefix)].lower() == prefix.lower():
            return check('fail', f'content looks like {kind}, not {ext or "a supported file"}')
    test = SIGNATURES.get(ext)
    if test is None:
        return check('fail', f'unsupported extension {ext!r} (PDF, MP3 or MP4 only)')
    if not test(magic):
        return check('fail', f'{ext} extension but file signature does not match')
    return check('pass', f'{ext} signature matches')


def check_size(path, config):
    size = Path(path).stat().st_size
    limit = config.get('max_file_bytes')
    if size == 0:
        return check('fail', 'empty file', bytes=size)
    if limit and size > int(limit):
        return check('fail', f'{size} bytes exceeds max_file_bytes {limit}', bytes=size)
    return check('pass', f'{size} bytes', bytes=size)


def scan_malware(path, config, run=subprocess.run):
    """Exit 0 = clean; codes in scanner_infected_codes (default [1], ClamAV's)
    = infected; anything else, including a missing tool, is an error. Errors
    never count as clean."""
    cmd = config.get('scanner_command')
    if not isinstance(cmd, list) or not cmd:
        return check('error', 'no scanner_command configured')
    code, out, err = _run([*cmd, str(path)], run, timeout=int(config.get('scanner_timeout', 900)))
    tail = (out + err).strip()[-500:]
    if code == 0:
        return check('pass', 'scanner reported clean', command=cmd)
    if code in config.get('scanner_infected_codes', [1]):
        return check('fail', 'MALWARE DETECTED: ' + tail, command=cmd)
    return check('error', f'scanner error (exit {code}): {tail or err}', command=cmd)


def clamav_db_age(config, run=subprocess.run, now=None):
    """ClamAV only: read the signature date from `clamscan --version` against the
    configured database and compare with scanner_max_db_age_hours."""
    cmd = config.get('scanner_command') or []
    max_age = config.get('scanner_max_db_age_hours')
    if not cmd or Path(cmd[0]).name != 'clamscan' or not max_age:
        return check('skip', 'scanner freshness not configured (scanner_max_db_age_hours)')
    db = [a for a in cmd if a.startswith('--database=') or a.startswith('-d')]
    code, out, err = _run(['clamscan', *db, '--version'], run, timeout=60)
    m = re.search(r'/(\d+)/(\w{3} \w{3} +\d+ [\d:]+ \d{4})', out or '')
    if code != 0 or not m:
        return check('error', f'cannot read ClamAV database date: {(out + err).strip()[:200]}')
    # clamscan prints the build time with ctime() in the local zone.
    built = datetime.strptime(' '.join(m.group(2).split()), '%a %b %d %H:%M:%S %Y').astimezone()
    age = ((now or datetime.now(timezone.utc)) - built).total_seconds() / 3600
    status = 'pass' if age <= float(max_age) else 'fail'
    return check(status, f'signatures version {m.group(1)} built {built.isoformat()} ({age:.0f} h old)')


# ---------------------------------------------------------------- PDF tool parsing

def parse_pdfinfo(text):
    info, pages = {}, []
    for line in text.splitlines():
        m = re.match(r'Page\s+(\d+)\s+size:\s+([\d.]+) x ([\d.]+) pts', line)
        if m:
            pages.append((float(m.group(2)), float(m.group(3))))
            continue
        if ':' in line:
            key, value = line.split(':', 1)
            info[key.strip()] = value.strip()
    info['_page_sizes'] = pages
    return info


def _table(text):
    """Parse poppler's fixed-width tables using the dashed separator line."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('---'):
            spans = [(m.start(), m.end()) for m in re.finditer(r'-+', line)]
            header = lines[i - 1] if i else ''
            names = [header[a:b + 1].strip() or f'c{n}' for n, (a, b) in enumerate(spans)]
            rows = []
            for row in lines[i + 1:]:
                if row.strip():
                    cells = [row[a:(spans[n + 1][0] if n + 1 < len(spans) else len(row))].strip()
                             for n, (a, _) in enumerate(spans)]
                    rows.append(dict(zip(names, cells)))
            return rows
    return []


def parse_pdffonts(text):
    return [{'name': r.get('name', ''), 'type': r.get('type', ''), 'embedded': r.get('emb') == 'yes'} for r in _table(text)]


def parse_pdfimages(text):
    images = []
    for line in text.splitlines()[2:]:
        parts = line.split()
        if len(parts) < 14 or not parts[0].isdigit():
            continue
        def num(v):
            try:
                return float(v)
            except ValueError:
                return 0.0
        images.append({'page': int(parts[0]), 'type': parts[2], 'width': int(parts[3]), 'height': int(parts[4]),
                       'color': parts[5], 'x_ppi': num(parts[12]), 'y_ppi': num(parts[13])})
    return images


def classify_pdf(info, fonts, images, filename=''):
    """Classify a PDF from parsed poppler output. Returns class, ranking score
    inputs, evidence and reviewer flags. Heuristic: staff confirm."""
    pages = int(info.get('Pages', '0') or 0)
    sizes = info.get('_page_sizes') or []
    page_area = {i + 1: w * h for i, (w, h) in enumerate(sizes)}
    default_area = (statistics.median([w * h for w, h in sizes]) if sizes else 612 * 792)
    covered, ppis = set(), []
    for img in images:
        if img['type'] != 'image' or not img['x_ppi'] or not img['y_ppi']:
            continue
        area = (img['width'] / img['x_ppi'] * 72) * (img['height'] / img['y_ppi'] * 72)
        if area >= 0.5 * page_area.get(img['page'], default_area):
            covered.add(img['page'])
            ppis.append(min(img['x_ppi'], img['y_ppi']))
    scan_ratio = len(covered) / pages if pages else 0
    text_fonts = [f for f in fonts if not OCR_FONTS.search(f['name'])]
    ocr_fonts = [f for f in fonts if OCR_FONTS.search(f['name'])]
    producer = ' / '.join(v for v in (info.get('Producer', ''), info.get('Creator', '')) if v)
    title = info.get('Title', '')
    uniform = len({(round(w), round(h)) for w, h in sizes}) == 1 if sizes else False
    evidence, weak = [], []

    strong_ebook = bool(EBOOK_PRODUCERS.search(producer))
    if strong_ebook:
        evidence.append(f'producer/creator names an ebook converter: {producer!r}')
    if re.search(r'\.(epub|mobi|azw3?)\b', title, re.I):
        weak.append(f'title metadata names an ebook file: {title!r}')
    if EBOOK_FILENAME.search(filename):
        weak.append(f'filename mentions an ebook format: {filename!r}')
    if sizes and uniform and not covered and text_fonts and sizes[0][0] <= 400:
        weak.append(f'uniform small reflow-style pages ({sizes[0][0]:.0f}x{sizes[0][1]:.0f} pt) with no page images')
    scan_meta = bool(SCAN_PRODUCERS.search(producer))
    if scan_meta:
        evidence.append(f'producer/creator names scanning/OCR software: {producer!r}')
    evidence.append(f'{len(covered)}/{pages} pages carry a page-sized image; {len(text_fonts)} text fonts, {len(ocr_fonts)} OCR-layer fonts')

    if strong_ebook or len(weak) >= 2:
        cls = 'likely_ebook_conversion'
    elif pages and scan_ratio >= 0.8:
        cls = 'scan'
    elif pages and scan_ratio >= 0.2:
        cls = 'mixed'
    elif pages and text_fonts:
        cls = 'born_digital'
    elif scan_meta and pages:
        cls = 'scan'
    else:
        cls = 'unknown'
    evidence.extend(weak)

    flags = []
    if cls == 'likely_ebook_conversion':
        flags.append('LIKELY EBOOK CONVERSION: page breaks and pagination may not match the print edition. Prefer a scan or original PDF if one exists.')
    elif weak:
        flags.append('Possible ebook conversion signal: ' + '; '.join(weak))
    if cls == 'mixed':
        flags.append(f'MIXED: only {len(covered)} of {pages} pages are page images (partial scan, inserts, or plates). Check the body.')
    if cls == 'unknown':
        flags.append('UNCLASSIFIED: no text fonts and no page-sized images detected. Open and inspect.')
    median_ppi = statistics.median(ppis) if ppis else None
    if cls == 'scan' and median_ppi and median_ppi < 150:
        flags.append(f'LOW-RESOLUTION SCAN: median {median_ppi:.0f} ppi')
    if cls == 'scan' and not fonts:
        flags.append('Scan has no text layer (not searchable); OCR may help after approval.')
    return {'class': cls, 'scan_page_ratio': round(scan_ratio, 3), 'median_scan_ppi': median_ppi,
            'text_fonts': len(text_fonts), 'ocr_fonts': len(ocr_fonts), 'pages': pages,
            'uniform_page_size': uniform, 'producer': producer, 'evidence': evidence, 'flags': flags}


def ranking_score(classification, qpdf_status='pass', encrypted=False):
    """0-100. Higher is preferred when choosing between candidates of one work.
    Scans and born-digital PDFs outrank ebook conversions. Not a gate."""
    score = BASE_SCORE[classification['class']]
    ppi = classification.get('median_scan_ppi')
    if classification['class'] == 'scan' and ppi:
        score += 5 if ppi >= 300 else (-15 if ppi < 150 else 0)
    if classification['class'] == 'scan' and (classification.get('ocr_fonts') or classification.get('text_fonts')):
        score += 5  # searchable text layer
    score -= {'pass': 0, 'warn': 5}.get(qpdf_status, 30)
    if encrypted:
        score -= 10
    return max(0, min(100, score))


def pdf_checks(path, run=subprocess.run, max_pages=5000):
    checks, details = {}, {}
    code, out, err = _run(['pdfinfo', str(path)], run)
    if code != 0:
        checks['pdfinfo'] = check('error' if code is None else 'fail', f'pdfinfo failed: {err.strip()[:300]}')
        return checks, None
    info = parse_pdfinfo(out)
    pages = int(info.get('Pages', '0') or 0)
    checks['pdfinfo'] = check('pass' if pages > 0 else 'fail', f'{pages} pages, PDF {info.get("PDF version", "?")}')
    encrypted = info.get('Encrypted', 'no').lower().startswith('yes')
    checks['not_encrypted'] = check('warn' if encrypted else 'pass', info.get('Encrypted', 'no'))
    if pages:
        code, out, err = _run(['pdfinfo', '-f', '1', '-l', str(min(pages, max_pages)), str(path)], run)
        if code == 0:
            info['_page_sizes'] = parse_pdfinfo(out)['_page_sizes']
    code, out, err = _run(['qpdf', '--check', str(path)], run)
    # qpdf: 0 ok, 3 warnings, 2 errors.
    qstatus = {0: 'pass', 3: 'warn'}.get(code, 'error' if code is None else 'fail')
    checks['qpdf_check'] = check(qstatus, ' '.join((out + err).split())[:300])
    code, out, err = _run(['pdffonts', '-l', str(min(pages, max_pages)), str(path)], run)
    fonts = parse_pdffonts(out) if code == 0 else []
    checks['pdffonts'] = check('pass' if code == 0 else ('error' if code is None else 'fail'),
                               f'{len(fonts)} fonts' if code == 0 else err.strip()[:300])
    code, out, err = _run(['pdfimages', '-list', '-l', str(min(pages, max_pages)), str(path)], run)
    images = parse_pdfimages(out) if code == 0 else []
    checks['pdfimages'] = check('pass' if code == 0 else ('error' if code is None else 'fail'),
                                f'{len(images)} images' if code == 0 else err.strip()[:300])
    cls = classify_pdf(info, fonts, images, Path(path).name)
    details = {'info': {k: v for k, v in info.items() if not k.startswith('_')}, 'classification': cls,
               'ranking_score': ranking_score(cls, qstatus, encrypted)}
    return checks, details


def media_checks(path, run=subprocess.run):
    code, out, err = _run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', str(path)], run)
    if code == 0:
        return {'ffprobe': check('pass', 'container and streams readable')}
    return {'ffprobe': check('error' if code is None else 'fail', err.strip()[:300] or 'ffprobe failed')}


TOOLS = (('clamscan', ['clamscan', '--version']), ('pdfinfo', ['pdfinfo', '-v']),
         ('qpdf', ['qpdf', '--version']), ('ffprobe', ['ffprobe', '-version']))


def tool_versions(run=subprocess.run):
    out = {}
    for name, cmd in TOOLS:
        code, stdout, stderr = _run(cmd, run, timeout=30)
        text = (stdout or stderr).strip().splitlines()
        out[name] = text[0] if code == 0 and text else 'not installed'
    return out


# ---------------------------------------------------------------- report

REQUIRED_PASS = ('size', 'signature', 'malware_scan', 'unchanged_during_validation')


def validate(path, config, run=subprocess.run):
    """Run every automated check on one candidate and build the review report."""
    path = Path(path)
    automated = {'size': check_size(path, config), 'signature': check_signature(path)}
    before = sha256(path)
    details = None
    if automated['signature']['status'] == 'pass':
        automated['malware_scan'] = scan_malware(path, config, run)
        freshness = clamav_db_age(config, run)
        if freshness['status'] != 'skip':
            automated['scanner_signatures_fresh'] = freshness
        if path.suffix.lower() == '.pdf':
            extra, details = pdf_checks(path, run)
        else:
            extra = media_checks(path, run)
        automated.update(extra)
    after = sha256(path)
    automated['sha256'] = check('pass', before)
    automated['unchanged_during_validation'] = check('pass' if before == after else 'fail',
                                                     'hash stable' if before == after else 'file changed while validating')
    failed = [k for k, v in automated.items() if v['status'] in ('fail', 'error')]
    missing = [k for k in REQUIRED_PASS if k not in automated]
    verdict = 'pass' if not failed and not missing else 'fail'
    flags = list(details['classification']['flags']) if details else []
    flags += [f'{k}: {v["detail"]}' for k, v in automated.items() if v['status'] == 'warn']
    return {
        'file': path.name,
        'sha256': before,
        'checked_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'automated_checks': automated,
        'automated_verdict': verdict,
        'automated_failures': failed + [f'{k} (not run)' for k in missing],
        'pdf': details,
        'ranking_score': details['ranking_score'] if details else None,
        'reviewer_flags': flags,
        'staff_judgment': [{'item': k, 'question': q, 'status': 'pending'} for k, q in STAFF_JUDGMENT],
        'tool_versions': tool_versions(run),
        'note': 'Automated checks cannot establish bibliographic match or completeness. Staff must record each judgment item.',
    }


def rank(reports):
    """Order candidate reports for the same work: automated passes first, then score."""
    return sorted(reports, key=lambda r: (r['automated_verdict'] != 'pass', -(r['ranking_score'] or 0)))


def render(report):
    lines = [f"Candidate: {report['file']}", f"SHA-256:   {report['sha256']}", '',
             f"== AUTOMATED CHECKS: {report['automated_verdict'].upper()} =="]
    for name, c in report['automated_checks'].items():
        lines.append(f"  [{c['status'].upper():5}] {name}: {c['detail']}")
    if report['pdf']:
        cls = report['pdf']['classification']
        lines += ['', f"== PDF TYPE: {cls['class'].replace('_', ' ').upper()} (ranking score {report['ranking_score']}/100) =="]
        lines += [f'  - {e}' for e in cls['evidence']]
    if report['reviewer_flags']:
        lines += ['', '== FLAGS FOR THE REVIEWER ==']
        lines += [f'  ! {f}' for f in report['reviewer_flags']]
    lines += ['', '== STAFF JUDGMENT REQUIRED (not decided by any tool) ==']
    lines += [f"  [ ] {s['item']}: {s['question']}" for s in report['staff_judgment']]
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--config', type=Path, help='Private pipeline config (read only)')
    parser.add_argument('--scanner', help='Override scanner command (shell-quoted), e.g. \'clamscan --no-summary "--database=DIR"\'')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    config = json.loads(args.config.read_text()) if args.config else {}
    if args.scanner:
        config['scanner_command'] = shlex.split(args.scanner)
    reports = rank([validate(f, config) for f in args.files])
    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        print('\n\n'.join(render(r) for r in reports))
    return 0 if all(r['automated_verdict'] == 'pass' for r in reports) else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
