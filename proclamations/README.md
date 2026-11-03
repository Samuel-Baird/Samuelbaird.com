# Proclamations generator

Generates the Church's proclamations in the **layout of the official PDFs**, as vector PDFs at standard and poster sizes, in three editions: **English** and **Spanish** (the Church's own published text for each language, pulled from its website) and the **Deseret Alphabet** (a transliteration of the English). Another language or script plugs in as a new `Script`.

Unofficial: not produced or approved by The Church of Jesus Christ of Latter-day Saints. Every PDF says so in its bottom margin (`--no-credit` removes the line, for your own use).

## Quick start

```bash
cd proclamations
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt     # reportlab, pymupdf, pyyaml (Node is needed for Deseret)
cd ..
proclamations/.venv/Scripts/python -m proclamations.fetch_texts                  # re-read the English and Spanish text from the Church site
proclamations/.venv/Scripts/python -m proclamations.generate                     # 3 editions x 4 documents x 11 sizes = 132 PDFs -> proclamations/out/
proclamations/.venv/Scripts/python -m proclamations.generate --edition deseret --doc family --size 24x36
proclamations/.venv/Scripts/python -m proclamations.check                        # format parity vs the originals
proclamations/.venv/Scripts/python -m proclamations.check --outputs              # integrity of every PDF in out/
proclamations/.venv/Scripts/python -m proclamations.publish                      # copy to site/posters + previews + manifest
```

## Output layout

One flat folder per edition: `out/english/`, `out/spanish/` and `out/deseret/`, each holding `<doc>-<edition>-<size>.pdf` (for example `deseret/family-deseret-a4.pdf`). `publish` copies them to `site/posters/<edition>/`.

## What it makes

| Document | Follows the design of | Notable features reproduced |
|---|---|---|
| `family` | The Family: A Proclamation to the World (1995) | maroon rules, open-face title and subtitle, small-caps author line, small-caps lead-in on each paragraph, drop cap, italic closing note |
| `living-christ` | The Living Christ (2000) | thin page frame, brown title, small-caps subtitles, indented paragraphs, drop cap, signatory block |
| `restoration` | The Restoration of the Fulness of the Gospel (2020) | page frame, double rule around a letter-spaced subtitle, drop cap, italic closing note |
| `articles-of-faith` | The Articles of Faith poster | gold rules, ornamental divider, large verse numerals, drop cap, right-aligned signature |

Sizes: `letter` (8.5 x 11 in) and its metric equivalent `a4` (210 x 297 mm) for ordinary printing, then posters: 11x17, 18x24, 24x36, 27x40, 40x60 (inches) and A3, A2, A1, A0. All portrait. `letter` is also the originals' own size, which the format check uses.

**Each size is a re-layout, not a stretch.** The design is 612 units wide and scaled to the page width. Header and footer keep the original proportions; the extra height of a poster goes to the text block, and the largest type size that fills it is found by search. Text is justified with an optimal line-breaker and balanced across two columns. English and Spanish are hyphenated with dictionary patterns (pyphen), as the originals are; names are never split, and breaks after dashes need no extra hyphen. Deseret has no hyphenation convention, so it only breaks at spaces and dashes.

## Keeping the format faithful

`reference.py` measures the original PDFs (downloaded to a git-ignored `.cache/`, never redistributed) and stores only numbers in `reference.json`: rule and frame positions, colours and weights, column edges, type sizes, title placement. `check.py` renders the English text with the same templates at letter size and compares. Line breaks are not compared, because the originals use proprietary typefaces. Currently 49 of 49 measurements match the four originals; refresh the measurements with `python -m proclamations.reference --refresh`.

`check --outputs` verifies every generated PDF: exact page size, no text outside the page, and every word of the source present in the extracted text.

## Source text

`texts/en/*.yaml` and `texts/es/*.yaml` are read from the Church's own pages (`?lang=eng` and `?lang=spa`) by `fetch_texts.py`, with URL and date. The English was compared word for word with the official PDFs; the only differences are layout artifacts such as hyphenation and drop caps. Heading line breaks and small-caps lead-in counts are per language in `templates.py`.

## Deliberately not reproduced

- The Church's logo and wordmark, the barcode and approval numbers on the printed back pages: an unofficial edition should not look official.
- The apostles' signature facsimiles in The Living Christ. The signers' names are typeset instead.
- The proprietary typefaces (Palatino LDS, Goudy Old Style, McKay, Berkeley, Trajan). English and Spanish use Noto Serif; Deseret uses Noto Sans Deseret (plus Noto Sans for digits and punctuation), all SIL OFL; notices are in `fonts/`. The Deseret face only has the 80 Deseret letters and one weight, so bold is synthesized and italic is a slant.

## Adding a language

For a language the Church publishes, add its code to `fetch_texts.LANGS`, fetch it, add a `Script` in `scripts.py` (source language, hyphenation dictionary, credit line) and its heading breaks and lead-in counts in `templates.py`. A script conversion of existing text implements `convert()` instead, as Deseret does. Right-to-left scripts and fonts without small caps would need template work.

## Text extraction

ReportLab writes non-BMP characters (all of Deseret) into the PDF's ToUnicode table incorrectly. `fonts.py` patches this so copied and searched text is right, and writes a real space character between words so the text can be read aloud and searched.

## Tests

```bash
proclamations/.venv/Scripts/python -m pytest proclamations/tests
```

## Copyright

The proclamations are the Church's. This tool re-typesets and transliterates their text for personal, non-commercial use. Get permission before publishing results more widely; the Church's permissions portal covers uses beyond incidental personal use.
