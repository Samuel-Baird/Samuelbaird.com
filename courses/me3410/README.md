# ME 3410 assignment pipeline

The instructor allows AI on assignments and tests as long as its use is stated at the top of each one.
This folder turns a Canvas handout into a submission-ready PDF: AI-use statement, hand calculations,
ANSYS screenshots and a hand-vs-ANSYS comparison. Progress is tracked at
`samuelbaird.com/learn/me3410` (unlisted, noindex).

```
courses/me3410/
  canvas/scan.md          due dates, policies, file index (from the Nov 13 Canvas scan)
  canvas/files/           gitignored: handouts + _extract/<name>/{text.md, img/}
  pipeline/
    report.py             Report builder -> HTML (KaTeX rendered in Node) -> PDF (headless Chrome)
    report.css            print styles; hand calcs sit on an engineering-paper "sheet"
    mech_common.py        helpers that run inside ANSYS Mechanical (import, NS, material, images)
    katex_render.cjs      server-side math rendering (npm i in pipeline/)
  work/<assignment>/
    cad.py                geometry -> STEP (build123d, run with ../../.venv-cad)
    ansys.py              Mechanical script: mesh study, loads, solve, screenshots, results JSON
    solve.py              hand calculations + figures + report -> ../../out/<name>.pdf
  out/                    gitignored: the PDFs to review and submit
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
- `cd courses/me3410/pipeline && npm i` (KaTeX).

## Mechanical gotchas (2026 R1, learned the hard way)
- Spatial load formulas accept **one** variable (`x` or `z`, not both). For a load varying in two
  directions, split the face in CAD and apply one x-only formula per piece.
- A formula pressure needs `AppliedBy = Direct`, and its state stays "UnderDefined" until a later script
  call reads its properties and re-sets `AppliedBy`. `ansys.py` does this in `refresh()` after meshing.
- Put `ExtAPI.DataModel.Project.New()` in its own script call (`#%% split`) before importing geometry;
  in the same call, mesh properties can be read-only.
- Globals persist between script calls, so `#%% split` phases share state.
- Plots: `export_image` switches to mm/MPa and hides element edges, then restores m/Pa so formula loads
  are never reinterpreted.

## Every PDF must have
1. The AI-use statement first (built into `Report`).
2. Given data with sources.
3. Hand calculations: symbolic form, numbers substituted, boxed result, units; every number computed in Python.
4. ANSYS: model with BCs and loads, mesh, the requested contours, mesh-convergence evidence.
5. A comparison table (hand vs. ANSYS, % difference) and a short discussion of any difference.

The student reviews each PDF and submits it on Canvas themself; nothing here submits anything.
