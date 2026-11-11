# school — fast-track study guides

Private repo. Each course gets a study site at `samuelbaird.com/learn/<course>` (unlisted: `noindex`, not in the sitemap or nav), built from the Canvas course, the syllabus and the textbook.

## Hard rules (read first)
- **Academic integrity.** Syllabi usually allow AI for finding information and brainstorming and forbid it for solving assigned work or on tests/quizzes. ME 3320 does. So the site contains concepts, videos, equations and *original* practice problems only. Never solve assigned homework, take-home test problems or quiz problems. Never open the site during a take-home test.
- **Copyright.** Textbook PDFs, instructor files and solution manuals stay local (`.gitignore` blocks `*.pdf`, `textbook/cache/`, `canvas/files/`). The public JSON holds section/page/problem-number references, Canvas links and original writing — no book text.
- **Read-only Canvas.** Scan with Claude in Chrome. Never submit, edit or take quizzes. Ask before downloading files.

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
scripts/
  build_toc.py            PDF bookmarks -> toc.json (page offset: printed = PDF - 24 for Bergman 8e)
  problem_index.py        problem numbers by section heading (rough; headings can be off)
  publish.mjs             validate course.json and copy it to ../Samuelbaird.com/learn/<id>/
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

## Gotchas
- `python -I` ignores the script's folder; use plain `python` for the builders and `-I` only for scripts that read untrusted files.
- PowerShell/bash tool calls can collapse `\\` to `\`; write TeX with the Write/Edit tools, not shell heredocs.
- YouTube pages enforce Trusted Types: set `textContent`, not `innerHTML`.
