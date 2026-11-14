"""ME 3410 catch-up tracker -> tracker.json for samuelbaird.com/learn/me3410.

Edit STATUS below as work moves (todo -> pdf_ready -> submitted -> graded), then:
    python courses/me3410/tracker.py && node scripts/publish_tracker.mjs me3410

Due dates are Canvas due_at converted to Mountain time. Late policy (syllabus §6): 10% per
day late, capped at 50%. Grade weights come from Canvas assignment groups.
"""
import json
import math
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

HERE = Path(__file__).parent
MT = ZoneInfo("America/Denver")  # handles the Nov 1 switch from MDT to MST
COURSE = "https://uvu.instructure.com/courses/641173"
TODAY = datetime(2026, 11, 14, tzinfo=MT)

WEIGHTS = {"Attendance": 10, "Assignments": 25, "Exams": 40, "Term project": 25}

# Already graded in Canvas (as of the Nov 13 scan); counted in the projection.
GRADED = [
    ("HW 1 Syllabus", "Assignments", 10, 10),
    ("HW 2 Shape functions", "Assignments", 10, 10),
    ("HW 3 1D element", "Assignments", 10, 10),
    ("Pre-term project assignment", "Assignments", 10, 10),
    ("Team formation", "Term project", 10, 10),
    ("Roll call attendance", "Attendance", 76, 100),
]


def mt(iso_z):
    return datetime.fromisoformat(iso_z.replace("Z", "+00:00")).astimezone(MT)


