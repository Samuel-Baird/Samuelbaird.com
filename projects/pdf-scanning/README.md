# PDF scanning

Tools and notes for turning a book scan into a clean PDF: find pages to rescan, find pages scanned twice, add the cover, name the file after the book.

## Setup (once)

```powershell
pip install -r projects/pdf-scanning/requirements.txt
```

OCR runs locally with RapidOCR (ONNX, CPU). Nothing is uploaded anywhere.

## Workflow

1. **Scan** the book to one PDF (for example `scan.pdf`) and the cover separately (`cover.pdf`, and `back.pdf` if you scan the back cover).
2. **Check** it:

   ```powershell
   python projects/pdf-scanning/bookscan.py check scan.pdf
   ```

   OCR takes about 4 seconds a page, so a 350-page book takes about 25 minutes. Results are cached in `scan.bookscan/ocr.jsonl`, so an interrupted run picks up where it stopped. Add `--limit 5` for a quick test. The report is in `scan.bookscan/report.md`, and thumbnails of every flagged page are in `scan.bookscan/review/`.
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

`drop` and `assemble` both check that every page image in the output is byte-identical to its source and in the right order (`Page images match ...: True`). Neither ever overwrites an existing file.

## Reading the report

- **Page order** is the most reliable check. It reads the printed page number from each page's running header ("84 MORMONISM IN FIVE MINUTES" or "AUTHOR-CHAPTER TITLE? 65") and tracks the gap between PDF page and printed page:
  - `N extra scan(s) between`: a run of pages was scanned twice. The **Rescanned pages** section finds the two copies and suggests which to drop.
  - `N printed page(s) missing between`: pages were skipped, so rescan them.
  - It only covers pages that have a running header. Front matter (roman numerals), chapter-opening pages and back matter aren't checked, so look through those by eye. If a book's headers aren't recognised, pass `--header-regex` with one group around the number, for example `--header-regex "^(\d+)\s"`.
- **Rescanned pages**: the suggestion keeps the copy with the higher OCR confidence. OCR can't see a finger, clip or sticky tab in the margin, so compare both copies in `review/` first. On the first book, the copy with the slightly better OCR had a yellow object in the margin and was the one to drop.
- **Pages with matching text** includes pairs that aren't duplicates, such as the same author bio printed twice or cross-reference lists. Only the pairs that line up with an extra-scan break are real rescans.
- **Pages to look at**:
  - *Soft image* is a sharpness score (variance of the Laplacian) well below the book's median. Short end-of-chapter pages and reading lists score low only because they're mostly blank paper with the next page showing through, so check the thumbnail. On the first book every flagged "soft" page was fine.
  - *Low OCR confidence* (below 0.93 average, or over 15% of lines unsure) is a better sign of real blur, skew or glare. A typical clean page scores about 0.98.
  - *Dark* pages usually mean the page lifted or a shadow fell across it.
- **Blank or near-blank pages** are usually part dividers and blank versos. Only worry about one where you expected text.

## Notes from the first book (Nov 2026)

- The book was a 358-page paperback, scanned with BookChanger, one JPEG per page, each cropped to a slightly different size. The check found 4 spreads scanned twice (8 extra pages) and no missing pages. No page needed a rescan.
- Image hashes (pHash/dHash) were useless for finding duplicates, because every text page looks alike at hash resolution. Comparing OCR text (4-word phrases) and the printed page numbers worked, which is why the tool doesn't use image hashes.
- Duplicates came as whole spreads (2 pages) repeated right after the original, which is what happens when the scanner re-shoots a spread. The tool looks for that pattern.
- PDFs over 100 MB can't be read directly by Claude's PDF reader. The tool works with any size because it pulls the page images out with PyMuPDF.

## Ideas for later

- Add a searchable text layer to the finished PDF (`ocrmypdf`, or write the RapidOCR text in as invisible text).
- Flag skew from the angles of the OCR text boxes.
