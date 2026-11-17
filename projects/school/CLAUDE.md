# school — fast-track study guides

Private repo. Each course gets a study site at `samuelbaird.com/learn/<course>` (unlisted: `noindex`, not in the sitemap or nav), built from the Canvas course, the syllabus and the textbook.

## Hard rules (read first)
- **Copyright.** Textbook PDFs, instructor files and solution manuals stay local (`.gitignore` blocks `*.pdf`, `textbook/cache/`, `canvas/files/`, `knowledge/cache/`, `knowledge/sources/`). The public JSON holds section/page/problem-number references, Canvas links and original writing — no book text. Notes under `knowledge/` are paraphrase with page cites; run `python -I scripts/kb_check.py` (must report 0) before committing them.
- **Read-only Canvas.** Scan with Claude in Chrome. Never submit, edit or take quizzes. Ask before downloading files.
- **ME 3410 assignment pipeline** (`courses/me3410/`, see its README): the instructor allows AI on assignments and tests if its use is stated at the top. Every document starts with the AI-use statement built into `pipeline/report.py`; never remove it. The student reviews and submits; nothing here submits to Canvas. Generated Word files, ANSYS output and handouts stay local (gitignored); the public tracker JSON holds statuses and deliverable names only.

## Layout
```
courses/<id>/
  canvas/scan.md          notes from the Canvas scan (dates, scope, HW, study guides, file index)
  textbook/toc.json       chapter/section/example page map (refs only), built by scripts/build_toc.py
  textbook/cache/         gitignored: problem index and any extracted text, local only
  content.py              hand-written study content per unit (videos, bullets, equations, pitfalls)
  problems/*.py           original practice problems; every number in a solution is computed in Python
  build_course.py         assembles course.json (add --verify-videos to check every YouTube id via oEmbed)
  course.json             the page's data
knowledge/                how people learn + a searchable library of textbook material (see knowledge/README.md)
  learning/playbook.md    12 rules for building study guides, with a per-unit checklist (read before content work)
  learning/glossary.md    cross-book terms in our own words
  learning/books/<slug>.md  chapter digests of 6 learning-science textbooks (own words, page cites)
  cache/, sources/        gitignored: extracted page text, FTS index, textbook PDFs
scripts/
  kb_extract.py kb_toc.py kb_index.py   PDF -> per-page text cache -> chapter map -> SQLite FTS index (any textbook)
  kb_search.py kb_read.py               search the index / read cached pages by printed page range (local reading only)
  kb_check.py                           copyright guardrail: flags verbatim runs of book text in committed notes
  build_toc.py            PDF bookmarks -> toc.json (page offset: printed = PDF - 24 for Bergman 8e)
  problem_index.py        problem numbers by section heading (rough; headings can be off)
  publish.mjs             validate course.json and copy it to ../../sites/samuelbaird.com/learn/<id>/
```
The page itself (`learn/<id>/index.html`) lives in the `Samuelbaird.com` repo; `learn/me3320/index.html` is the template for new courses.

## Workflow for a new course
1. **Scan Canvas** (Claude in Chrome, logged in): modules, syllabus, calendar, assignments + due dates, exam rules, study guides, posted examples. In-page `fetch('/api/v1/courses/<id>/modules?include[]=items')` lists everything; pdf.js from cdnjs can read PDF text in the page, rendered into the DOM and read with `get_page_text` (long JS return values are truncated).
2. **Map the textbook**: `python -I scripts/build_toc.py "<pdf>" courses/<id>/textbook/toc.json`.
3. **Write `content.py`**: one unit per calendar block, in course order, tagged by which exam covers it.
4. **Find videos** by searching YouTube inside the logged-in Chrome (`/results?search_query=…&sp=EgIQAQ%253D%253D`, parse `ytInitialData`). Prefer chapter-aligned channels (for Bergman: Kody Powell, Ron Hugo, Regina Vrikkis, Brian Bernard, LearnChemE). Verify with `--verify-videos`; unembeddable videos are dropped automatically.
5. **Write problems** in `problems/part*.py` using `common.T()` templating (`<<name:.3g>>`, `<<x:sci3>>`) so solutions are computed, never typed. Keep a self-check (`python partN.py`) that fails on leftover `<<`.
6. `python courses/<id>/build_course.py --verify-videos && node scripts/publish.mjs <id>`.
7. Preview the site (`site-preview` in the workspace `.claude/launch.json`, port 4173), check every unit renders without KaTeX errors, then branch + PR on `Samuelbaird.com`.

## Teaching approach (read `knowledge/learning/playbook.md` before writing `content.py` or `problems/`)
The short version, each rule backed by the learning-science books:
1. **Retrieval first** — questions before answers; prefer problems and recall prompts over more reading.
2. **Immediate, specific feedback** — solutions name the exact error and show the sanity check; every pitfall has a problem that triggers it.
3. **Space and revisit** — an expanding review schedule tied to the exam dates, earlier-unit review problems inside later units, cumulative mocks.
4. **Mix and contrast** — put look-alike cases side by side with the deciding feature; mix methods so learners must choose before computing.
5. **Worked example → guided → independent**, with difficulty tags; early wins, then exam-like problems.
6. **Frame and meaning** — a one-sentence goal per unit, equations with their conditions of use, chunked `know` blocks (about four ideas).
7. **Exam-format and novel-setup practice** — transfer is programmed, not assumed.
8. **Calibrate** — predict-then-check on mocks; readiness checklist; say that rereading feels better than it works.
9. **Effort-based motivation** — progress tracking, specific next steps, no punitive wording; test-day routine and graded exam rehearsal.
Integrity rules above still win over all of this. Look up anything in the books with `scripts/kb_search.py`; cite as book + printed page and paraphrase.

## General how-tos
- `notes/download-course-videos-kaltura.md`: download, transcribe and clip UVU Canvas/Kaltura lecture recordings (personal use).

## Gotchas
- `python -I` ignores the script's folder; use plain `python` for the builders and `-I` only for scripts that read untrusted files.
- PowerShell/bash tool calls can collapse `\\` to `\`; write TeX with the Write/Edit tools, not shell heredocs.
- YouTube pages enforce Trusted Types: set `textContent`, not `innerHTML`.
