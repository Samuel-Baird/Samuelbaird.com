# ME 3410 assignment pipeline

The instructor allows AI on assignments and tests as long as its use is stated at the top of each one.
This folder turns a Canvas handout into a submission-ready Word document (native, editable equations; export to PDF from Word): AI-use statement, hand calculations,
ANSYS screenshots and a hand-vs-ANSYS comparison. Progress is tracked at
`samuelbaird.com/learn/me3410` (unlisted, noindex).

```
courses/me3410/
  canvas/scan.md          due dates, policies, file index (from the Nov 13 Canvas scan)
  canvas/files/           gitignored: handouts + _extract/<name>/{text.md, img/}
  pipeline/
    report.py             Report builder -> Markdown -> Word .docx via pandoc (reference.docx styles);
                          .pdf() also renders HTML/KaTeX -> PDF with headless Chrome
    make_reference_docx.py  builds reference.docx (AI box, hand-calc shading, tables)
    report.css            print styles; hand calcs sit on an engineering-paper "sheet"
    mech_common.py        helpers that run inside ANSYS Mechanical (import, NS, material, images)
    katex_render.cjs      server-side math rendering (npm i in pipeline/)
  work/<assignment>/
    cad.py                geometry -> STEP (build123d, run with ../../.venv-cad)
    ansys.py              Mechanical script: mesh study, loads, solve, screenshots, results JSON
    solve.py              hand calculations + figures + report -> ../../out/<name>.docx
  out/                    gitignored: the Word files to review, export to PDF and submit
  tracker.py              plan + statuses -> tracker.json (portal data)
```

## Run an assignment
```bash
cd courses/me3410/work/part1_spar_a
../../../../.venv-cad/Scripts/python.exe cad.py
MECHPY=~/.mcp-servers/pymechanical-mcp/venv/Scripts/python.exe
$MECHPY ../../../../scripts/mech.py ansys.py --lib ../../pipeline/mech_common.py \
  --var "ASSETS=$PWD/assets" --var "OUT=$PWD/ansys_out" --var MODE=full
python solve.py
```
Then update the item's status in `tracker.py`, run it, and `node scripts/publish_tracker.mjs me3410`.

## One-time setup
- ANSYS 2026 R1 Student (`C:\Program Files\ANSYS Inc\ANSYS Student\v261`); PyMechanical comes from the
  pymechanical MCP server's venv. `scripts/mech.py` launches Mechanical in batch mode or attaches to port 10000.
- `python -m venv .venv-cad && .venv-cad/Scripts/pip install build123d` (repo root, gitignored).
- `pip install pypandoc_binary python-docx` (pandoc bundled); `cd courses/me3410/pipeline && npm i` (KaTeX, only for the optional PDF path).

## Mechanical gotchas (2026 R1, learned the hard way)
- Spatial load formulas accept **one** variable (`x` or `z`, not both). For a load varying in two
  directions, split the face in CAD and apply one x-only formula per piece.
- A formula pressure needs `AppliedBy = Direct`, and its state stays "UnderDefined" until a later script
  call reads its properties and re-sets `AppliedBy`. `ansys.py` does this in `refresh()` after meshing.
- Put `ExtAPI.DataModel.Project.New()` in its own script call (`#%% split`), and set mesh properties
  (`ElementOrder`, `ElementSize`) in a later call than the geometry import: right after import they can
  be read-only. `mech.py` also retries a failed phase once after 3 s.
- Globals persist between script calls, so `#%% split` phases share state.
- Sweep fails on a body whose source face is split into several faces (e.g. a split loaded face);
  MultiZone meshes it as all-hex. ANSYS Student stops at 128,000 nodes: quadratic hexes run about 5.6
  nodes per element, so check the finest mesh's node count before a long study.
- Plots: `export_image` switches to mm/MPa and hides element edges, then restores m/Pa so formula loads
  are never reinterpreted.

## Every document must have
1. The AI-use statement first (built into `Report`).
2. Given data with sources.
3. Hand calculations: symbolic form, numbers substituted, boxed result, units; every number computed in Python.
4. ANSYS: model with BCs and loads, mesh, the requested contours, mesh-convergence evidence.
5. A comparison table (hand vs. ANSYS, % difference) and a short discussion of any difference.

The student reviews each Word file, exports it to PDF and submits it on Canvas; nothing here submits anything.
