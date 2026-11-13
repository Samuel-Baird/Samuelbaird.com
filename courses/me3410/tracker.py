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
TODAY = datetime(2026, 11, 13, tzinfo=MT)

WEIGHTS = {"Attendance": 10, "Assignments": 25, "Exams": 40, "Term project": 25}

# Already graded in Canvas (as of the Nov 13 scan); counted in the projection.
GRADED = [
    ("HW 1 Syllabus", "Assignments", 10, 10),
    ("HW 2 Shape functions", "Assignments", 10, 10),
    ("HW 3 1D element", "Assignments", 10, 10),
    ("HW 4 Truss element", "Assignments", 0, 10),
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
         status="pdf_ready", pdf="TP_Part_I_Spar_A_I-section.pdf",
         deliver=["FBD, resultant and root reactions (900 N, 450 N·m), LC2 torque 45 N·m",
                  "V(x), M(x) derivation and plots; checks at x = 0.25 m",
                  "Spar A centroid and I (parallel axis), area check",
                  "σ = Mc/I at root and x = 250 mm, FoS ≥ 2",
                  "Web shear VQ/It", "Tip deflection q₀L⁴/30EI and tapered numerical integral",
                  "Torsion J = ⅓Σbt³, tip twist (LC2)",
                  "ANSYS: constant + tapered, LC1 + LC2, mesh convergence, comparison tables",
                  "Send PDF to the team for the combined progress report"],
         note="Due tonight 11:59 PM MT (Canvas shows Nov 14 in UTC). Team submits one combined report; this PDF is the Spar A section."),
    dict(id="hw7", title="HW 7: 2D & 3D models", cid=9163932, group="Assignments", pts=10,
         due="2026-11-12T06:59:59Z", plan="2026-11-13", hrs=3, kind="ANSYS (2D + 3D) + hand checks",
         status="todo", pdf="HW7_2D_3D_Models.pdf",
         deliver=["Q1 plane stress vs. strain, justified", "Q1 2D model (plane stress) with BCs/loads",
                  "Q1 3D model with BCs/loads", "Q1 mesh refinement for both",
                  "Q1 reactions at A and B, equilibrium check", "Q1 von Mises, total and X/Y deformation of C (2D vs 3D)",
                  "Q2 spherical vessel model (2D axisymmetric or 3D) and BCs",
                  "Q2 table: radial deformation for E-glass, S-glass, Kevlar, carbon fiber",
                  "Q2 selected material and why", "Q2 radial deformation, radial stress, hoop stress contours"],
         note="Already 1 day late on Nov 13; every day costs another 10%. Do it right after Part I."),
    dict(id="test1", title="Test 1 (1D, truss, beam)", cid=9349636, group="Exams", pts=50,
         due="2026-10-15T05:59:59Z", plan="2026-11-14", hrs=4, kind="Hand calcs + ANSYS + statics checks",
         status="todo", pdf="Test1_1D_Truss_Beam.pdf",
         deliver=["Q1 1D stepped shaft: 7-step FE hand solution (u₂, u₃, midpoint of element 1, reactions, σ₁)",
                  "Q1 ANSYS: model, directional deformation, reactions, direct stress per element",
                  "Q1 comparison table", "Q2 truss ANSYS: model, X/Y deformation, reactions, member stresses",
                  "Q2 statics reactions + % error table", "Q3 beam ANSYS: model, deflection, reactions, SFD/BMD, max combined stress",
                  "Q3 statics/MoM reactions and max bending stress + % error table"],
         note="Worth the entire 40% exam category right now (currently 0). Instructor commented Nov 2: \"Please submit the exam to improve your grade.\""),
    dict(id="hw5", title="HW 5: Beam element (W16x31)", cid=9163927, group="Assignments", pts=10,
         due="2026-10-12T05:59:59Z", plan="2026-11-15", hrs=1.5, kind="ANSYS beam + statics/MoM",
         status="todo", pdf="HW5_Beam_Element.pdf",
         deliver=["FE model with BCs and loads", "Total deformation", "Directional deformation Y",
                  "Max bending stress (Beam Tool)", "Reaction forces", "Statics & MoM validation"],
         note="Instructor's solutions are posted on Canvas; use them to check, not to copy."),
    dict(id="ict-1", title="In-class tutorial: 1D / Truss / Beam", cid=9163939, group="Assignments", pts=10,
         due="2026-10-06T05:59:59Z", plan="2026-11-15", hrs=1.5, kind="ANSYS ×3 + validation",
         status="todo", pdf="InClass_1D_Truss_Beam.pdf",
         deliver=["Q1 1D shaft: model, deflection at B, reactions, element stresses", "Q2 truss: model, deflection at A, reactions, stresses",
                  "Q3 beam: model, max deflection, reactions, SFD/BMD, stresses", "Validation for each"],
         note="Same tooling as Test 1, so do it the same weekend."),
    dict(id="hw6", title="HW 6: Plate under distributed pressure", cid=9163930, group="Assignments", pts=10,
         due="2026-10-29T05:59:59Z", plan="2026-11-16", hrs=1.5, kind="ANSYS 2D",
         status="todo", pdf="HW6_Plate_Pressure.pdf",
         deliver=["Plane stress or strain, justified", "FE model, BCs and loads", "Manual mesh refinement (+ adaptive if possible)",
                  "Deformed vs. undeformed", "Total deformation", "Von Mises contour"]),
    dict(id="ict-1028a", title="In-class tutorial 10-28 (problem 1)", cid=9361468, group="Assignments", pts=10,
         due="2026-10-30T05:59:59Z", plan="2026-11-16", hrs=1.5, kind="ANSYS 2D",
         status="todo", pdf="InClass_10-28_P1.pdf",
         deliver=["Problem 1 from the 10-28 handout (plane stress/strain tutorial)"],
         note="The 10-28 handout is a step-by-step screenshot tutorial; problem 1 is required."),
    dict(id="ict-1028b", title="In-class tutorial 10-28 (problem 2, bonus)", cid=9361471, group="Assignments", pts=10,
         due="2026-10-30T05:59:59Z", plan="2026-11-16", hrs=1, kind="ANSYS 2D",
         status="todo", pdf="InClass_10-28_P2.pdf",
         deliver=["Problem 2 from the 10-28 handout (bonus points)"]),
    dict(id="ict-1104", title="In-class tutorial 11-4", cid=9365212, group="Assignments", pts=10,
         due="2026-11-06T06:59:59Z", plan="2026-11-17", hrs=1.5, kind="ANSYS + mesh refinement",
         status="blocked", pdf="InClass_11-04.pdf",
         deliver=["FE model with BCs and loads (state them)", "Mesh refinement curve", "Equivalent stress", "Total deformation"],
         note="No handout on Canvas. Ask Dr. Seibi or a teammate which tutorial was done on Nov 4 (likely axisymmetric, from the module order)."),
    dict(id="bracket", title="In-class tutorial: 3D bracket", cid=9163938, group="Assignments", pts=10,
         due="2026-11-20T06:59:59Z", plan="2026-11-18", hrs=2, kind="3D CAD + ANSYS",
         status="todo", pdf="InClass_3D_Bracket.pdf",
         deliver=["FE model with BCs and loads", "Equivalent stress", "Total deformation and X/Y/Z deformation", "Reaction force"]),
    dict(id="hw8", title="HW 8: Pipe elbow thermal stress", cid=9163933, group="Assignments", pts=10,
         due="2026-11-21T06:59:59Z", plan="2026-11-19", hrs=3, kind="Steady thermal → static structural",
         status="todo", pdf="HW8_Pipe_Elbow_Thermal.pdf",
         deliver=["Elbow with a second flange at the free end (aluminium alloy)",
                  "Thermal: model with BCs (initial temp, temperature, convection)", "Temperature distribution", "Heat flux",
                  "Structural: both flange faces fixed, imported temperature", "Total deformation", "Equivalent stress",
                  "Safety factor and fail / no-fail"]),
    dict(id="hw9", title="HW 9: 3D modeling", cid=9163934, group="Assignments", pts=10,
         due="2026-12-03T06:59:59Z", plan="2026-11-24", hrs=4, kind="Axisymmetric vs 3D + 3D bracket",
         status="todo", pdf="HW9_3D_Modeling.pdf",
         deliver=["Q1 rotating part at 100 rpm: axisymmetric model", "Q1 3D model", "Q1 compare total deformation and equivalent stress",
                  "Q2 lifting bracket: half model", "Q2 full model",
                  "Q2 for both: FEM with BCs, total deformation, Y deformation, equivalent stress, shear stress"]),
    dict(id="post", title="Post-term project assessment (individual)", cid=9351753, group="Assignments", pts=10,
         due="2026-12-05T06:59:59Z", plan="2026-12-03", hrs=2, kind="Statics / MoM / FEA questions",
         status="todo", pdf="Post_Term_Assessment_FormB.pdf",
         deliver=["Answer Form B questions (statics, MoM, FEA interpretation)"]),
    dict(id="tp-report", title="Term project report (team, 50 pts)", cid=9351779, group="Term project", pts=50,
         due="2026-12-10T06:59:59Z", plan="2026-12-05", hrs=6, kind="Team report: Spar A sections + full wing",
         status="todo", pdf="TP_Report_Spar_A.pdf",
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
            "ai": "Instructor allows AI if its use is stated at the beginning of each assignment (verbal permission; "
                  "the syllabus has no AI clause). Every PDF opens with an AI-use statement.",
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
            "report.py: one PDF per assignment, AI-use statement first, hand calcs, ANSYS screenshots, comparison tables.",
            "Review the PDF, then submit it on Canvas yourself and mark it submitted here.",
        ],
        "items": items,
        "graded": [{"title": t, "group": g, "earned": e, "possible": p} for t, g, e, p in GRADED],
    }
    (HERE / "tracker.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"tracker.json: {len(items)} items · now {now_total}% · with plan {plan_total}%")


if __name__ == "__main__":
    build()
