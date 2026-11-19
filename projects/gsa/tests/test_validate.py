import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate as v
import pdf_fixtures as fx

# The industry-standard EICAR test string, assembled at runtime so this source
# file itself never matches a scanner signature.
EICAR = ('X5O!P%@AP[4\\PZX54(P^)7CC)7}$' + 'EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*').encode()
CLAM_DB = Path(os.environ.get('GSA_CLAMAV_DB', Path.home() / 'Library/Application Support/GSA Worker/clamav/db'))
HAVE_CLAM = shutil.which('clamscan') and any(CLAM_DB.glob('*.c[lv]d'))
HAVE_PDF_TOOLS = all(shutil.which(t) for t in ('pdfinfo', 'pdffonts', 'pdfimages', 'qpdf'))
CLAM_CONFIG = {'scanner_command': ['clamscan', '--no-summary', f'--database={CLAM_DB}'], 'max_file_bytes': 10 ** 8}


def fake_scanner(directory, code, action=''):
    script = Path(directory) / f'scanner{code}.sh'
    script.write_text(f'#!/bin/sh\n{action}\necho "fake scanner"\nexit {code}\n')
    script.chmod(0o700)
    return {'scanner_command': [str(script)], 'max_file_bytes': 10 ** 8}


def no_tools(cmd, **kw):
    raise FileNotFoundError(cmd[0])


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, data):
        path = self.dir / name
        path.write_bytes(data)
        return path


class SignatureTests(Base):
    def test_signatures(self):
        self.assertEqual(v.check_signature(self.write('a.pdf', b'%PDF-1.7\n'))['status'], 'pass')
        self.assertEqual(v.check_signature(self.write('a.mp3', b'ID3\x04'))['status'], 'pass')
        self.assertEqual(v.check_signature(self.write('a.mp4', b'\0\0\0\x18ftypmp42'))['status'], 'pass')
        self.assertEqual(v.check_signature(self.write('b.pdf', b'MZ\x90\0'))['detail'], 'content looks like windows_executable, not .pdf')
        self.assertEqual(v.check_signature(self.write('c.pdf', b'PK\x03\x04'))['status'], 'fail')
        self.assertEqual(v.check_signature(self.write('d.pdf', b'hello'))['status'], 'fail')
        self.assertEqual(v.check_signature(self.write('e.epub', b'PK\x03\x04'))['status'], 'fail')

    def test_size_limit(self):
        self.assertEqual(v.check_size(self.write('a.pdf', b'x' * 11), {'max_file_bytes': 10})['status'], 'fail')
        self.assertEqual(v.check_size(self.write('b.pdf', b''), {})['status'], 'fail')

    def test_signature_failure_stops_before_tools(self):
        report = v.validate(self.write('x.pdf', b'MZ'), {'scanner_command': ['unused']}, run=no_tools)
        self.assertEqual(report['automated_verdict'], 'fail')
        self.assertNotIn('malware_scan', report['automated_checks'])
        self.assertIn('malware_scan (not run)', report['automated_failures'])


class ScannerTests(Base):
    def test_exit_codes(self):
        path = self.write('a.pdf', b'%PDF-1.4')
        self.assertEqual(v.scan_malware(path, fake_scanner(self.dir, 0))['status'], 'pass')
        self.assertEqual(v.scan_malware(path, fake_scanner(self.dir, 1))['status'], 'fail')
        self.assertEqual(v.scan_malware(path, fake_scanner(self.dir, 2))['status'], 'error')
        self.assertEqual(v.scan_malware(path, {'scanner_command': ['/nonexistent/scanner']})['status'], 'error')
        self.assertEqual(v.scan_malware(path, {})['status'], 'error')

    def test_scanner_error_or_tool_missing_fails_report(self):
        path = self.write('a.pdf', b'%PDF-1.4')
        report = v.validate(path, fake_scanner(self.dir, 2), run=no_tools)
        self.assertEqual(report['automated_verdict'], 'fail')
        self.assertIn('malware_scan', report['automated_failures'])

    def test_file_changed_during_validation_fails(self):
        path = self.write('a.pdf', b'%PDF-1.4')
        report = v.validate(path, fake_scanner(self.dir, 0, f'printf more >> "{path}"'))
        self.assertEqual(report['automated_checks']['unchanged_during_validation']['status'], 'fail')
        self.assertEqual(report['automated_verdict'], 'fail')

    def test_db_age(self):
        config = {'scanner_command': ['clamscan', '--database=/x'], 'scanner_max_db_age_hours': 48}
        stamp = datetime(2026, 11, 18, 23, 24, 39)
        out = f'ClamAV 1.5.5/28188/{stamp.strftime("%a %b %d %H:%M:%S %Y")}\n'
        fake = lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, out, '')
        now = stamp.astimezone()
        self.assertEqual(v.clamav_db_age(config, fake, now + timedelta(hours=10))['status'], 'pass')
        self.assertEqual(v.clamav_db_age(config, fake, now + timedelta(hours=60))['status'], 'fail')
        self.assertEqual(v.clamav_db_age({'scanner_command': ['other']}, fake)['status'], 'skip')

    @unittest.skipUnless(HAVE_CLAM, 'clamscan with a signature database not available')
    def test_real_clamav_detects_eicar_and_passes_clean_pdf(self):
        infected = self.write('eicar.pdf', EICAR)
        result = v.scan_malware(infected, CLAM_CONFIG)
        self.assertEqual(result['status'], 'fail')
        self.assertIn('Eicar', result['detail'])
        self.assertEqual(v.scan_malware(self.write('clean.pdf', fx.text_pdf()), CLAM_CONFIG)['status'], 'pass')
        fresh = v.clamav_db_age(dict(CLAM_CONFIG, scanner_max_db_age_hours=24 * 365))
        self.assertEqual(fresh['status'], 'pass', fresh['detail'])


