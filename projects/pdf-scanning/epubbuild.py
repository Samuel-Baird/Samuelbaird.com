"""Reflowable EPUB from a scanned book, rebuilt from Windows OCR line positions.

What it reconstructs: chapters (matched against the printed contents), parts, headings,
paragraphs (first-line indents, page turns), numbered/bulleted lists, block quotes,
reading lists, the index, and front matter pages named in the book's config.

It was built on an edited volume whose contents list "N. Title" lines followed by an author
line, with chapter openings in large type. Other layouts will likely need the chapter
detection adjusted. Everything book-specific lives in a JSON config (see books/).

OCR repair, in order: known misreads (config + built-in), the "Th" ligature read as rlh/ff/lh,
dropped ligatures (affrm -> affirm, offcially -> officially), "kl" read as "ld", words run
together ("ofa"), words clipped at the spine (completed only when one dictionary word
clearly wins), and "Th..." words dropped at the start of a line (recovered from the
RapidOCR cache of the same PDF, if there is one).
"""
import difflib, html, io, json, re

import pymupdf as fitz
from PIL import Image
from wordfreq import iter_wordlist, zipf_frequency
from ebooklib import epub

from winocr import page_image


def known(w, z=1.0):
    return zipf_frequency(w.lower(), 'en') >= z


VOCAB = {}
for _i, _w in enumerate(iter_wordlist('en')):
    if _i > 120000:
        break
    if _w.isalpha():
        VOCAB.setdefault(_w[:3], []).append(_w)

LIG = ['fi', 'fl', 'ff', 'ffi', 'ffl']
FIXES = {'Tlis': 'This', 'lhe': 'The', 'Tie': 'The', 'Tle': 'The', 'tle': 'the', 'Ihe': 'The', 'YVhat': 'What',
         'YVho': 'Who', 'YVhy': 'Why', 'Tiere': 'There', 'Tlere': 'There', 'Tley': 'They', 'Tlat': 'That',
         'Tlese': 'These', 'Tlose': 'Those', 'Tlough': 'Though',
         'ofa': 'of a', 'ofthe': 'of the', 'inthe': 'in the', 'tothe': 'to the', 'onthe': 'on the',
         'andthe': 'and the', 'ofhis': 'of his', 'ofher': 'of her', 'ofits': 'of its', 'ofan': 'of an',
         'ffe': 'The', 'rlhe': 'The', 'rlhey': 'They', 'rlhose': 'Those', 'rlhis': 'This', 'lhey': 'They'}
SMALL = ('of', 'a', 'the', 'to', 'in', 'and', 'on', 'is', 'as', 'at', 'by', 'or', 'an', 'it')
TH = re.compile(r'^(rlh|rh|lh|ff|Ih)(?=[a-z])')
JUNK = re.compile(r"^([^A-Za-z]*)([a-z]+)[€\]\[|}{¢©®£¥]$")
LIST = re.compile(r'^(•|·|◦|o\s(?=[A-Z])|e\s(?=[A-Z])|(\d{1,2}|l)\.\s+[A-Z])')
TERM = re.compile(r'[.?!:"”)\]]$')
ENTRY = re.compile(r"^([A-Z][\w'’.-]+(\s(van|de|von|[A-Z][\w'’.-]+))*,\s|See also)")
CHNUM = re.compile(r'^[\dIOlS]{1,3}$')

_cache = {}


def repair_word(w):
    if w in _cache:
        return _cache[w]
    out = w
    m = re.fullmatch(r"([^A-Za-z]*)([A-Za-z]+)([^A-Za-z]*)", w)
    if m:
        pre, core, post = m.groups()
        if core in FIXES:
            out = pre + FIXES[core] + post
        elif len(core) >= 3 and not known(core, 1.5) and not core[0].isupper():
            best = None
            for i in range(1, len(core)):                       # dropped ligature
                for lg in LIG + (['i', 'l'] if core[i - 1] == 'f' else []):
                    c = core[:i] + lg + core[i:]
                    z = zipf_frequency(c.lower(), 'en')
                    if z >= 2.0 and (best is None or z > best[0]):
                        best = (z, c)
            if best is None and 'ld' in core:                   # "kl" read as "ld"
                c = core.replace('ld', 'kl')
                if known(c, 2.0):
                    best = (0, c)
            if best is None:                                    # words run together
                for a in SMALL:
                    rest = core[len(a):]
                    if core.lower().startswith(a) and rest and (known(rest, 3.0) or rest == 'a'):
                        best = (0, core[:len(a)] + ' ' + rest); break
            if best is None:
                for a in SMALL:
                    head = core[:-len(a)]
                    if core.lower().endswith(a) and len(head) >= 3 and known(head, 3.0):
                        best = (0, head + ' ' + core[-len(a):]); break
            if best:
                out = pre + best[1] + post
    _cache[w] = out
    return out


