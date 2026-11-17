# knowledge — how people learn, and how to look it up

Reference material that the course builders (`content.py`, `problems/*.py`) draw on so study sites are designed around how learning works, not just what the syllabus covers.

## What is committed
```
knowledge/
  learning/
    playbook.md        principles -> concrete rules for building study guides (start here)
    glossary.md        cross-book learning-science terms, in our own words
    books.json         registry of the source textbooks (title, edition, page offset)
    books/<slug>.md    chapter-by-chapter digest of one book: own-words bullets, key terms, page refs
    books/<slug>.toc.json  chapter -> printed/pdf start page (refs only)
```
Everything committed is original writing plus page references. **No book text, ever** (see CLAUDE.md copyright rule). `scripts/kb_check.py` scans these files for verbatim runs of book text and must pass before a commit.

## What stays local (gitignored)
```
knowledge/sources/<slug>.pdf          the textbook PDFs
knowledge/cache/<slug>.pages.jsonl    per-page extracted text
knowledge/cache/kb.sqlite             full-text search index over every cached book
```
Rebuild on a fresh clone by dropping the PDFs into `knowledge/sources/` (names in `books.json`) and running:

```bash
for s in chance olson-ramirez mazur-odum gluck domjan-delamater dehouwer-hughes; do python -I scripts/kb_extract.py knowledge/sources/$s.pdf $s; done
python -I scripts/kb_toc.py
python -I scripts/kb_index.py
```

## Looking things up
```bash
python -I scripts/kb_search.py "spacing effect" -n 8          # all books, ranked, with printed page cites
python -I scripts/kb_search.py "shaping" --book chance        # one book
python -I scripts/kb_read.py chance 129 135                    # read printed pages 129-135 of a book
python -I scripts/kb_check.py                                  # copyright guardrail
```
Use the output to understand and paraphrase. Cite as `book slug, p. N` (printed page).

## Adding another textbook (any course)
`kb_extract.py <pdf> <slug>` -> add its chapter list to `SPECS` in `scripts/kb_toc.py` (+ an `OFFSET_OVERRIDE` if the auto offset is off; check an opener page by hand) -> `kb_index.py`. Course textbooks that already have a `pages.jsonl` become searchable alongside the learning books.