PDFINFO = """Title:           Synthetic
Producer:        calibre 7.1.0
Encrypted:       no
Pages:           2
PDF version:     1.4
Page    1 size: 396 x 612 pts
Page    2 size: 396 x 612 pts
"""
PDFFONTS = """name                                 type              encoding         emb sub uni object ID
------------------------------------ ----------------- ---------------- --- --- --- ---------
ABCDEF+Times New Roman               TrueType          WinAnsi          yes yes no       5  0
GlyphLessFont                        Type 1            Standard         no  no  no       3  0
"""
PDFIMAGES = """page   num  type   width height color comp bpc  enc interp  object ID x-ppi y-ppi size ratio
--------------------------------------------------------------------------------------------
   1     0 image    1700  2200  gray    1   8  jpeg   no         6  0   200   200  50K 1.3%
   2     1 image    1700  2200  gray    1   8  jpeg   no         9  0   200   200  50K 1.3%
   2     2 smask     100   100  gray    1   8  image  no        10  0    10    10  1K  1.0%
"""


def info(pages=3, size=(612, 792), **meta):
    return dict({'Pages': str(pages), '_page_sizes': [size] * pages}, **meta)


def page_images(pages, ppi=300, size=(612, 792)):
    return [{'page': p, 'type': 'image', 'width': int(size[0] / 72 * ppi), 'height': int(size[1] / 72 * ppi),
             'color': 'gray', 'x_ppi': ppi, 'y_ppi': ppi} for p in range(1, pages + 1)]


TEXT_FONT = [{'name': 'ABCDEF+Garamond', 'type': 'Type 1C', 'embedded': True}]


class ParserAndClassifierTests(unittest.TestCase):
    def test_parsers(self):
        parsed = v.parse_pdfinfo(PDFINFO)
        self.assertEqual(parsed['Pages'], '2')
        self.assertEqual(parsed['_page_sizes'], [(396.0, 612.0)] * 2)
        fonts = v.parse_pdffonts(PDFFONTS)
        self.assertEqual([f['name'] for f in fonts], ['ABCDEF+Times New Roman', 'GlyphLessFont'])
        self.assertTrue(fonts[0]['embedded'])
        images = v.parse_pdfimages(PDFIMAGES)
        self.assertEqual(len(images), 3)
        self.assertEqual(images[2]['type'], 'smask')

    def test_scan_by_layout_without_metadata(self):
        result = v.classify_pdf(info(10), [], page_images(10))
        self.assertEqual(result['class'], 'scan')
        self.assertEqual(result['scan_page_ratio'], 1.0)

    def test_scan_with_ocr_text_layer_still_scan(self):
        result = v.classify_pdf(info(4), TEXT_FONT, page_images(4))
        self.assertEqual(result['class'], 'scan')

    def test_born_digital(self):
        result = v.classify_pdf(info(5, Producer='Adobe InDesign 18'), TEXT_FONT, [])
        self.assertEqual(result['class'], 'born_digital')
        self.assertEqual(result['flags'], [])

    def test_ebook_converters_by_metadata(self):
        for producer in ('calibre 7.1.0', 'ebook-convert', 'Adobe Digital Editions 4.5', 'KindleGen 2.9'):
            with self.subTest(producer=producer):
                result = v.classify_pdf(info(5, Producer=producer), TEXT_FONT, [])
                self.assertEqual(result['class'], 'likely_ebook_conversion')
                self.assertIn('LIKELY EBOOK CONVERSION', result['flags'][0])

    def test_ebook_by_two_weak_signals_only(self):
        small = info(20, size=(360, 576))
        one = v.classify_pdf(small, TEXT_FONT, [])
        self.assertEqual(one['class'], 'born_digital')
        self.assertTrue(one['flags'][0].startswith('Possible ebook conversion'))
        two = v.classify_pdf(small, TEXT_FONT, [], filename='Title (epub).pdf')
        self.assertEqual(two['class'], 'likely_ebook_conversion')

    def test_mixed_unknown_and_low_res(self):
        self.assertEqual(v.classify_pdf(info(10), TEXT_FONT, page_images(3))['class'], 'mixed')
        self.assertEqual(v.classify_pdf(info(3), [], [])['class'], 'unknown')
        low = v.classify_pdf(info(3), [], page_images(3, ppi=100))
        self.assertTrue(any('LOW-RESOLUTION' in f for f in low['flags']))

    def test_ranking_prefers_scans_and_true_pdfs(self):
        scan = v.ranking_score(v.classify_pdf(info(3), TEXT_FONT, page_images(3)))
        born = v.ranking_score(v.classify_pdf(info(3), TEXT_FONT, []))
        ebook = v.ranking_score(v.classify_pdf(info(3, Producer='calibre'), TEXT_FONT, []))
        self.assertGreater(min(scan, born), ebook + 40)
        damaged = v.ranking_score(v.classify_pdf(info(3), TEXT_FONT, []), qpdf_status='fail')
        self.assertLess(damaged, born)

    def test_rank_orders_failures_last(self):
        reports = [{'automated_verdict': 'pass', 'ranking_score': 15, 'file': 'ebook'},
                   {'automated_verdict': 'fail', 'ranking_score': 90, 'file': 'broken'},
                   {'automated_verdict': 'pass', 'ranking_score': 85, 'file': 'scan'}]
        self.assertEqual([r['file'] for r in v.rank(reports)], ['scan', 'ebook', 'broken'])


