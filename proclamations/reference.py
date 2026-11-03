"""Measure the layout of the Church's own proclamation PDFs.

    python -m proclamations.reference            # use reference.json
    python -m proclamations.reference --refresh  # download the originals (to .cache/) and re-measure

reference.json holds only numbers (rule positions, column edges, type sizes). The originals are
downloaded to a git-ignored cache for measuring and are never redistributed.
"""
import collections
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
REFERENCE = HERE / "reference.json"

ORIGINALS = {
    "family": "https://www.churchofjesuschrist.org/bc/content/shared/content/english/pdf/36035_000_24_family.pdf",
    "living-christ": "https://www.churchofjesuschrist.org/bc/content/shared/content/english/pdf/36035_000_25_livingchrist.pdf",
    "restoration": "https://newsroom.churchofjesuschrist.org/multimedia/file/restoration-proclamation-2020-april.pdf",
    "articles-of-faith": "https://www.churchofjesuschrist.org/bc/content/shared/content/english/pdf/language-materials/64370_eng.pdf",
}


def _sides(item):
    """Yield ((x0, y0), (x1, y1)) edges for a line or rectangle drawing item."""
    if item[0] == "l":
        yield (item[1].x, item[1].y), (item[2].x, item[2].y)
    elif item[0] == "re":
        r = item[1]
        yield (r.x0, r.y0), (r.x1, r.y0)
        yield (r.x0, r.y1), (r.x1, r.y1)
        yield (r.x0, r.y0), (r.x0, r.y1)
        yield (r.x1, r.y0), (r.x1, r.y1)


def _segments(page):
    """Horizontal/vertical stroked lines at least 40pt long that lie on the page."""
    W, H = page.rect.width, page.rect.height
    out = {}
    for dr in page.get_drawings():
        color = dr.get("color")
        if color is None:
            continue                      # fill-only shapes (white masks) are not rules
        width = dr.get("width") or 0.0
        for item in dr["items"]:
            for (x0, y0), (x1, y1) in _sides(item):
                if abs(y0 - y1) < 0.2 and abs(x0 - x1) >= 40:
                    seg = ("h", y0, min(x0, x1), max(x0, x1), H)
                elif abs(x0 - x1) < 0.2 and abs(y0 - y1) >= 40:
                    seg = ("v", x0, min(y0, y1), max(y0, y1), W)
                else:
                    continue
                if not (-0.5 <= seg[1] <= seg[4] + 0.5):
                    continue              # crop/bleed marks outside the page
                key = (seg[0], round(seg[1], 1), round(seg[2], 1), round(seg[3], 1))
                out[key] = {"o": seg[0], "pos": key[1], "a": key[2], "b": key[3],
                            "w": round(width, 2), "c": [round(x, 2) for x in color]}
    return sorted(out.values(), key=lambda s: (s["o"], s["pos"], s["a"]))


def measure(path):
    import pymupdf
    page = pymupdf.open(path)[0]
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for s in ln["spans"]:
                if s["text"].strip():
                    spans.append(s)
    body_size = collections.Counter(round(s["size"], 1) for s in spans).most_common(1)[0][0]
    body = [s for s in spans if abs(s["size"] - body_size) < 0.35]
    lefts = collections.Counter(round(s["bbox"][0]) for s in body if s["bbox"][0] < page.rect.width / 2 - 5)
    rights = collections.Counter(round(s["bbox"][0]) for s in body if s["bbox"][0] > page.rect.width / 2 + 5)
    # title = large type that ends above the body text (drop caps start inside the body, so they are excluded).
    # Extents come from visible characters only: printed spans often carry trailing space glyphs.
    body_top = min(b["bbox"][1] for b in body)
    xs0, xs1, ys0 = [], [], []
    for blk in page.get_text("rawdict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                if sp["size"] < 20 or sp["bbox"][3] > body_top + 1:
                    continue
                for ch in sp["chars"]:
                    if ch["c"].strip():
                        xs0.append(ch["bbox"][0])
                        xs1.append(ch["bbox"][2])
                        ys0.append(ch["bbox"][1])
    tb = [min(xs0), min(ys0), max(xs1)] if xs0 else None
    return {
        "page": [round(page.rect.width, 1), round(page.rect.height, 1)],
        "rules": _segments(page),
        "body_size": body_size,
        "col1_left": lefts.most_common(1)[0][0] if lefts else None,
        "col2_left": rights.most_common(1)[0][0] if rights else None,
        "body_top": round(min(s["bbox"][1] for s in body), 1),
        "title_center_x": round((tb[0] + tb[2]) / 2, 1) if tb else None,
        "title_top": round(tb[1], 1) if tb else None,
    }


def download(slug):
    CACHE.mkdir(exist_ok=True)
    dest = CACHE / f"{slug}.pdf"
    if not dest.exists():
        req = urllib.request.Request(ORIGINALS[slug], headers={"User-Agent": "Mozilla/5.0"})
        dest.write_bytes(urllib.request.urlopen(req, timeout=90).read())
    return dest


def refresh():
    data = {slug: measure(download(slug)) for slug in ORIGINALS}
    REFERENCE.write_text(json.dumps(data, indent=1), encoding="utf-8", newline="\n")
    return data


def load():
    return json.loads(REFERENCE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    d = refresh() if "--refresh" in sys.argv else load()
    for slug, m in d.items():
        print(f"{slug}: page {m['page']}, body {m['body_size']}pt, cols at x={m['col1_left']}/{m['col2_left']}, "
              f"{len(m['rules'])} rules, title top {m['title_top']}")
