# PDF scanning

Tools and notes for turning a book scan into a clean PDF, a smaller searchable PDF and an EPUB. They find pages to rescan (scanned twice, clipped at the spine, blurry), add the cover, and name the file after the book.

## Setup (once)

```powershell
pip install -r projects/pdf-scanning/requirements.txt
```

Everything runs locally and nothing is uploaded. There are two OCR engines:
- **RapidOCR** (ONNX, CPU) is used by `check`. It gives a confidence score for every line, which the quality flags need. It takes about 4 seconds a page.
- **Windows OCR** (built into Windows 10/11) is used by `small` and `epub`. It keeps word spacing and line positions better, and takes under a second a page. It needs an English language pack, which Windows has by default.

## Workflow

1. **Scan** the book to one PDF (for example `scan.pdf`) and the cover separately (`cover.pdf`, and `back.pdf` if you scan the back cover).
2. **Check** it:

   ```powershell
   python projects/pdf-scanning/bookscan.py check scan.pdf
   ```

   A 350-page book takes about 25 minutes. Results are cached in `scan.bookscan/ocr.jsonl`, so an interrupted run picks up where it stopped. Add `--limit 5` for a quick test. The report is in `scan.bookscan/report.md`, and thumbnails of every flagged page are in `scan.bookscan/review/`.
3. **Look at the thumbnails** before deciding anything (see "Reading the report" below), then rescan what is actually bad.
4. **Drop duplicates.** This writes `scan_deduped.pdf` and never changes `scan.pdf`:

   ```powershell
   python projects/pdf-scanning/bookscan.py drop scan.pdf 59 60 101 102
   ```

   Page numbers are PDF page numbers (1-based) in the original file.
5. **Add the covers and name the file:**

   ```powershell
   python projects/pdf-scanning/bookscan.py assemble scan_deduped.pdf --front cover.pdf --back back.pdf --title "Book Title" --author "Author"
   ```

   This writes `Book Title.pdf` next to the input and sets the PDF title and author.
6. **Smaller, searchable copy** (optional). This writes `Book Title (small).pdf`:

   ```powershell
   python projects/pdf-scanning/bookscan.py small "Book Title.pdf"
   ```

   Pages are resampled to 150 dpi. The inside pages become grayscale with the paper cleaned to white, and the cover stays in color. An invisible Windows OCR text layer makes the PDF searchable. The first book went from 151 MB to 38 MB in about a minute. Options: `--dpi`, `--quality` (JPEG, default 55), `--color-pages 1 351`, `--no-text`.
7. **EPUB** (optional). This needs a short config file for the book (see "EPUB" below) and writes `Book Title.epub`:

   ```powershell
   python projects/pdf-scanning/bookscan.py epub "Book Title.pdf" --config projects/pdf-scanning/books/<book>.json
   ```

`drop` and `assemble` both check that every page image in the output is byte-identical to its source and in the right order (`Page images match ...: True`). Neither ever overwrites an existing file. They also carry the OCR caches over to the output's `.bookscan` folder with the pages renumbered, so `small`, `epub` and `check` never OCR the same book twice.

## Reading the report

- **Page order** is the most reliable check. It reads the printed page number from each page's running header ("84 MORMONISM IN FIVE MINUTES" or "AUTHOR-CHAPTER TITLE? 65") and tracks the gap between PDF page and printed page:
  - `N extra scan(s) between`: a run of pages was scanned twice. The **Rescanned pages** section finds the two copies and suggests which to drop.
  - `N printed page(s) missing between`: pages were skipped, so rescan them.
  - It only covers pages that have a running header. Front matter (roman numerals), chapter-opening pages and back matter aren't checked, so look through those by eye. If a book's headers aren't recognised, pass `--header-regex` with one group around the number, for example `--header-regex "^(\d+)\s"`.
- **Rescanned pages**: the suggestion keeps the copy with the higher OCR confidence. OCR can't see a finger, clip or sticky tab in the margin, so compare both copies in `review/` first. On the first book, the copy with the slightly better OCR had a yellow object in the margin and was the one to drop.
- **Text cut off at the page edge** lists pages where at least 3 lines of text run into the image edge, meaning the crop went through the text next to the spine. Left-hand pages lose the ends of lines and right-hand pages lose the starts. A sliver missing is still readable, but the OCR (and so the EPUB) loses letters there. For a clean copy, rescan those pages with a looser crop. Pages with only 3–6 lines touching are often fine, so check the thumbnails.
- **Pages with matching text** includes pairs that aren't duplicates, such as the same author bio printed twice or cross-reference lists. Only the pairs that line up with an extra-scan break are real rescans.
- **Pages to look at**:
  - *Soft image* is a sharpness score (variance of the Laplacian) well below the book's median. Short end-of-chapter pages and reading lists score low only because they're mostly blank paper with the next page showing through, so check the thumbnail. On the first book every flagged "soft" page was fine.
  - *Low OCR confidence* (below 0.93 average, or over 15% of lines unsure) is a better sign of real blur, skew or glare. A typical clean page scores about 0.98.
  - *Dark* pages usually mean the page lifted or a shadow fell across it.