def fix_th(w):
    m = re.fullmatch(r"([^A-Za-z]*)([A-Za-z]+)(.*)", w)
    if not m or known(m.group(2), 1.5):
        return w
    c = TH.sub('Th', m.group(2))
    return m.group(1) + c + m.group(3) if c != m.group(2) and known(c, 2.0) else w


def complete_clipped(tok):
    j = JUNK.match(tok)
    if j:                       # last letter clipped and read as a symbol: exactly one letter missing
        stem = j.group(2)
        pool = VOCAB.get(stem[:3], []) + [stem + c for c in 'abcdefghijklmnopqrstuvwxyz']
        cands = sorted({(zipf_frequency(w, 'en'), w) for w in pool
                        if w.startswith(stem) and len(w) == len(stem) + 1 and known(w, 2.0)}, reverse=True)
        if cands and (len(cands) == 1 or cands[0][0] - cands[1][0] >= 0.3):
            return j.group(1) + cands[0][1]
        return j.group(1) + stem
    m = re.fullmatch(r"([^A-Za-z]*)([a-z]{3,})([^A-Za-z]*)", tok)
    if not m or known(m.group(2), 1.0):
        return tok
    core = m.group(2); cands = {}
    for stem in (core, core[:-1]):          # the last visible letter may be half cut and misread
        for w in VOCAB.get(stem[:3], []):
            if w.startswith(stem) and 0 < len(w) - len(stem) <= 2:
                cands[w] = zipf_frequency(w, 'en')
    ranked = sorted(cands.items(), key=lambda kv: -kv[1])
    if ranked and (len(ranked) == 1 or ranked[0][1] - ranked[1][1] >= 0.7):
        return m.group(1) + ranked[0][0] + m.group(3)
    return tok


def join(a, b):
    if not a:
        return b
    if a.endswith('-') and not a.endswith('--'):
        left = re.findall(r'([A-Za-z]+)-$', a); right = re.findall(r'^([A-Za-z]+)', b)
        if left and right and known(left[0] + right[0], 1.5) and not right[0][0].isupper():
            return a[:-1] + b                   # soft hyphen at a line break
        return a + b                            # real hyphen (Latter-day)
    last = a.split(' ')[-1]
    if ('http' in last or 'www.' in last or '/' in last) and b[:1] in '.-/#_?=&':
        return a + b                            # URL broken across lines
    return a + ' ' + b


