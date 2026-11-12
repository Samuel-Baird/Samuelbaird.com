# Learning playbook — how to build study guides that work

Distilled from six learning-science textbooks (chapter digests in `books/`). Each rule says what to do, why (with the supporting pages), and where it lands in a course build. Page cites use the book's printed pages: **Chance** (Chance & Furlong 2023), **Olson** (Olson & Ramirez 2020), **Mazur** (Mazur & Odum 2023), **Gluck** (Gluck et al. 2016), **Domjan** (Domjan & Delamater 2024), **DeHouwer** (De Houwer & Hughes 2020).

**Evidence note.** These are learning-and-behavior textbooks, mostly about conditioning, memory and skill, not engineering education. Rules marked *(book-backed)* are stated by the books with data; rules marked *(inference)* are our translation of a general principle to a study site. Use the rules as defaults and sanity-check them against what students report.

**Boundary.** None of this overrides the academic-integrity rule in `CLAUDE.md`: the site teaches and drills; it never solves assigned homework, quizzes or take-home tests.

---

## The twelve rules

### 1. Make the learner retrieve, not re-read *(book-backed)*
Writing down everything recalled from a passage beat re-reading it a week later, with or without feedback; failed attempts still help, and short quizzes mid-lecture improved later exam scores, including on untested material (Gluck pp. 278–280). Frequent testing helps from grade school through college and works best with fast feedback; the authors note students rarely self-test, so build it in (Olson pp. 75, 144). Successive relearning to mastery over several sessions boosts long-term retention (Olson p. 230); Chance lists self-testing among seven retention tactics (pp. 382–386).
**Apply:** every unit should end with questions the learner answers *before* seeing the answer (cover-up solution, "write the setup first"). Prefer `problems` and recall prompts over more reading text. Add a "close the page and list the 5 equations/assumptions" step to `know`.

### 2. Give feedback that is immediate, specific and correct *(book-backed)*
Practice without knowledge of results did not improve skill; quantitative feedback beat right/wrong (Gluck pp. 317–318; Mazur pp. 294–296). Delays weaken operant learning and need bridging signals (Domjan pp. 110–111; DeHouwer pp. 119, 142, 164). Correct errors before they are rehearsed (Olson p. 75). Fade support later so the learner builds an internal standard (Mazur pp. 299–301).
**Apply:** solutions show the check (units, limiting case, magnitude) next to each step, not only the final number; wrong-answer explanations name *the specific error* ("used T in °C in the radiation term"). Pair with `pitfalls` so each pitfall is something a problem tests.

### 3. Space it, and revisit old units *(book-backed)*
Distributed practice outperformed massed practice across hundreds of experiments (Olson pp. 133–134); trainees in a spaced schedule needed fewer total hours even though they liked it least, so how studying *feels* is a poor gauge (Gluck p. 319; Mazur p. 307). Spacing trades speed for durability (DeHouwer p. 49), and deadline-driven schedules produce last-minute cramming (Chance pp. 200–202, 221).
**Apply:** put an expanding review schedule on the site (day 1, 3, 7, 14 before each exam) and put 1–2 *earlier-unit* problems into every later unit. Ship cumulative mock exams (`mocks`) in the final week, mixing exam coverage.

### 4. Mix and contrast to teach discrimination *(book-backed)*
Variable or randomly ordered practice produced better later performance despite worse practice scores (Mazur pp. 301–304; Gluck pp. 319–320). Contrasting labelled examples of both categories sharpens boundaries (Gluck pp. 226–227); minimal-difference practice builds fine discrimination (Domjan pp. 219–223); varied examples build concepts and are checked with unseen instances (Mazur pp. 231, 235–237; Chance pp. 329–332).
**Apply:** pair look-alike situations side by side ("steady vs transient conduction", "fin tip adiabatic vs convective") with the single feature that decides the method. Write problem sets that mix methods so the learner must *choose* before computing. `tableGuide`/`mistakes` should be organised by "when to use which".

### 5. Progress worked example → guided → independent *(book-backed + inference)*
Shaping works by reinforcing small steps and raising the bar as the learner succeeds (Chance pp. 173–180; Domjan pp. 107–109; Mazur pp. 112–115). Modelling is a strong channel, especially for hard tasks (Chance pp. 303, 315–317; Olson pp. 350–351, 368), and observe-then-practice beat either alone (Mazur pp. 297–298). Guided discovery beat unaided discovery (Olson p. 310). Early success and controllability protect against helplessness (Mazur p. 172; Chance pp. 193–194).
**Apply:** each unit's `problems` run easy → moderate → exam-like, tagged by difficulty, with a worked example first and later problems with hints that can be revealed one at a time (*inference*). Start the unit at the learner's likely level, not at the book's.

### 6. Build a frame first, then process for meaning *(book-backed)*
A paragraph was recalled about twice as well when its topic was given beforehand (Gluck pp. 274–276), and meaning-based processing beats repetition. Understanding a principle gives flexible knowledge; formula-only learners fail on unfamiliar problems (Olson pp. 280–285). Material pitched between the known and the unknown teaches best (Olson pp. 304, 307–308).
**Apply:** `why` and the unit opener state the one-sentence goal ("this unit answers: how much heat leaves the body per metre of fin?") and connect to the previous unit. Equations (`eq`) come with when-they-apply, not just the formula.

### 7. Practice in the form and context of use *(book-backed)*
Retrieval is best when study and test conditions match (transfer-appropriate processing) and transfer follows shared elements (Gluck pp. 277–278, 328; Olson pp. 68–70, 227–231). Learned performance can fail when context changes (Mazur pp. 98–100); extinction and correction are context-specific and relapse elsewhere (Domjan pp. 159–164; DeHouwer pp. 88, 106). Do not assume transfer: program it with varied examples and settings (Chance pp. 329–332, 343–346).
**Apply:** practice problems should look like the exam (units, data tables, closed-book steps). Vary contexts across problems on purpose (different fluids, geometries, givens). Include one "novel setup" problem per unit that tests transfer.

