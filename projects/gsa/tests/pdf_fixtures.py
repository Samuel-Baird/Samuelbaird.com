"""Generate small synthetic PDFs for validation tests (no real books)."""
import zlib


def _pdf(objects, info):
    """objects: list of bytes bodies for objects 1..n (1 = catalog, 2 = pages)."""
    info_num = len(objects) + 1
    objects = objects + [b'<< ' + b' '.join(b'/%s (%s)' % (k.encode(), v.encode()) for k, v in info.items()) + b' >>']
    out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offsets = []
    for n, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b'%d 0 obj\n' % n + body + b'\nendobj\n'
    xref = len(out)
    out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objects) + 1)
    out += b''.join(b'%010d 00000 n \n' % o for o in offsets)
    out += b'trailer\n<< /Size %d /Root 1 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objects) + 1, info_num, xref)
    return bytes(out)


def _stream(data, extra=b''):
    return b'<< /Length %d %s >>\nstream\n' % (len(data), extra) + data + b'\nendstream'


def text_pdf(pages=3, size=(612, 792), producer='LaTeX with hyperref', creator='pdfTeX-1.40', title='Synthetic text'):
    """Born-digital style: text drawn with a standard font, no images."""
    n = pages
    # 1 catalog, 2 pages, 3 font, then per page: page obj, content obj
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>', None, b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    kids = []
    for i in range(n):
        page_num = 4 + 2 * i
        kids.append(b'%d 0 R' % page_num)
        content = b'BT /F1 12 Tf 72 700 Td (Synthetic test page %d) Tj ET' % (i + 1)
        objs.append(b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] /Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>'
                    % (size[0], size[1], page_num + 1))
        objs.append(_stream(content))
    objs[1] = b'<< /Type /Pages /Kids [' + b' '.join(kids) + b'] /Count %d >>' % n
    return _pdf(objs, {'Title': title, 'Producer': producer, 'Creator': creator})


def scan_pdf(pages=3, ppi=200, size=(612, 792), producer='ScanSnap Manager', with_ocr_layer=False):
    """Page-image 'scan': one full-page grayscale image per page."""
    w, h = int(size[0] / 72 * ppi), int(size[1] / 72 * ppi)
    pixels = zlib.compress(bytes(x * 7 % 256 for x in range(w)) * h, 9)
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>', None,
            b'<< /Type /Font /Subtype /Type1 /BaseFont /GlyphLessFont >>']
    kids = []
    for i in range(pages):
        base = 4 + 3 * i
        kids.append(b'%d 0 R' % base)
        # The image is drawn over the full page, so effective ppi = w / (page width in inches).
        content = b'q %d 0 0 %d 0 0 cm /Im0 Do Q' % size
        if with_ocr_layer:
            content += b' BT 3 Tr /F1 12 Tf 72 700 Td (ocr text) Tj ET'
        res = b'<< /XObject << /Im0 %d 0 R >>%s >>' % (base + 2, b' /Font << /F1 3 0 R >>' if with_ocr_layer else b'')
        objs.append(b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] /Resources %s /Contents %d 0 R >>'
                    % (size[0], size[1], res, base + 1))
        objs.append(_stream(content))
        objs.append(_stream(pixels, b'/Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode' % (w, h)))
    objs[1] = b'<< /Type /Pages /Kids [' + b' '.join(kids) + b'] /Count %d >>' % pages
    return _pdf(objs, {'Title': 'Synthetic scan', 'Producer': producer, 'Creator': producer})


def calibre_pdf(pages=4):
    """Text PDF carrying calibre-style producer metadata and small uniform pages."""
    return text_pdf(pages, size=(396, 612), producer='calibre 7.1.0 [https://calibre-ebook.com]',
                    creator='calibre 7.1.0', title='Synthetic.epub')