- **Blank or near-blank pages** are usually part dividers and blank versos. Only worry about one where you expected text.

## EPUB

`epub` rebuilds a reflowable book from the Windows OCR line positions:
- chapters, matched against the printed contents
- parts, headings and paragraphs (first-line indents, sentences that run across a page turn)
- numbered and bulleted lists, block quotes and reading lists
- the index, with a note that its page numbers refer to the print edition
- the front-matter pages you name in the config

It also repairs common OCR damage:
- known misreads, like "Tie" for "The"
- the "Th" ligature read as "rlh" or "ff"
- dropped "fi"/"ffi" ligatures ("affrm" becomes "affirm")
- "kl" read as "ld"
- words run together ("ofa")
- words clipped at the spine, completed only when one dictionary word clearly wins
- "Th…" words that Windows OCR drops at the start of a line, recovered from the RapidOCR cache if `check` was run

Everything specific to one book goes in `books/<book>.json`. Copy `books/mormonism-in-five-minutes.json` and change:
- **Metadata:** `title`, `author`, `author_role` (`aut`, or `edt` for an editor), `author_label` ("Edited by"), `publisher`, `isbn`.
- **Structure:** all of these are PDF page numbers in the finished PDF (cover = page 1).
  - `toc_pages`: first and last contents page.
  - `front`: front-matter pages to keep. `kind: "lines"` keeps line breaks, which suits a copyright page.
  - `body_start`: first page after the front matter.
  - `index_heading`: the index's title, if the book has one.
- **Sections inside chapters:** `subheads` (small headings), `refs_heading` (where a reading list starts, laid out as references) and `refs_end_headings`.
- **Fixes:**
  - `toc_fixes`: correct OCR slips in chapter titles or authors (check them against the running headers).
  - `text_fixes`: regex replacements applied to the whole text.
  - `header_regex`: extra running headers to strip.

**Limits:** it was built on an edited volume. Its contents list "N. Title?" lines, each followed by the author, and its chapters open with the title in large type. A book laid out differently (titles not ending in "?", no numbers, no authors) will need `toc_title_end`/`toc_skip` set, or changes to `parse_toc` and the chapter matching in `epubbuild.py`. The command prints how many chapters it found ("77 of 77") and which ones it missed. Footnotes, tables and images aren't handled. Tables come out as run-on text, and pictures are dropped.

To check an EPUB: Calibre's `ebook-convert book.epub check.txt` should run without errors. Then skim a few chapters in a reader.

## Notes from the first book (Nov 2026)

- The book was a 358-page paperback, scanned with BookChanger, one JPEG per page at about 340 dpi, each cropped to a slightly different size. The check found 4 spreads scanned twice (8 extra pages) and no missing pages.
- **The first version of `check` missed spine clipping.** About 50 pages had the crop running through the text at the spine. Most were left-hand pages (book pages 8–150), plus a few right-hand ones. It's barely visible on screen, but it cost letters in the OCR. The "Text cut off at the page edge" section was added because of this.
- On one page the scanning app left a vertical seam about 250 px in from the edge, and the letters crossing it were erased ("hase 2" for "Phase 2"). Neither an edge test nor a column-brightness test picked it out from normal gutter shading, so the report can't find these. They show up as odd words in the EPUB.
- Image hashes (pHash/dHash) were useless for finding duplicates, because every text page looks alike at hash resolution. Comparing OCR text (4-word phrases) and the printed page numbers worked.
- Duplicates came as whole spreads (2 pages) repeated right after the original, which is what happens when the scanner re-shoots a spread. The tool looks for that pattern.
- RapidOCR sometimes drops the spaces between words ("toreceiverevelation"), so it's fine for checking but poor for reading text. That's why the EPUB uses Windows OCR. Windows OCR drops the "fi" ligature and sometimes the whole "Th…" word at a line start, and the EPUB repairs cover both. After repair, 99.9% of the EPUB's words were dictionary words.
- PDFs over 100 MB can't be read directly by Claude's PDF reader. The tools work with any size because they pull the page images out with PyMuPDF.

## Ideas for later

- Detect app seams: a sharp brightness step down the page that cuts through letters.
- Flag skew from the angles of the OCR text boxes.
- Footnotes and tables in the EPUB.