class Book:
    def __init__(self, pdf, cfg, win, rapid=None):
        self.pdf, self.cfg, self.R = pdf, cfg, win
        self.N = max(win)
        self.H = sorted(r['h'] for r in win.values())[len(win) // 2]   # book's typical page height
        self.recovered = []
        self.text_fixes = [(re.compile(a), b) for a, b in cfg.get('text_fixes', [])]
        self.rapid = {}
        for p, r in (rapid or {}).items():
            self.rapid[p] = [(re.sub(r'[^a-z]', '', l.lower()), re.sub(r'[^A-Za-z]', '', l))
                             for l in r['text'].split('\n')]
        self._lines = {}

    # ----- text -----
    def repair(self, text):
        text = re.sub(r'(^|\s)l\.(?=\s+[A-Z])', r'\g<1>1.', text)
        for rx, rep in self.text_fixes:
            text = rx.sub(rep, text)
        return ' '.join(repair_word(fix_th(w)) for w in text.split(' '))

    def lead_word(self, p, t):
        key = re.sub(r'[^a-z]', '', t.lower())[:18]
        if len(key) < 10:
            return None
        for rl, raw in self.rapid.get(p, []):
            i = rl.find(key)
            if 0 < i <= 9:
                return raw[:i] if rl[:i].startswith('th') and known(rl[:i], 3.0) else None
        return None

    # ----- geometry (thresholds are fractions of the book's median page height, tuned on ~340 dpi scans) -----
    def is_running_header(self, l):
        t = l['t']
        numbered = re.search(r'(^[\dxvil]+\s)|(\s[\dxvil]+$)|^[\dxvil]+$', t)
        if l['h'] < 0.0145 and numbered:                # small type with a page number
            return True
        letters = re.sub(r'[^A-Za-z]', '', t)
        caps = len(letters) >= 10 and letters.upper() == letters
        if caps and (numbered or '—' in t or re.search(r'[A-Z]-[A-Z]', t)):
            return True                                 # "84 BOOK TITLE" / "AUTHOR—CHAPTER? 85"
        rx = self.cfg.get('header_regex')
        return bool(rx and re.search(rx, t))

    def page_lines(self, p):
        if p in self._lines:
            return [dict(l) for l in self._lines[p]]
        r = self.R[p]; H = self.H
        L = [dict(l) for l in r['lines'] if l['t'].strip()]
        for l in L:
            l['h'] = (l['y2'] - l['y']) / H; l['t'] = l['t'].strip()
        if L and self.is_running_header(L[0]):
            L = L[1:]
        if L and L[-1]['h'] < 0.0145 and re.fullmatch(r'[\dxvil]+', L[-1]['t']):
            L = L[:-1]                                  # folio at the foot
        body = [l for l in L if l['h'] >= 0.0133] or L
        left = sorted(l['x'] for l in body)[len(body) // 5] if body else 0
        right = sorted(l['x2'] for l in body)[int(len(body) * 0.9)] if body else r['w']
        for l in L:
            first = l['t'].split(' ')[0]
            if self.rapid and (l['t'][:1].islower() or first in ('ffe', 'rlhe', 'lhe')):
                w = self.lead_word(p, l['t'])
                if w:
                    if first in ('ffe', 'rlhe', 'lhe'):
                        l['t'] = l['t'].split(' ', 1)[1] if ' ' in l['t'] else ''
                    self.recovered.append((p, w, l['t'][:30]))
                    l['t'] = w + ' ' + l['t']
            if l['x2'] >= r['w'] - 6 and not l['t'].endswith('-'):
                ws = l['t'].split(' '); ws[-1] = complete_clipped(ws[-1]); l['t'] = ' '.join(ws)
            l['rel'] = (l['x'] - left) / r['w']
            l['short'] = l['x2'] < right - 0.05 * r['w']
            l['page'] = p
        self._lines[p] = L
        return [dict(l) for l in L]

    # ----- paragraphs -----
    def is_heading(self, l, nxt, prev_ended):
        t = l['t']
        if l['rel'] > 0.02 or not l['short'] or len(t) > 70 or TERM.search(t) or t.endswith((',', ';', '-')):
            return False
        if not (t[0].isupper() or t[0].isdigit()) or LIST.match(t) or not prev_ended:
            return False
        return nxt is None or nxt['rel'] <= 0.02

    def blocks(self, lines):
        cfg = self.cfg
        subheads = {s.lower() for s in cfg.get('subheads', [])}
        refs_on = cfg.get('refs_heading', '').lower()
        refs_off = {s.lower() for s in cfg.get('refs_end_headings', [])}
        out = []; cur = None; prev = None; mode = 'body'; ended = True; cur_rel = 0; cur_n = 0

        def flush():
            nonlocal cur
            if cur and cur[1].strip():
                out.append((cur[0], self.repair(cur[1].strip())))
            cur = None

        for i, l in enumerate(lines):
            t = l['t']; nxt = lines[i + 1] if i + 1 < len(lines) else None
            prev_ended = ended or prev is None or bool(TERM.search(prev['t']))
            low = t.lower().rstrip(':')
            if low in subheads or low == refs_on or low in refs_off or self.is_heading(l, nxt, prev_ended):
                flush()
                if low == refs_on:
                    mode = 'refs'
                elif low in refs_off:
                    mode = 'body'
                out.append(('h4' if low in subheads else 'h3', t))
                prev = l; ended = True
                continue
            new = cur is None or ended
            if prev is not None and not new:
                if t[:1].islower() and not TERM.search(prev['t']) and mode != 'refs':
                    new = False                         # sentence carries on (page turn, hanging indent)
                elif cur[0] == 'quote' and abs(l['rel'] - cur_rel) < 0.015 and \
                        not (prev['short'] and TERM.search(prev['t'])):
                    new = False                         # still inside a block quote
                elif cur[0] == 'li' and not LIST.match(t) and l['rel'] > cur_rel + 0.01 and \
                        not (prev['short'] and TERM.search(prev['t'])):
                    new = False                         # hanging indent of a list item
                elif l['rel'] - prev['rel'] > 0.03:
                    new = True                          # first-line indent
                elif prev['rel'] - l['rel'] > 0.02 and cur_n > 1:
                    new = True                          # outdent
                elif LIST.match(t) or (prev['short'] and TERM.search(prev['t'])):
                    new = True
                elif mode == 'refs' and TERM.search(prev['t']) and ENTRY.match(t):
                    new = True
            if new and cur is not None and t[:1].islower() and prev and not TERM.search(prev['t']) \
                    and mode != 'refs' and cur[0] != 'quote':
                new = False
            if new:
                after_quote = bool(cur) and cur[0] == 'quote'
                flush()
                kind = 'ref' if mode == 'refs' else ('li' if LIST.match(t) else 'p')
                if kind == 'p' and l['rel'] > 0.03 and nxt is not None and nxt['rel'] > 0.03 and \
                        abs(nxt['rel'] - l['rel']) < 0.015 and nxt['t'][:1] not in '•·◦':
                    kind = 'quote'
                elif kind == 'p' and after_quote and t[:1].islower():
                    kind = 'cont'
                if kind == 'li':
                    t = re.sub(r'^(•|·|◦|o\s|e\s)\s*', '• ', t)
                cur = [kind, t]; cur_rel = l['rel']; cur_n = 1
            else:
                cur[1] = join(cur[1], t); cur_n += 1
            prev = l; ended = False
        flush()
        return out

    # ----- structure -----
    def parse_toc(self):
        a, b = self.cfg['toc_pages']
        end = re.compile(self.cfg.get('toc_title_end', r'\?["”]?$'))
        skip = re.compile(self.cfg.get('toc_skip', r'(([xvi]+ )?CONTENTS( [xvi]+)?)|Contents'))
        parts, chs, state = [], [], None
        for p in range(a, b + 1):
            W = self.R[p]['w']
            for ln in self.R[p]['lines']:
                t = ln['t'].strip()
                if (ln['x'] > 0.75 * W and re.fullmatch(r'[\dxvil]+', t)) or skip.fullmatch(t):
                    continue
                m = re.match(r'^(\d+)\s*\.\s*(.*)', t)
                if m:
                    chs.append(dict(n=int(m.group(1)), title=m.group(2), author='', part=parts[-1] if parts else None))
                    state = 'author' if end.search(t) else 'title'
                elif state == 'title':
                    chs[-1]['title'] += ' ' + t
                    if end.search(t):
                        state = 'author'
                elif state == 'author':
                    chs[-1]['author'] = t; state = None
                else:
                    parts.append(t)
        for n, fix in self.cfg.get('toc_fixes', {}).items():
            chs[int(n) - 1].update(fix)
        ignore = {s.lower() for s in self.cfg.get('toc_not_parts', [])}
        return [p for p in parts if p.lower() not in ignore], chs

    def large_top(self, L):
        out = []
        for i, l in enumerate(L[:7]):
            if i == 0 and CHNUM.match(l['t']):
                continue
            if l['h'] <= 0.0215:
                break
            out.append(l['t'])
        return ' '.join(out)

    def build(self, out):
        cfg = self.cfg
        parts, chs = self.parse_toc()
        first_body = cfg['body_start']
        starts, k = {}, 0
        for p in range(first_body, self.N + 1):
            if k >= len(chs):
                break
            L = self.page_lines(p)
            big = self.large_top(L) if L else ''
            title = chs[k]['title'].lower()
            if big and difflib.SequenceMatcher(None, big.lower()[:len(title) + 2], title).ratio() > 0.75:
                starts[p] = k; k += 1
        missing = [c['n'] for i, c in enumerate(chs) if i not in starts.values()]

        part_pages = [p for p in range(first_body, self.N + 1)
                      if len(self.page_lines(p)) == 1 and self.page_lines(p)[0]['t'] in parts]
        idx_head = cfg.get('index_heading')
        index_start = next((p for p in range(first_body, self.N + 1)
                            if self.page_lines(p) and self.page_lines(p)[0]['t'] == idx_head), None) if idx_head else None
        index_end = index_start
        while index_start and index_end + 1 <= self.N and self.R[index_end + 1]['lines']:
            index_end += 1
        stops = sorted(starts) + part_pages + ([index_start] if index_start else [])
        last = cfg.get('body_end', index_start - 1 if index_start else self.N)

        def chapter_blocks(k, p0, p1):
            L = self.page_lines(p0)
            i = 1 if CHNUM.match(L[0]['t']) else 0
            title = chs[k]['title'].lower(); got = ''
            while i < len(L) and len(got) < len(title) - 2:         # title lines
                got = (got + ' ' + L[i]['t'].lower()).strip(); i += 1
            if i < len(L) and difflib.SequenceMatcher(None, L[i]['t'].lower(), chs[k]['author'].lower()).ratio() > 0.5:
                i += 1                                              # author line
            lines = L[i:]
            for p in range(p0 + 1, p1):
                lines += self.page_lines(p)
            return self.blocks(lines)

        # ----- write -----
        book = epub.EpubBook()
        book.set_identifier(f"urn:isbn:{cfg['isbn']}" if cfg.get('isbn') else cfg['title'])
        book.set_title(cfg['title'])
        book.set_language(cfg.get('language', 'en'))
        book.add_author(cfg['author'], role=cfg.get('author_role', 'aut'))
        if cfg.get('publisher'):
            book.add_metadata('DC', 'publisher', cfg['publisher'])
        book.add_metadata('DC', 'description', 'Personal scan converted from OCR.' +
                          (' Index page numbers refer to the print edition.' if index_start else ''))
        doc = fitz.open(self.pdf)
        im = page_image(doc, doc[0]); im.thumbnail((1200, 1800))
        bio = io.BytesIO(); im.save(bio, 'JPEG', quality=85)
        book.set_cover('cover.jpg', bio.getvalue())
        css = epub.EpubItem(uid='css', file_name='style.css', media_type='text/css', content=CSS)
        book.add_item(css)

        def page(uid, title, body):
            c = epub.EpubHtml(uid=uid, title=title, file_name=f'{uid}.xhtml', lang=cfg.get('language', 'en'))
            c.content = f'<html><head><title>{html.escape(title)}</title></head><body>{body}</body></html>'
            c.add_item(css); book.add_item(c)
            return c

        spine = ['nav']; nav = []
        by = f"{cfg.get('author_label', '')} {cfg['author']}".strip()
        spine.append(page('title', 'Title page', f'<h1 class="center" style="margin-top:30%">{html.escape(cfg["title"])}</h1>'
                          f'<p class="center">{html.escape(by)}</p>'))
        nav.append(epub.Link('title.xhtml', 'Title page', 'title'))
        for j, fm in enumerate(cfg.get('front', [])):
            pages = range(fm['from'], fm.get('to', fm['from']) + 1)
            uid = f'front{j + 1}'
            if fm.get('kind') == 'lines':           # keep line breaks (copyright page)
                body = ''
                for p in pages:
                    for l in self.page_lines(p):
                        t = l['t']
                        for a, b in fm.get('fixes', []):
                            t = re.sub(a, b, t)
                        body += f'<p class="plain">{esc(t)}</p>'
            else:
                lines = [l for p in pages for l in self.page_lines(p)]
                if lines and lines[0]['t'].lower() == fm['title'].lower():
                    lines = lines[1:]
                body = render(self.blocks(lines))
            spine.append(page(uid, fm['title'], f'<h1>{html.escape(fm["title"])}</h1>' + body))
            if fm.get('in_toc', True):
                nav.append(epub.Link(f'{uid}.xhtml', fm['title'], uid))

        cur_part, sec, stats = None, None, []
        for p0 in sorted(starts):
            k = starts[p0]; c = chs[k]
            p1 = min([q for q in stops if q > p0] + [last + 1])
            if c['part'] and c['part'] != cur_part:
                cur_part = c['part']; uid = f'part{parts.index(cur_part) + 1:02d}'
                spine.append(page(uid, cur_part, f'<h2 class="part">{html.escape(cur_part)}</h2>'))
                sec = (epub.Section(cur_part, href=f'{uid}.xhtml'), []); nav.append(sec)
            blocks = chapter_blocks(k, p0, p1)
            stats.append((c['n'], p0, p1 - 1, len(blocks)))
            uid = f'ch{c["n"]:02d}'
            spine.append(page(uid, f'{c["n"]}. {c["title"]}',
                              f'<h1><span class="num">{c["n"]}</span>{html.escape(c["title"])}</h1>'
                              f'<p class="author">{html.escape(c["author"])}</p>' + render(blocks)))
            link = epub.Link(f'{uid}.xhtml', f'{c["n"]}. {c["title"]}', uid)
            (sec[1] if sec else nav).append(link)

        if index_start:
            idx = []
            for p in range(index_start, index_end + 1):
                L = self.page_lines(p)[1 if p == index_start else 0:]
                for l in L:
                    t = l['t']
                    if idx and (idx[-1].endswith((',', ';', '-', '(')) or
                                (t[:1].islower() and not re.search(r'[\d)]$', idx[-1]))):
                        idx[-1] = idx[-1] + t if idx[-1].endswith('-') else idx[-1] + ' ' + t
                    else:
                        idx.append(t)
            spine.append(page('index', idx_head, f'<h1>{html.escape(idx_head)}</h1>'
                              '<p class="plain"><i>Page numbers refer to the print edition.</i></p>' +
                              ''.join(f'<p class="idx">{html.escape(t)}</p>' for t in idx)))
            nav.append(epub.Link('index.xhtml', idx_head, 'index'))

        book.toc = nav; book.spine = spine
        book.add_item(epub.EpubNcx()); book.add_item(epub.EpubNav())
        epub.write_epub(out, book)
        return dict(chapters=len(starts), of=len(chs), missing=missing, recovered=self.recovered, stats=stats)


CSS = '''body{font-family:serif;line-height:1.45;margin:0 4%}
h1{font-size:1.5em;margin:2em 0 .3em;line-height:1.2} h1 .num{display:block;font-size:.7em;color:#666;margin-bottom:.3em}
h2.part{text-align:center;margin-top:35%;font-size:1.6em}
p{margin:0;text-indent:1.4em;text-align:justify} h3+p,h4+p,p.first{text-indent:0}
h3{font-family:sans-serif;font-size:1.05em;margin:1.6em 0 .5em} h4{font-family:sans-serif;font-size:.95em;font-style:italic;margin:1.2em 0 .4em}
p.author{font-style:italic;text-indent:0;margin-bottom:1.5em}
p.li{margin:.2em 0 .2em 1.5em;text-indent:-1em} p.ref{text-indent:-1.5em;margin:0 0 .4em 1.5em;font-size:.95em;text-align:left}
p.plain{text-indent:0;text-align:left;margin:.15em 0} .center{text-align:center;text-indent:0}
p.idx{text-indent:-1em;margin-left:1em;text-align:left;font-size:.9em}
blockquote{margin:.8em 1.5em;font-size:.95em} blockquote+p{text-indent:0}'''


def esc(t):
    t = html.escape(t)
    return re.sub(r'(https?://\S+?)([.,;)]?)(?=\s|$)',
                  lambda m: f'<a href="{html.unescape(m.group(1))}">{m.group(1)}</a>{m.group(2)}', t)


def render(blocks):
    out, first = [], True
    for kind, t in blocks:
        if kind in ('h3', 'h4'):
            out.append(f'<{kind}>{html.escape(t)}</{kind}>'); first = True
        elif kind == 'li':
            out.append(f'<p class="li">{esc(t)}</p>')
        elif kind == 'ref':
            out.append(f'<p class="ref">{esc(t)}</p>')
        elif kind == 'quote':
            out.append(f'<blockquote><p class="plain">{esc(t)}</p></blockquote>'); first = True
        elif kind == 'cont':
            out.append(f'<p class="first">{esc(t)}</p>'); first = False
        else:
            out.append(f'<p class="first">{esc(t)}</p>' if first else f'<p>{esc(t)}</p>'); first = False
    return '\n'.join(out)