### 8. Calibrate: do not trust the feeling of knowing *(book-backed)*
Judgments of learning and feelings of knowing run overconfident; students predicted the same recall after a day or a week; few use self-testing (Gluck pp. 288–289). Learning and performance differ — knowledge can sit unexpressed until a payoff appears, so assess with delayed and transfer tasks (Olson pp. 6, 321–322; Mazur pp. 193–194, 286; Domjan pp. 6–7).
**Apply:** add a "predict your score, then check" step to mock exams and a readiness checklist by topic ("could you set this up cold?"). Tell learners explicitly that rereading feels easy and teaches less.

### 9. Respect working memory *(book-backed + inference)*
Working memory holds only a handful of items; chunking, using verbal plus visual channels, and avoiding multitasking help (Gluck pp. 354–356, 382). Mastery-based, small-step, frame-by-frame instruction with frequent responding keeps success high (Chance pp. 269–270; DeHouwer pp. 221–222).
**Apply:** keep each `know` block short and chunked (≈4±1 ideas); one idea per equation panel; diagrams and equations side by side; no wall of text; collapse optional depth (*inference*). Break multi-step problems into labelled steps.

### 10. Motivate with success, signals and small wins *(book-backed)*
Reinforcement works best when immediate and contingent (Chance pp. 133, 147–150); intermittent reward builds persistence but thin it gradually (Chance pp. 200–202; Domjan pp. 124–130); the value of any reward depends on alternatives, and frequent low-stakes quizzes produce steadier studying than rare large exams (Mazur pp. 140–141, 314–318). Self-efficacy grows from moderate goals and success experiences (Olson pp. 354–355, 369). Reinforce effort on hard tasks to build persistence rather than helplessness (Chance pp. 193–194, 263).
**Apply:** progress tracking and checkboxes per unit, visible streaks only for effort (not ranking), brief correct-answer confirmations. Give a study-plan layout that front-loads a quick win each session (*inference*). Avoid punishing language ("you failed") — use specific next steps instead (Chance pp. 247, 252–258; Mazur pp. 174–180).

### 11. Manage emotion and arousal *(book-backed)*
Subjects paired with anxiety or humiliation can become lasting aversions (Olson pp. 203–204; Chance pp. 98–101, 105–108). Moderate arousal and mild stress can help; high or chronic stress impairs recall (Gluck pp. 409–413; Olson pp. 144, 384–385). Graded exposure with calm practice reduces anxiety (Mazur pp. 71–72, 170–171).
**Apply:** a short "test-day routine" and graded exam rehearsal (untimed → timed → closed-book mock); calm, matter-of-fact tone; never alarmist language about exam difficulty. Sleep and breaks are part of the plan (Gluck pp. 3, 330).

### 12. Design the schedule around attention and sleep, and guard against shortcuts *(book-backed)*
Memory loss is usually interference or retrieval failure, not erasure (Mazur pp. 251–261; Domjan pp. 235–239); retrieval changes memories (Domjan pp. 240–241; Gluck pp. 281–288). A dedicated place and time for studying, leaving when off-task, builds stimulus control (Mazur pp. 241–244). Learning styles matching showed no benefit, "brain-based" claims mostly restate older theory (Olson pp. 451–454); music, "brain games" and brain drugs have weak support (Gluck pp. 63, 493, 513).
**Apply:** do not label content as "visual/auditory learner" tracks. Offer multiple representations because they help everyone (diagram + equation + words), not as styles. Keep study blocks short with breaks and a stop point.

---

## Per-unit checklist (before publishing a unit)
- [ ] One-sentence goal and link to the previous unit (rule 6).
- [ ] ≤ 5 chunked ideas in `know`; equations show conditions of use (rules 6, 9).
- [ ] Each pitfall has a problem that triggers it (rules 2, 4).
- [ ] Worked example → guided → independent, with difficulty tags (rule 5).
- [ ] At least one retrieval prompt answered before the solution is visible (rule 1).
- [ ] At least one earlier-unit review problem and one mixed-method problem (rules 3, 4).
- [ ] At least one novel-setup problem and exam-format practice (rule 7).
- [ ] Solutions explain the specific error and the check, with every number computed in Python (rule 2; repo rule).
- [ ] No homework/quiz/test problems solved (integrity rule).

## Course-level checklist
- [ ] Spaced review calendar tied to the exam dates (rule 3).
- [ ] Cumulative mocks late, with predict-then-check (rules 3, 8).
- [ ] Test-day routine and readiness list (rules 8, 11).
- [ ] Progress tracking that rewards effort, not rank (rule 10).

## Where each rule lives in `courses/<id>/`
| Course artifact | Rules |
|---|---|
| `content.py` `why`, `know`, `eq`, `pitfalls` | 2, 4, 6, 9 |
| `problems/*.py` (difficulty tags, mixed order, review items) | 1, 2, 3, 4, 5, 7 |
| `mocks`, `tests` (cumulative, predict-then-check) | 3, 7, 8 |
| `mistakes`, `tableGuide` (when-to-use-which) | 4 |
| Page template: progress, review calendar, test-day routine | 3, 10, 11, 12 |

## Open questions the books do not settle
- How much worked-example support is best for engineering calculation problems (the books give general guidance only; test with real students).
- Optimal spacing intervals for a 3–5 week fast-track course (the books show spacing helps but give no calendar).
- Whether to randomise problem order inside a unit when learners are new to it (variable practice helps later tests but can lower early scores — Mazur pp. 303–304).
