# ME 3410-002 Applied Finite Element Analysis, Fall 2026: Canvas scan (Nov 13, 2026)

Canvas: https://uvu.instructure.com/courses/641173 · Instructor: Dr. Abdennour (AC) Seibi.
Scope of this scan, at the student's request: the catch-up assignments only (plus syllabus policy lines needed to plan).

## Policies that drive the plan
- **AI:** the syllabus has no AI clause, but Dr. Seibi's Canvas message to the class on Fri Nov 13, 2026 ("Accessing ANSYS remotely") says AI tools are permitted for coursework and exams, for assignments, problem-solving and examinations, provided AI use is clearly disclosed in the submission. Every document opens with an AI-use statement (`pipeline/report.py`).
- **ANSYS access:** remotely through the Citrix lab at myapps.uvu.edu (same message). The pipeline uses the local ANSYS 2026 R1 Student install.
- **Late work (syllabus §6):** accepted, minus 10% per day, capped at 50%.
- **Make-up exams:** only by arrangement. For Test 1, the instructor commented on Nov 2: "Please submit the exam to improve your grade."
- **Weights (Canvas groups):** Attendance 10 · Assignments 25 · Exams 40 · Term project 25.
- Canvas scores on Nov 13: 52.6% on graded work, 17.3% counting missing work as zero. HW 4 was graded 0 (not in the catch-up list).

## Due dates (Canvas `due_at` is UTC; local time is Mountain)
All "Nov 14 / Nov 20 / Nov 21 / Dec 3 / Dec 5 / Dec 10" dates in UTC are 11:59 PM MT the evening before.

| Item | Canvas id | Due (MT) | Pts | Group | Handout (local, gitignored) |
|---|---|---|---|---|---|
| In-class tutorial 1D/Truss/Beam | 9163939 | Mon Oct 5 | 10 | Assignments | In Class Tutorial (1D, Truss, Beam) - V2.pdf |
| HW 5 Beam element | 9163927 | Sun Oct 11 | 10 | Assignments | HW5 - Beam Element.pdf (+ 2 posted solutions) |
| Test 1 | 9349636 | Wed Oct 14 | 50 | Exams | TEST 1 (10-7-2027) - V1.docx |
| HW 6 Plate under pressure | 9163930 | Wed Oct 28 | 10 | Assignments | PLATE UNDER DISTRIBUTED PRESSURE - V1.docx |
| In-class tutorial 10-28 (×2, #2 bonus) | 9361468, 9361471 | Thu Oct 29 | 10 + 10 | Assignments | IN Class Tutorial (10-28-26).docx (screenshot tutorial) |
| In-class tutorial 11-4 | 9365212 | Thu Nov 5 | 10 | Assignments | none on Canvas: ask which tutorial |
| HW 7 2D & 3D models | 9163932 | Wed Nov 11 | 10 | Assignments | HW 7 (2-3D Models) - V1.pdf |
| Term Project Part I | 9347065 | **Fri Nov 13** | 10 | Term project | Term Project Part I - Progress Report - V1.docx |
| 3D bracket in-class | 9163938 | Thu Nov 19 | 10 | Assignments | IN CLASS TUTOTIAL (3D BRACKET).docx |
| HW 8 Pipe elbow thermal | 9163933 | Fri Nov 20 | 10 | Assignments | THERMAL-STRESS ANALYSIS TUTORIAL - PIPE ELBOW - V1.docx |
| HW 9 3D modeling | 9163934 | Wed Dec 2 | 10 | Assignments | 3D Modeling-1-1-1.docx + HW9 Q2 hint |
| Post-term assessment (individual) | 9351753 | Fri Dec 4 | 10 | Assignments | AFEA_Post_Form B.docx |
| Term project report (team) | 9351779 | Wed Dec 9 | 50 | Term project | WING_TERM_PROJECT - V2.docx |

## HW 8 instructions (Canvas assignment text, paraphrased)
The handout is the pipe-elbow thermal-stress tutorial; the assignment page changes it: use Aluminium alloy, add a
second flange of the same dimensions at the free end. (1) Steady-state thermal with the tutorial loading: FE model with
BCs (initial temperature, temperature, convection), temperature distribution, heat flux. (2) Static structural with
the imported temperature and the outer faces of both flanges fixed: FE model with BCs, total deformation, equivalent
stress, and whether the elbow fails under static loading (compute the safety factor).

## Term project
Team project, four spars (A I-section, B C-channel, C box, D twin-web); each student takes one.
The student's spar: **A, I-section** (H 60, B 55, tf 6, tw 4 mm, 852 mm²). Material: ANSYS Aluminum Alloy.
Load q(x) = 1200(1 − x/L) N/m, L = 1.5 m; LC2 offset e = 50 mm. Validation section x = 250 mm.
Requirements: FoS ≥ 2, tip deflection ≤ 8 mm. The handout's reference deflection (5.64 mm) uses E = 69 GPa;
ANSYS Aluminum Alloy has E = 71 GPa (5.49 mm).

## Files
Downloaded with permission to `canvas/files/` (gitignored), extracted with
`python -I scripts/extract_handouts.py courses/me3410/canvas/files` into `canvas/files/_extract/<name>/{text.md,img/}`.
