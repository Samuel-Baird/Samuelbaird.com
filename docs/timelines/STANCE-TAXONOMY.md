# Stance taxonomy

**Status: implemented.** Every quote is categorised against this, and the
three-value model it replaced — one `affirms`/`hedges`/`denies` axis across all
six questions — is gone from both the data and the schema. The field contract
is in [`SCHEMA.md`](./SCHEMA.md); the bands and their criteria also live in
`QUESTIONS` in `constants.ts`, so whoever assigns one is held to the same
written rule the page shows its readers.

The three questions this document once left open were settled when it was
built; each is recorded at the point it applies, and collected under
[Decisions](#decisions-taken).

---

## Why the previous model had to go

**Three values could not hold these questions.** "How many Gods are above the
Father?" has at least four distinct answers, and they are ordered — infinite,
indefinite, finite, none. Collapsing that into affirm/deny throws away the
distinction the corpus actually argues about.

**Divinity and mortality are independent, and the previous model welded them
together.** `FATHER-BECAME-GOD` and `FATHER-MORTAL-EXPERIENCE` are treated as
two ways of saying one thing. They are not. Under this tradition's own
theology, Jehovah was God before and during his mortal life — so "God once was
as man now is" does **not**, by itself, assert that there was a time the Father
was not God. Only *attainment* language does that. A quote can affirm the
mortality and say nothing whatever about the divinity, and many do.

**Heavenly Mother needed a role scale, not an existence scale.** Existence is
close to uncontested here — 49 of 59 quotes affirm it and exactly one denies —
so an existence axis is a flat line. What actually moves over time is how much
doctrinal work she does: required for spirit birth at one end, a capped and
carefully bounded parent at the other.

**So each group gets its own ordered scale.** Some have three bands, some have
five or six. On some, "declines to say" is a genuine midpoint between two
positions; on others it is off-scale entirely and must be drawn apart from the
ordered bands rather than in the middle of them.

---

## Group 1 — Divinity

**Was the Father always God?**

Ordered by commitment to divine becoming. `Declines` is a true midpoint.

| Band | Criteria — tag only if the quote does this | Markers |
|---|---|---|
| **Not always God** | Asserts a state-change into godhood: he *attained*, *became*, *was exalted to*, or *progressed to* being God, or that there was a time he was not God. | "became a God", "attained godhood", "was exalted to" |
| **Declines to say** | Raises the Father's origin or history and explicitly withholds, or is deliberately poised between attainment and eternal divinity. | "we do not know", "it has not been revealed" |
| **Always God** | Asserts the Father has always been God — no beginning to his divinity, no attainment. | "from eternity to eternity", "always was God" |

**Not sufficient on its own:** mortality language, a Father-above-the-Father
claim, or "as man now is, God once was." Those belong to Group 2 or Group 3 and
must be tagged there instead. A quote earns a Group 1 band only for explicit
becoming-or-always language about divinity itself.

---

## Group 2 — Regress

**How many Gods are above the Father?**

Ordered by **strength of the regress claim**, not by number. Indefinite
outranks finite deliberately: leaving the chain open is a stronger commitment
than closing it at a stated point.

| Band | Criteria | Markers |
|---|---|---|
| **Infinite regress** | An explicitly endless or numberless succession of Gods above the Father. | "without end", "endless", "no first", "eternal succession" |
| **Indefinite regress** | A chain above the Father with no stated terminus and no stated count. The default reading of an unqualified "the Father had a Father." | "his Father had a Father", "and so on" |
| **Finite regress** | A bounded chain: a stated count, or a named terminus above the Father. | "a God above him, and above that God…" ending somewhere |
| **Father is the Most High** | Asserts nothing is above the Father — he is the terminus. | "no God above him", "the Most High" |
| **Declines to say** | Raises the question and withholds. **Off-scale**, not a midpoint. | "we are not told what lies beyond" |

**Boundary rule.** An unquantified chain is *indefinite*, never *infinite*.
Promoting it is retrojection, and it is the most tempting error available in
this group — an unbounded-sounding phrase is not a claim about infinity.

---

## Group 3 — Mortality

**Did the Father pass through a mortal life?**

| Band | Criteria | Markers |
|---|---|---|
| **Mortal probation as we are** | A mortality like ours: tested, subject to law, able to fall. A probation, not merely an incarnation. | "as man now is", "passed through mortality", "kept his estate" |
| **Mortal, already divine** | Lived a mortal life *while already God* — the Jehovah pattern. Incarnation without loss of divinity, or explicit comparison to Christ's mortality. | "as Jesus did", "condescended", "dwelt in flesh" |
| **Declines to say** | Raises his mortality and withholds its character. | |
| **Denies mortality** | Asserts the Father never was mortal. | |

**Why the second band exists.** It is the band the current data cannot express.
Today every mortality quote collapses into a plain affirmation, which then
reads as implying he was not God at the time — precisely the inference this
tradition does *not* draw about Christ. Expect several existing placements to
move here on re-reading.

---

## Group 4 — Eternal increase

**Do the exalted become parents of spirit children?**

| Band | Criteria | Markers |
|---|---|---|
| **Literal begetting** | Spirit children are begotten and born of heavenly parents. Procreation stated, not implied. | "begotten", "born of", "spirit children" |
| **Increase, mechanism unstated** | Affirms eternal increase, posterity, or continuation of seed while withholding the mechanism. | "continuation of the seeds", "eternal increase" |
| **Organized, not begotten** | Spirits are organized, adopted, or fashioned from pre-existing intelligence — explicitly *not* begotten. | "organized", "adopted", "intelligences" |
| **Declines to say** | Raises the question and withholds. Off-scale. | |
| **Denies increase** | Denies that exalted beings have spirit posterity at all. | |

---

## Group 5 — Heavenly Mother

**What work does she do?**

Ordered by how much doctrinal weight she carries. Existence survives as the
floor of the scale rather than as the whole question.

| Band | Criteria | Markers |
|---|---|---|
| **Necessary for spirit birth** | She is required for spirit children to exist — a procreative role. Begetting is said to need a mother, or she is named as bearing spirit offspring. | "born of", "mother of our spirits", "no father without a mother" |
| **A parent, mechanism unstated** | Parentage affirmed — we are her children, she is a parent alongside the Father — without asserting how. The "heavenly parents" formula. | "heavenly parents", "we are her children" |
| **Present, role unstated** *(provisional — see open question 3)* | She exists, or is a consort or exalted wife, with no claim about parentage or generation. | "a wife", "an exalted woman" |
| **Role capped** | Grants her, then explicitly restricts what follows: no speculation, no worship, no inference beyond what is given. | "we do not pray to her", "little has been revealed" |
| **Declines to say** | Raises her and withholds entirely. Off-scale. | |
| **Denied** | Denies her, or denies the specific role proposed. | |

**Boundary rules**

- **A rebuke of a practice is a cap, not a denial.** Cannon's 1895 objection
  targets addressing her in prayer and the fitness of a hymn; that restricts her
  role, it does not deny her. Under an existence scale this case was genuinely
  hard to place, and the role framing absorbs it without special pleading —
  which is some evidence the framing is right.
- **"Heavenly parents" alone never reaches the top band.** It affirms
  parentage, not mechanism. Promoting it is the same error as reading an
  unquantified chain as infinite.
- **Independent of Group 4.** "Do the exalted beget spirit children?" and "is
  she required for it?" are different questions. A quote can affirm literal
  begetting without naming a Mother at all, and can affirm "heavenly parents"
  with no mechanism anywhere. Tag each group on its own evidence.

**Deliberately excluded.** Whether she may be *worshipped* is a different axis
from what she does in the plan, even though capping statements often bundle the
two. If it needs tracking it should become its own group; folded in here it
would stop the scale being ordered.

---

## Group 6 — Divine progression

**Does God still progress?**

| Band | Criteria | Markers |
|---|---|---|
| **Progresses in knowledge** | God advances in knowledge, truth, or perfection. The strong claim. | "progressing eternally", "learning" |
| **Progresses in dominion only** | Explicitly restricts progression to glory, dominion, or kingdoms while denying growth in knowledge. | "only in dominions", "not in knowledge" |
| **Declines to say** | Raises it and withholds. Off-scale. | |
| **Denies progression** | God possesses all knowledge and does not advance. | "knows all things", "cannot increase" |

---

## Where the existing categories land

| Category | Group | Notes |
|---|---|---|
| `FATHER-BECAME-GOD` | 1 | **Must be re-read.** Currently conflates becoming with mortality. |
| `FATHER-ALWAYS-GOD` | 1 | All four current uses are complicated; expect movement. |
| `BACKWARD-AGNOSTIC` | 1 or 2 | Ambiguous today — see open question 1. |
| `BACKWARD-EXPLICIT` | 2 | Defaults to **indefinite**, not infinite. |
| `INFINITE-CHAIN` | 2 | "Infinite" only where explicitly endless; otherwise demote to indefinite. |
| `FATHER-MORTAL-EXPERIENCE` | 3 | Splits across the probation and already-divine bands. |
| `FORWARD-EXPLICIT` | 4 | Literal begetting. |
| `FORWARD-EUPHEMISM` | 4 | Increase, mechanism unstated. |
| `SPIRIT-BIRTH-VIVIPAROUS` | 4 | Literal begetting. |
| `SPIRIT-BIRTH-ADOPTION` | 4 | Organized, not begotten. |
| `HEAVENLY-MOTHER` | 5 | Needs the full role split; currently 49 affirm / 9 hedge / 1 deny. |
| `DIVINE-PROGRESSION` | 6 | Needs the knowledge/dominion split. |
| `MANY-WORLDS`, `TRIPARTITE-FRAMEWORK`, `RETREAT-REFRAME` | — | Descriptive only; no stance, as today. |

**Two bands have no tag at all:** *finite regress* and *Father is the Most
High*. Both need either new categories or — better — the stance value carrying
the resolution, so that a category only says which question a quote bears on.

---

## The structural change this implies

Today a category carries much of the meaning and the stance adds a direction,
which is why a five-band scale cannot be expressed. The taxonomy above wants
the inverse: **the question owns an ordered scale, and categories only say
which questions a quote bears on.**

That also disposes of the awkwardness introduced when subjects began to
overlap — a category's recorded direction currently means whatever its
*defining* subject says it means, and a narrower subject may only borrow it
where the reading survives. With scales owned by questions, a quote simply has
a band per question it addresses, and nothing has to be reinterpreted.

## Decisions taken

**`BACKWARD-AGNOSTIC` raises both divinity and regress.** Splitting the tag by
which question is being declined would have presumed the answer, and sources
that decline are rarely that tidy. Each question is answered separately, and a
quote may decline one while saying something definite about the other.

**Off-scale answers are drawn apart.** Declining to say is a rung between "not
always God" and "always God", so on that question it sits in the middle. It is
not a rung between an infinite regress and none, so everywhere else it is drawn
below a dashed rule rather than inside the scale. Drawing both boundaries alike
would imply an order that is not there.

**"Present, role unstated" was kept.** It is thin, and the temptation was to
merge it into "Role capped". But capping is a deliberate act — granting her and
then closing the subject — while saying nothing further is just silence. Fusing
them would recreate exactly the kind of conflation this taxonomy exists to
remove, and a band that stays near-empty is itself a finding about the record.

## What it cost

A re-read, not a relabel — 610 answers across 524 quotes, assigned from the
excerpts again rather than translated from the old field. Everything recorded
under the previous model was discarded, including the placements it had flagged
for review, because a fused question cannot be mechanically split.
