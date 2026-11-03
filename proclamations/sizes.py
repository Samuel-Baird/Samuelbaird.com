"""Page sizes, in PDF points (1 in = 72 pt). All portrait: standard print sizes first, then posters."""
MM = 72 / 25.4

SIZES = {
    "letter": (8.5 * 72, 11 * 72),          # standard US size; also the originals' own size
    "a4": (210 * MM, 297 * MM),             # its metric equivalent
    "11x17": (11 * 72, 17 * 72),
    "18x24": (18 * 72, 24 * 72),
    "24x36": (24 * 72, 36 * 72),
    "27x40": (27 * 72, 40 * 72),
    "40x60": (40 * 72, 60 * 72),
    "a3": (297 * MM, 420 * MM),
    "a2": (420 * MM, 594 * MM),
    "a1": (594 * MM, 841 * MM),
    "a0": (841 * MM, 1189 * MM),
}
POSTERS = [n for n in SIZES if n not in ("letter", "a4")]

LABELS = {
    "a4": "A4 (210 x 297 mm)",
    "11x17": '11" x 17" (small / bulletin)', "18x24": '18" x 24" (medium)', "24x36": '24" x 36" (large)',
    "27x40": '27" x 40" (movie one-sheet)', "40x60": '40" x 60" (extra large)',
    "a3": "A3 (297 x 420 mm)", "a2": "A2 (420 x 594 mm)", "a1": "A1 (594 x 841 mm)", "a0": "A0 (841 x 1189 mm)",
    "letter": 'Letter (8.5" x 11")',
}


def get(name):
    n = name.lower()
    if n in SIZES:
        return SIZES[n]
    raise KeyError(f"unknown size '{name}'; choose from {', '.join(SIZES)}")