# id, title, canvas assignment id, group, points, due (UTC from Canvas), plan date, hours,
# kind, status, deliverables, notes
ITEMS = [
    dict(id="tp-part1", title="Term Project Part I: Spar A (I-section)", cid=9347065, group="Term project",
         pts=10, due="2026-11-14T06:59:59Z", plan="2026-11-13", hrs=2, kind="Team · hand calcs + ANSYS",
         status="pdf_ready", pdf="TP_Part_I_Spar_A_I-section.docx",
         deliver=["FBD, resultant and root reactions (900 N, 450 N·m), LC2 torque 45 N·m",
                  "V(x), M(x) derivation and plots; checks at x = 0.25 m",
                  "Spar A centroid and I (parallel axis), area check",
                  "σ = Mc/I at root and x = 250 mm, FoS ≥ 2",
                  "Web shear VQ/It", "Tip deflection q₀L⁴/30EI and tapered numerical integral",
                  "Torsion J = ⅓Σbt³, tip twist (LC2)",
                  "Warping-restrained (Vlasov) twist explains the LC2 FE twist",
                  "ANSYS: constant + tapered, LC1 + LC2, hex mesh, 4-level mesh study (handout sizes), mass",
                  "Validation tables in the handout's §8.1 format",
                  "Appendix: four-spar hand values for the team summary table",
                  "Send the Word file to the team for the combined progress report"],
         note="Due tonight 11:59 PM MT (Canvas shows Nov 14 in UTC). Team submits one combined report; this Word file is the Spar A section."),
    dict(id="hw7", title="HW 7: 2D & 3D models", cid=9163932, group="Assignments", pts=10,
         due="2026-11-12T06:59:59Z", plan="2026-11-13", hrs=3, kind="ANSYS (2D + 3D) + hand checks",
         status="pdf_ready", pdf="HW7_2D_3D_Models.docx",
         deliver=["Q1 plane stress vs. strain, justified", "Q1 2D model (plane stress) with BCs/loads",
                  "Q1 3D model with BCs/loads", "Q1 mesh refinement for both",
                  "Q1 reactions at A and B, equilibrium check", "Q1 von Mises, total and X/Y deformation of C (2D vs 3D)",
                  "Q2 spherical vessel model (2D axisymmetric or 3D) and BCs",
                  "Q2 table: radial deformation for E-glass, S-glass, Kevlar, carbon fiber",
                  "Q2 selected material and why", "Q2 radial deformation, radial stress, hoop stress contours"],
         note="Already 1 day late on Nov 13; every day costs another 10%. Q2 uses ANSYS library fibers; Kevlar 49 "
              "is not in the library, so it comes from the handout table (ν = 0.36 assumed)."),
    dict(id="hw4", title="HW 4: Truss element", cid=9163925, group="Assignments", pts=10,
         due="2026-09-28T05:59:59Z", plan="2026-11-13", hrs=1, kind="Direct-stiffness hand solution + ANSYS links",
         status="pdf_ready", pdf="HW4_Truss_Element.docx",
         deliver=["Q1 FE hand solution: element and global stiffness, joint deflections",
                  "Q1 member stresses and reaction forces", "Q1 verification (method of joints, equilibrium)",
                  "Q2 ANSYS model (link elements), deflections, stresses, reactions",
                  "Q2 comparison table with the hand solution"],
         note="Graded 0 because it was never submitted. Late cap is 50%, so it is still worth up to 5 points."),
    dict(id="test1", title="Test 1 (1D, truss, beam)", cid=9349636, group="Exams", pts=50,
         due="2026-10-15T05:59:59Z", plan="2026-11-14", hrs=4, kind="Hand calcs + ANSYS + statics checks",
         status="pdf_ready", pdf="Test1_1D_Truss_Beam.docx",
         deliver=["Q1 1D stepped shaft: 7-step FE hand solution (u₂, u₃, midpoint of element 1, reactions, σ₁)",
                  "Q1 ANSYS: model, directional deformation, reactions, direct stress per element",
                  "Q1 comparison table", "Q2 truss ANSYS: model, X/Y deformation, reactions, member stresses",
                  "Q2 statics reactions + % error table", "Q3 beam ANSYS: model, deflection, reactions, SFD/BMD, max combined stress",
                  "Q3 statics/MoM reactions and max bending stress + % error table",
                  "Extras: member forces and joint deflections (Q2), midspan deflection with shear term (Q3), mesh studies"],
         note="Worth the entire 40% exam category right now (currently 0). Instructor commented Nov 2: \"Please submit the exam to improve your grade.\" "
              "Word file ready: every reaction and stress matches ANSYS to round-off; Q3 deflection differs by shear deformation (explained)."),
    dict(id="hw5", title="HW 5: Beam element (W16x31)", cid=9163927, group="Assignments", pts=10,
         due="2026-10-12T05:59:59Z", plan="2026-11-13", hrs=1.5, kind="FE hand solution + ANSYS beam + statics/MoM",
         status="pdf_ready", pdf="HW5_Beam_Element.docx",
         deliver=["Two-element FE hand solution (stiffness, equivalent loads, nodal displacements, reactions)",
                  "FE model with BCs and loads", "Total deformation", "Directional deformation Y",
                  "Max bending stress (Beam Tool)", "Reaction forces (wall force + moment, roller)",
                  "Statics & MoM validation (superposition, V/M diagrams, deflection curve)",
                  "Mesh study and hand vs. ANSYS table, shear-deformation explanation"],
         note="Default ANSYS (Timoshenko BEAM188) differs from the hand solution by shear deformation; the Word file "
              "explains it and shows a shear-rigid ANSYS run that matches."),
    dict(id="ict-1", title="In-class tutorial: 1D / Truss / Beam", cid=9163939, group="Assignments", pts=10,
         due="2026-10-06T05:59:59Z", plan="2026-11-15", hrs=1.5, kind="ANSYS ×3 + validation",
         status="pdf_ready", pdf="InClass_1D_Truss_Beam.docx",
         deliver=["Q1 1D shaft: model, deflection at B, reactions, element stresses", "Q2 truss: model, deflection at A, reactions, stresses",
                  "Q3 beam: model, max deflection, reactions, SFD/BMD, stresses", "Validation for each",
                  "Extras: FE hand solution (Q1), elastic curve of span AB (Q3), shear-rigid check, mesh studies"],
         note="Word file ready: every reaction, stress and the handout's reference values match ANSYS to round-off. "
              "The handout's Q3 y_max = 0.238 in is the upward peak of span AB, not the deflection at C (0.418 in); "
              "the Word file explains this."),
    dict(id="hw6", title="HW 6: Plate under distributed pressure", cid=9163930, group="Assignments", pts=10,
         due="2026-10-29T05:59:59Z", plan="2026-11-13", hrs=1.5, kind="ANSYS 2D + hand checks",
         status="pdf_ready", pdf="HW6_Plate_Pressure.docx",
         deliver=["Plane stress or strain, justified", "FE model, BCs and loads", "Manual mesh refinement (+ adaptive if possible)",
                  "Deformed vs. undeformed", "Total deformation", "Von Mises contour",
                  "Hand checks: reactions, beam-theory stress at x = 140 mm and in the fillet, tip-deflection bounds",
                  "Wall/top corner stress singularity explained; adaptive runs that converge and one that does not"],
         note="Left edge fixed (wall hatching), holes free. Reactions match statics exactly; peak meaningful stress 89 MPa "
              "on the R50 fillet (FoS 2.8 vs. 250 MPa); tip deflection 0.215 mm."),
    dict(id="ict-1028a", title="In-class tutorial 10-28 (problem 1)", cid=9361468, group="Assignments", pts=10,
         due="2026-10-30T05:59:59Z", plan="2026-11-16", hrs=1.5, kind="ANSYS 2D",
         status="pdf_ready", pdf="InClass_10-28_P1.docx",
         deliver=["Stepped plate with R25 fillet, 2D plane stress (justified)", "FE model, BCs and loads",
                  "Meshing techniques: face sizing, edge sizing, adaptive convergence (vs. the in-class table)",
                  "Hand check: nominal stress × Kt at the fillet, static safety factor (DET)",
                  "Von Mises, total deformation, stress along the fillet",
                  "Fatigue Tool: life and safety factor at R = -1 and R = -0.5 (Goodman), checked by hand"],
         note="Word file ready. The 10-28 notes are handwritten (no problem statement), so problem 1 is taken as the "
              "stepped plate worked in class. Fillet stress converges to 113.4 MPa, matching the class table; hand Kt σ0 = "
              "118.1 MPa (Kt 1.4 extrapolated; effective 1.35). Fatigue safety factors are below 1 at 10^6 cycles."),
    dict(id="ict-1028b", title="In-class tutorial 10-28 (problem 2, bonus)", cid=9361471, group="Assignments", pts=10,
         due="2026-10-30T05:59:59Z", plan="2026-11-16", hrs=1, kind="ANSYS 2D",
         status="pdf_ready", pdf="InClass_10-28_P2.docx",
         deliver=["Q2 of the Plane Strain-Stress Tutorial (V2): long pressurized concrete block with a Ø50 hole",
                  "Plane strain, justified", "FE model, BCs and loads (fixed base, 50/25 MPa top, 10 MPa sides)",
                  "Max von Mises and location; σx, σy, τxy; max vertical displacement",
                  "Mesh convergence (8 meshes); fillet-radius study (R5-R40)",
                  "Hand checks: statics, beam theory on the hole section, Kirsch hole stresses, column displacement",
                  "Concrete failure check (Coulomb-Mohr, 3 / 40 MPa)"],
         note="Word file ready. Problem source found on Canvas: Q2 of the Plane Strain-Stress Tutorial (V2). Reactions "
              "match statics exactly. Peak von Mises 142 MPa on the R20 fillet; hole sides -129 MPa, crown +17 MPa "
              "(Kirsch with the FE nominal stress within 2% at the sides). The block fails: the 50 MPa load alone "
              "exceeds the 40 MPa crushing strength (Mohr-Coulomb minimum 0.17 at the hole crown)."),
    dict(id="ict-1104", title="In-class tutorial 11-4", cid=9365212, group="Assignments", pts=10,
         due="2026-11-06T06:59:59Z", plan="2026-11-17", hrs=1.5, kind="ANSYS + mesh refinement",
         status="blocked", pdf="InClass_11-04.docx",
         deliver=["FE model with BCs and loads (state them)", "Mesh refinement curve", "Equivalent stress", "Total deformation"],
         note="No handout on Canvas. Ask Dr. Seibi or a teammate which tutorial was done on Nov 4 (likely axisymmetric, from the module order)."),
    dict(id="bracket", title="In-class tutorial: 3D bracket", cid=9163938, group="Assignments", pts=10,
         due="2026-11-20T06:59:59Z", plan="2026-11-18", hrs=2, kind="3D CAD + ANSYS",
         status="pdf_ready", pdf="InClass_3D_Bracket.docx",
         deliver=["FE model with BCs and loads (bearing load + axial force on the 30 mm hole, base fixed)",
                  "Equivalent stress (converged on the R10 fillet)", "Total deformation and X/Y/Z deformation",
                  "Reaction force and moment, checked against statics",
                  "Beam-theory checks of the upright, mesh study, bearing load vs. uniform force"],
         note="Word file ready. Peak von Mises 152.6 MPa on the R10 fillet (yield safety factor 1.83); total deformation "
              "0.654 mm at the top of the upright; reactions match the load to 0.01%. Geometry placements read from "
              "the isometric sketch are stated in the document."),
    dict(id="hw8", title="HW 8: Pipe elbow thermal stress", cid=9163933, group="Assignments", pts=10,
         due="2026-11-21T06:59:59Z", plan="2026-11-19", hrs=3, kind="Steady thermal → static structural",
         status="pdf_ready", pdf="HW8_Pipe_Elbow_Thermal.docx",
         deliver=["Elbow with a second flange at the free end (aluminium alloy)",
                  "Thermal: model with BCs (initial temp, temperature, convection)", "Temperature distribution", "Heat flux",
                  "Structural: both flange faces fixed, imported temperature", "Total deformation", "Equivalent stress",
                  "Safety factor and fail / no-fail"],
         note="Word file ready. Elbow at 99.71-100 C, heat flow 50.95 W (hand 51.00 W). Fixed flanges push back with "
              "15.3 kN and 1.44 kN·m (hand beam models 14.0-17.3 kN, moment within 1%); max deformation 0.453 mm. "
              "Bend 109 MPa (n = 2.6); flange material at the bolted faces about 195-264 MPa (n = 1.06-1.30, hand "
              "EαΔT/(1−ν) = 190 MPa); the 548 MPa peak is a singular fixed-face edge. Verdict: does not fail."),
    dict(id="hw9", title="HW 9: 3D modeling", cid=9163934, group="Assignments", pts=10,
         due="2026-12-03T06:59:59Z", plan="2026-11-24", hrs=4, kind="Axisymmetric vs 3D + 3D bracket",
         status="todo", pdf="HW9_3D_Modeling.docx",
         deliver=["Q1 rotating part at 100 rpm: axisymmetric model", "Q1 3D model", "Q1 compare total deformation and equivalent stress",
                  "Q2 lifting bracket: half model", "Q2 full model",
                  "Q2 for both: FEM with BCs, total deformation, Y deformation, equivalent stress, shear stress"]),
    dict(id="post", title="Post-term project assessment (individual)", cid=9351753, group="Assignments", pts=10,
         due="2026-12-05T06:59:59Z", plan="2026-12-03", hrs=2, kind="Statics / MoM / FEA questions",
         status="todo", pdf="Post_Term_Assessment_FormB.docx",
         deliver=["Answer Form B questions (statics, MoM, FEA interpretation)"]),
    dict(id="tp-report", title="Term project report (team, 50 pts)", cid=9351779, group="Term project", pts=50,
         due="2026-12-10T06:59:59Z", plan="2026-12-05", hrs=6, kind="Team report: Spar A sections + full wing",
         status="todo", pdf="TP_Report_Spar_A.docx",
         deliver=["Spar A: Part I results carried into the report", "Wing model with NACA 0018 skin (team)",
                  "Mesh convergence and validation", "Optional eigenvalue buckling", "Design recommendation inputs for Spar A"]),
]