@unittest.skipUnless(HAVE_PDF_TOOLS, 'poppler and qpdf not installed')
class GeneratedPdfTests(Base):
    def report(self, name, data):
        return v.validate(self.write(name, data), fake_scanner(self.dir, 0))

    def test_text_scan_and_calibre_fixtures(self):
        text = self.report('Lastname, Title.pdf', fx.text_pdf())
        scan = self.report('scan.pdf', fx.scan_pdf(pages=2))
        noproducer = self.report('scan2.pdf', fx.scan_pdf(pages=2, producer=''))
        ebook = self.report('converted.pdf', fx.calibre_pdf())
        for r in (text, scan, noproducer, ebook):
            self.assertEqual(r['automated_verdict'], 'pass', r['automated_checks'])
            self.assertEqual(r['automated_checks']['qpdf_check']['status'], 'pass')
        self.assertEqual(text['pdf']['classification']['class'], 'born_digital')
        self.assertEqual(scan['pdf']['classification']['class'], 'scan')
        self.assertEqual(noproducer['pdf']['classification']['class'], 'scan')
        self.assertEqual(ebook['pdf']['classification']['class'], 'likely_ebook_conversion')
        self.assertEqual(v.rank([ebook, text])[0]['file'], 'Lastname, Title.pdf')

    def test_report_separates_automated_and_staff_judgment(self):
        report = self.report('converted.pdf', fx.calibre_pdf())
        staff = {s['item'] for s in report['staff_judgment']}
        self.assertTrue({'bibliographic_match', 'first_and_last_pages', 'body_spot_check', 'completeness', 'rights'} <= staff)
        self.assertTrue(all(s['status'] == 'pending' for s in report['staff_judgment']))
        self.assertFalse(staff & set(report['automated_checks']))
        text = v.render(report)
        self.assertLess(text.index('AUTOMATED CHECKS'), text.index('STAFF JUDGMENT REQUIRED'))
        self.assertIn('LIKELY EBOOK CONVERSION', text)

    def test_corrupt_pdf_fails(self):
        data = fx.text_pdf()
        report = self.report('broken.pdf', data[:len(data) // 2])
        self.assertEqual(report['automated_verdict'], 'fail')
        self.assertIn('pdfinfo', report['automated_failures'])

    def test_encryption(self):
        src = self.write('plain.pdf', fx.text_pdf())
        restricted, locked = self.dir / 'restricted.pdf', self.dir / 'locked.pdf'
        subprocess.run(['qpdf', '--encrypt', '', 'owner', '256', '--', str(src), str(restricted)], check=True)
        subprocess.run(['qpdf', '--encrypt', 'user', 'owner', '256', '--', str(src), str(locked)], check=True)
        report = v.validate(restricted, fake_scanner(self.dir, 0))
        self.assertEqual(report['automated_checks']['not_encrypted']['status'], 'warn')
        self.assertTrue(any('not_encrypted' in f for f in report['reviewer_flags']))
        # A user password blocks every PDF check, so the automated verdict fails.
        self.assertEqual(v.validate(locked, fake_scanner(self.dir, 0))['automated_verdict'], 'fail')


if __name__ == '__main__':
    unittest.main()
