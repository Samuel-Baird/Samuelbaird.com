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
- Geometry import and image export fail on paths with spaces (this repo lives under "AI projects"):
  pass `ASSETS`/`OUT` through a space-free folder. `work/test1/run_ansys.sh` stages them in
  `%LOCALAPPDATA%\Temp\me3410_test1` and copies the outputs back.
- The Student license can deny a solve that starts right after the previous one ("Maximum licensed number
  of demo users"). The solution just shows SolveFailed; `solve.out` in `AN.WorkingDir` says why.
  `work/test1/line_common.py: solve_retry()` waits and retries.
- Line-body models (trusses, frames, stepped shafts): each STEP edge imports as its own body. Join them
  with one node merge per joint (`merge_joints()` in `work/test1/line_common.py`). A Shear-Moment Diagram
  must be scoped to an edge Path from Construction Geometry and added after the solve; an unscoped one
  leaves the solution UnderDefined and the solve fails. Its `PlotData` is SI, in the path's local axes.
- `SetFit` leaves a short line body tiny in a wide image; `export_front_framed()` sets the focal point and
  scene width instead.
- Framing a zoom: set `Camera.SceneHeight` as well as `SceneWidth` (width × image height / width). With only the
  width set, the camera keeps the fitted height and the "close-up" barely zooms. A custom `ViewVector` of (0, 0, 1)
  skews 2D views; use the Front orientation and then set the focal point (`work/hw6/ansys.py: shot()`).
- Run one Mechanical at a time. `mech.py --new` while another instance is still open makes every solve fail on
  the Student license (results read back as zeros). Close stray `AnsysWBU`/`ansyscl` processes first.
- Fatigue Tool: `MeanStressTheory` takes `MeanStressTheoryType` (`NoneStress`, `Goodman`, `Soderberg`, `Gerber`...),
  not `FatigueAnalysisType`; there is no member called `None`. `LoadingType` takes `FatigueLoadType`
  (`FullyReversed`, `Ratio` + `LoadingRatio`). Its Goodman safety factor is the load factor
  1/n = σa/Se + σm/Su (`work/ict1028a/hand.py: fatigue()` reproduces it to round-off).
- Edge Sizing on a fillet with a coarse Face Sizing behind it (10 mm against 0.6 mm) adds few elements and gives
  erratic peak stresses; refine the face too, or use a Convergence object scoped to the fillet.
- To rerun only the later phases of a script on the live session, put them in a second file and run it with
  `SCRIPT=<file> bash run_ansys.sh` (globals persist; see `work/ict1028a/ansys_tail.py`).
- 3D views in batch mode: setting `Camera.ViewVector` does not take (the export stays on the last named
  orientation, e.g. a plan view). Use the named Iso orientation, `Camera.Rotate(180, CameraAxisType.ScreenY)` for
  the back, and set `FocalPoint` + `SceneWidth` + `SceneHeight` explicitly: `SetFit` crops tall parts in a
  1400 × 800 export (`work/bracket/ansys.py: view_export()`).
- Bearing Load + a Convergence object: the adaptive run's reactions drifted 2.7% above the applied load (the bearing
  distribution is re-applied on the refined mesh). Check the reactions of any adaptive run with a bearing load.
- 2D adaptive meshing (Convergence object): from a coarse start it can report "converged" before a stress
  singularity shows up, because the coarse mesh puts the peak elsewhere. Start it from a mesh fine enough to show
  the singular point, or put the Convergence object on deformation or a stress scoped away from it.

- Thermal → structural in one Mechanical session: `ST.ImportLoad(TH)` links a Steady-State Thermal analysis to a
  Static Structural one (the scripted version of dragging the system in Workbench); it adds the Imported Body
  Temperature, and solving ST after TH uses the thermal result (`work/hw8/ansys.py`).
- A bend made with build123d `revolve` imported into Mechanical as the 270° complement of the torus (face area 3×
  too large). Build pipe bends with `sweep` along a line-arc-line wire instead (`work/hw8/cad.py`).
- `mech.py` retries a failed phase once; for a phase that imports geometry that leaves a second body. Run with
  `--no-retry` while debugging a setup phase.
- Path results' `PlotData` has `X/Y/Z Coordinate` and `Values` keys (no length); compute the arc length from the
  coordinates (`work/hw8/solve.py: path_xy()`).
- A Fixed Support on a heated face also stops its in-plane thermal growth: expect σ_vM ≈ EαΔT/(1−ν) just under the
  face and singular peaks on its edges (`work/hw8`).

## Every document must have
1. The AI-use statement first (built into `Report`).
2. Given data with sources.
3. Hand calculations: symbolic form, numbers substituted, boxed result, units; every number computed in Python.
4. ANSYS: model with BCs and loads, mesh, the requested contours, mesh-convergence evidence.
5. A comparison table (hand vs. ANSYS, % difference) and a short discussion of any difference.

The student reviews each Word file, exports it to PDF and submits it on Canvas; nothing here submits anything.