def late_days(due, when):
    return max(0, math.ceil((when - due).total_seconds() / 86400))


def penalty(days):
    return min(0.5, 0.1 * days)


def build():
    items = []
    for prio, it in enumerate(ITEMS):
        it = dict(it, priority=prio + 1)
        due = mt(it["due"])
        plan = datetime.fromisoformat(it["plan"]).replace(hour=23, minute=0, tzinfo=MT)
        d = late_days(due, plan)
        it = dict(it, due_local=due.strftime("%a %b %d, %I:%M %p MT").replace(" 0", " "),
                  due_iso=due.isoformat(), url=f"{COURSE}/assignments/{it['cid']}",
                  late_days_at_plan=d, penalty_at_plan=penalty(d),
                  expected_pts=round(it["pts"] * 0.9 * (1 - penalty(d)), 2))
        items.append(it)
    items.sort(key=lambda x: (x["plan"], x["priority"]))

    # Grade projection: each group's earned/possible, weighted, Canvas-style.
    def project(include_plan):
        g = {k: [0.0, 0.0] for k in WEIGHTS}
        for _, grp, earned, possible in GRADED:
            g[grp][0] += earned
            g[grp][1] += possible
        for it in items:
            if it["id"] == "ict-1028b":
                continue  # bonus
            g[it["group"]][1] += it["pts"]
            if include_plan:
                g[it["group"]][0] += it["expected_pts"]
        tot = sum(WEIGHTS[k] * (g[k][0] / g[k][1]) for k in g if g[k][1])
        return round(tot, 1), {k: round(100 * g[k][0] / g[k][1], 1) for k in g if g[k][1]}

    now_total, now_groups = project(False)
    plan_total, plan_groups = project(True)
    data = {
        "course": "ME 3410 Applied Finite Element Analysis",
        "section": "002 · Fall 2026 · Dr. A. Seibi",
        "canvas": COURSE,
        "updated": TODAY.strftime("%b %d, %Y"),
        "policy": {
            "ai": "AI tools are permitted for coursework and exams, provided AI use is clearly disclosed in the "
                  "submission (Dr. Seibi's Canvas message to the class, Nov 13, 2026). Every document opens with an "
                  "AI-use statement.",
            "late": "Late work accepted, minus 10% per day, capped at 50% (syllabus §6).",
            "weights": WEIGHTS,
        },
        "grade": {
            "canvas_current": 52.6, "canvas_final_zeros": 17.3,
            "if_nothing_submitted": now_total, "if_plan_completed": plan_total,
            "groups_now": now_groups, "groups_plan": plan_groups,
            "assumption": "Projection assumes 90% quality on each item and the late penalty on its plan date.",
        },
        "pipeline": [
            "Read the handout (local, gitignored): problem statement + figures.",
            "solve.py: hand calculations with every number computed in Python (shown as symbolic → substituted → result).",
            "cad.py: geometry to STEP (build123d) when ANSYS needs a solid or line model.",
            "ansys.py: ANSYS Mechanical 2026 R1 Student run through PyMechanical: mesh study, solve, screenshots, results JSON.",
            "report.py: one Word document per assignment (native equations), AI-use statement first, hand calcs, ANSYS screenshots, comparison tables.",
            "Open it in Word, review and edit, then File > Export > PDF.",
            "Submit the PDF on Canvas yourself and mark it submitted here.",
        ],
        "items": items,
        "graded": [{"title": t, "group": g, "earned": e, "possible": p} for t, g, e, p in GRADED],
    }
    (HERE / "tracker.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"tracker.json: {len(items)} items · now {now_total}% · with plan {plan_total}%")


if __name__ == "__main__":
    build()
