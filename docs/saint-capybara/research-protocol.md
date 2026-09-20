# Saint Capybara — research protocol

**Research before advocacy.** No narration line responding to a claim is
written until the claim has been triaged, researched with the tools below,
and graded. This applies even when the "obvious" answer seems well known —
verify it anyway; Saint Capybara's credibility depends on never being
caught having skipped this step.

## 1. Claim triage

Get the source into anchorable form first. **Video:** transcribe it
(`tools/transcribe.py`, unchanged from the rest of the pipeline).
**Article:** ingest the text (`tools/capy_ingest.py --article-file`) so
`source/source.md` carries numbered paragraphs (`¶1`, `¶2`, …) and
`source/source_info.json` pins the text's sha256 and archive URL — the
paragraph numbers are the anchors. Then list every discrete claim in
`research/claims.md` as a table:

| # | Anchor | Verbatim claim | Category | Audience | Triage decision | Classification | Chosen? |
|---|---|---|---|---|---|---|---|

- **Anchor**: `m:ss–m:ss` for a video source; `¶12` or `¶4–¶5` for an
  article. Before a claim is chosen, read the anchor's neighbours in full
  (the ±10s around a clip; the paragraphs on either side of an excerpt)
  and record that in the per-claim notes as "Anchor context" — an
  excerpt must not change meaning once its neighbours are read.
- **Category**: historical-fact / doctrinal / scriptural-textual /
  statistical / philosophical / anecdotal / opinion.
- **Audience**: catholic / protestant / exmo / atheist / media / general —
  see `apologetics-playbook.md`'s audience-specific playbooks. Infer from
  the source if not obvious; note the inference rather than blocking on
  it. Sec 15 below keys its researcher-roster mapping on this column.
- **Triage decision**: respond / concede / skip (with a one-line reason —
  "already well covered elsewhere," "too minor to matter," "unverifiable
  either way").
- **Classification**: fact / inference / disputed / speculation (see
  grading below) — filled in after research, not before.
- **"Does it need defending?" checklist**, applied to every claim before
  deciding to respond to it:
  - Is it actually false, or just uncomfortable?
  - Is it already well-documented and undisputed (in which case: concede,
    don't relitigate)?
  - Would responding require distorting nuance to "win"?
  - Is there a genuinely stronger, more honest response than the obvious
    reflexive one?

## 2. Source hierarchy

See also `docs/saint-capybara/apologetics-playbook.md` "Source hierarchy
— quote upstream" — the on-screen citation should match the audience
(a Catholic source for a Catholic dialogue, Calvin/Reformed confessions
for a Calvinist one) and should be the upstream primary/scholarly source
an apologetic lead pointed to, not the lead itself.

- **Primary**: the original document/discourse/record itself (Journal of
  Discourses, a diary, an official statement, a scripture text).
- **Scholarly**: peer-reviewed or university-press historical/theological
  work (Gospel Scholar Archive).
- **Official**: current Church statements, handbooks, or newsroom
  material — cite as *current practice/position*, dated.
- **Scripture**: canonical text citation. **Bible quotations use the NRSVue
  (New Revised Standard Version, Updated Edition) by default** — record the
  translation in the source's `quote`/citation (e.g. "John 3:16 (NRSVue)"). Use
  another translation only when the claim turns on it (a KJV-dependent Book of
  Mormon parallel, a specific rendering an opponent relies on, the JST) and
  label it on screen. Never quote from memory: confirm the NRSVue wording
  before it goes in a card or excerpt.
- **Dataset**: Latter-day Stats datasets/studies for empirical/statistical
  claims — cite the dataset/study, not a paraphrase of it.
- **Apologetic-lead**: an apologetics site or forum post is a *lead only*
  — it must be traced to (and re-verified against) a primary or scholarly
  source before it can be used on screen. Record `traced_to` in
  `sources.yaml`. Never let an apologetic source be the terminal citation.
  **Named go-to leads (2026-09-13):** FAIR Answers
  (`fairlatterdaysaints.org` — prefer the Gospel Scholar Archive's mirror
  under `Read/Articles/FAIR/FAIR/…`, searchable with `search_concordance`
  and citable with `cite_page`, over the live wiki), Scripture Central
  KnoWhy (`scripturecentral.org`), Evidence Central
  (`evidencecentral.org`), and the Interpreter Foundation *website*
  (`interpreterfoundation.org` — the *journal*, when it's in the GSA, is
  `scholarly`, not a lead). **Chase the footnote, not the page**: a lead's
  value is the citation trail inside it, not its own prose. The traced
  entry itself must be `inspected: true` this run — a lead pointing at an
  uninspected source is still unusable on screen. `tools/capy_merge_briefs.py`
  and `tools/capy_check_sources.py` both enforce this mechanically: an
  entry whose `locator`/`verification.link` is one of these hosts must be
  `type: apologetic-lead` with `quote: null`, and its `traced_to` must
  resolve to an inspected, upstream `primary/scholarly/official/scripture/
  dataset` entry — never to another lead, a critic entry, or nothing at
  all.
- **Critic**: the critic's own clip/video — or, for an article source,
  the article's own text in `source/source.md` — is itself a legitimate
  `critic` source when quoting or characterizing what they said. An
  article project records it as the `type: critic` entry with
  `source_kind: article`, `locator: source/source.md`, `url`,
  `archive_url`, and `quote: null`; `excerpt` beats are validated
  verbatim against `source.md` (sha256-pinned at ingest), never against a
  `quote` field.
- Screenshots are **never** verification — a screenshot of a quote is
  not a source; go to the original. Separately, the on-screen *receipt*
  for an article is a rendered pull-quote (an `excerpt` beat drawn from
  the hashed, archived text), not a browser screenshot — browser
  screenshots stay banned for desktop-chrome/anonymity reasons
  (`brand.md` sec 9-10).

## 3. Tool map

- **Pulpit** (`mcp__2b2805da...`) — General Conference corpus,
  1830–present. `search_concordance` to find talks/paragraphs mentioning a
  term; `read_paragraphs` for full context; `talks_by_speaker` to check
  what a specific leader has said over time; **`verify_quote` before any
  attributed quotation from Conference is used on screen.** A
  `not-verbatim` or `not-found` verdict forbids on-screen attribution as a
  direct quote — paraphrase instead, or drop it. Cite with the tool's
  returned paragraph-level link every time.
- **Gospel Scholar Archive** (`mcp__3302d05e...`) — 7,000+ scholarly
  volumes, page-searchable. `search_concordance` to find candidate pages;
  `read_pages` for context; `cite_page` for the exact citation string;
  `get_page_image` for a clean receipt image (this is the only acceptable
  source of an on-screen "page photo" — never a raw screenshot of a PDF
  reader or search result page, which would leak desktop chrome).
- **Latter-day Stats** (`list_datasets`/`get_dataset`/`list_studies`/
  `get_study`) — institutional baselines for empirical/statistical claims
  (retention, membership, activity rates, etc). Cite the dataset/study id
  and its own methodology notes; do not extrapolate beyond what the study
  actually measured.
- A transcript-search / "RestoredTruth" style MCP, if present in a given
  session, is a **lead only** — same rule as apologetic sources: trace and
  re-verify before it's used on screen.
- **Apologetic leads** (FAIR Answers, Scripture Central KnoWhy, Evidence
  Central, Interpreter Foundation website) — sec 2's named go-to sites.
  Fetch with `WebFetch`, or (for FAIR) prefer the Gospel Scholar Archive
  mirror via `search_concordance`/`read_pages`/`cite_page`. Use only to
  find a footnote to chase upstream; record the lead itself as
  `type: apologetic-lead` with `traced_to` set, never as the terminal
  citation.
- **Article text** — fetch the page with the agent's own WebFetch (or
  have the user paste it, for paywalled pieces) into a cleaned, blank-line
  separated text file, then `capy_ingest.py --article-file cleaned.md
  --article-url URL`. `--article URL --fetch` (requests + trafilatura from
  this machine) and `--archive auto` both contact the publisher /
  archive.org from the home IP — opt-in only; prefer `--archive-url` with
  a Wayback capture made from the separate publishing browser profile.

## 4. Evidence grading

Every claim gets one of four gradings in `claims.md`/`sources.yaml`
(`grade_supports`):

- **Fact** — directly verified against a primary source, no reasonable
  dispute about what the record says (dispute about *interpretation* is a
  separate axis, see below).
- **Inference** — a reasonable reading of verified facts, not itself
  directly stated in a source; say so explicitly on screen ("the record
  doesn't say why, but a reasonable inference is...").
- **Disputed** — credible historians/scholars disagree about the facts or
  their interpretation; present both readings, don't pick a side dressed
  as settled fact.
- **Speculation** — neither side has strong evidence; say so plainly and
  don't dress it up as more certain than it is.

## 5. Doctrine-vs-opinion tiers

Never say "the Church teaches X" without specifying which of these tiers
X actually sits in, and dating it:

1. **Scripture** — canonical text.
2. **Official statement** — a formal, current Church statement or
   newsroom release.
3. **Current handbook/practice** — what is actually practiced/taught now,
   per the current General Handbook or equivalent.
4. **Leader teaching** — a specific leader's talk or writing, dated and
   attributed to them, not the institution.
5. **Older historical belief** — something taught or widely believed in
   the past that is not current practice/teaching; use past tense and the
   actual historical period, never present tense.
6. **Individual speculation** — a member's or leader's personal opinion,
   never institutional.

**Tiers 4-6 are never "the Church teaches."** Date every teaching cited.
No retroactive vocabulary — don't describe a 19th-century belief using a
term or framing that didn't exist or wasn't used at the time.

## 6. Quotation verification procedure

For every quotation that will appear on screen or be spoken as an
attributed quote:

1. Find the original (not a secondary paraphrase).
2. Confirm exact wording, including punctuation that changes meaning.
3. Confirm date and speaker/author.
4. Read enough surrounding context (±context) to know whether the quote is
   being used fairly.
5. Confirm authenticity via the tool's verification mechanism
   (`verify_quote` for Conference talks; `cite_page`/`read_pages` context
   check for GSA).
6. Record the verification in `sources.yaml`'s `verification` field:
   `{tool, verdict, link}`.

### 6a. User-asserted verification override (2026-09-11 user direction)

The user owns this project and may personally vouch for a source the agent's
own tools cannot confirm — a print/microfilm record with no digital copy, a
scan an OCR pass can't read, a paywall/anti-bot block, a site that refuses
automated fetches, etc. This is a real gap: agent tooling fails in ways that
don't mean the underlying fact is false.

**How this works — flag, don't hide:**

1. **The agent still attempts independent verification first**, every time,
   using every tool available (Pulpit/GSA, WebSearch/WebFetch, the Browser
   MCP, direct primary-source lookup). This override is a fallback for when
   those attempts fail, not a shortcut around trying.
2. **If the agent can't confirm it, ask for a source once** (a link, a
   citation, a page number) — the user may have one and forgot to include
   it.
3. **If the user says they've personally verified it and doesn't want to
   dig up a link, proceed on their word** — but record it honestly in
   `sources.yaml`:
   ```yaml
   verification:
     tool: "user-asserted"
     verdict: "unconfirmed-by-agent (user states personally verified)"
     link: null
   notes: "Agent could not independently confirm -- attempted: <what was
     tried and why it failed>. Included on the user's explicit direction as
     project owner."
   ```
4. **This flag must never be silently dropped.** It stays visible in
   `claims.md` and `sources.yaml` through Gate A, so the user sees at
   review time exactly which claims rest on their word alone versus
   independent confirmation, and can change their mind before anything
   ships.
5. **This does not weaken the sensitive-topics rules (sec 11) or lower the
   bar for a first attempt at verification** — it only changes what happens
   after a genuine, documented tooling failure. Escalation trigger #2 ("a
   load-bearing quote that cannot be verified") is satisfied by this
   flagged-override path instead of blocking indefinitely, once the user
   has explicitly chosen to override for that specific claim.

## 7. False-vs-misleading taxonomy

When rebutting a claim, be precise about which of these it is — the
response differs:

- **False** — the claim states something that didn't happen / isn't true.
  Rebut with the primary source that contradicts it.
- **Misleading** — technically true but creates a false impression by
  omission, framing, or decontextualization. Rebut by restoring context,
  not by disputing the literal words.
- **True but out of context** — the quote/fact is accurate; the argument
  built on it doesn't follow. State the fact and dispute the inference in
  the same beat — never a standalone concession beat with the rebuttal
  left implicit or deferred to a later beat.
- **True and damaging** — sometimes the honest answer is "yes, that
  happened." State it plainly (never deny a verifiable fact — Saint
  Capybara's credibility depends on that), but pair it immediately with
  the strongest available mitigating context, positive counter-evidence,
  or explanatory frame the research actually supports — don't let the
  claim stand alone as a concession. **If genuinely no defensible
  reframing exists for a load-bearing claim, that is escalation trigger 6
  below** — a design question for the user, not something to resolve by
  either spinning the fact or leaving it unanswered on screen.

## 8. Argument construction rules

**2026-09-09: Saint Capybara argues to win the argument on the merits,
not to stay neutral between it and the critic's framing — see
`brand.md` sec 2 for the full tone rewrite. These rules govern how, not
whether, to make that case rigorously.**

- **Order**: state the claim fairly (steelmanned) before responding —
  this still comes first even when the response ends up firm; a fair
  statement of the criticism is what makes a firm rebuttal credible, not
  a hedge against one.
- **Test the premise before answering it**: ask whether the claim's
  underlying assumption is even true before evaluating what follows from
  it — often the fastest route to "this doesn't survive contact with the
  record" is showing the premise doesn't hold, not just contesting the
  conclusion.
- **Burden of proof**: don't demand a critic prove a negative; address
  the actual evidence they cited.
- **Symmetry / double standards**: a "same standard?" beat should compare
  like to like — not a weak version of the counterexample against a
  strong version of the original claim — and when the critic is applying
  an inconsistent standard, name that directly rather than only noting
  the asymmetry exists.
- **Consistency is support only, not proof**: "this is consistent with X"
  is weaker evidence than "this directly states X" — don't blur the two,
  and don't let a claim graded `disputed` or `speculation` in `sources.yaml`
  get argued as if it were `fact` just because the conclusion favors the
  LDS position — the tone can be confident, the grading still has to be
  honest.
- **Identify the moral principle** being invoked before agreeing or
  disagreeing with how it's applied.
- **When the research supports it, argue the positive case, not just the
  rebuttal**: after showing where a criticism fails or overreaches, ask
  whether the LDS position explains the same evidence better — with
  fewer special exceptions, more coherently, or more consistently with
  the historical record — and say so plainly if it does. Don't stop at
  "the criticism fails" when "and here's why the LDS reading is
  stronger" is actually supported by what was found; see `brand.md` sec 2
  for the five-step shape this usually takes.

## 9. Analogy rules

Analogies are a comprehension aid, never evidence. Use sparingly, name
where the analogy breaks down, and never on a sensitive topic (see below).

## 10. Institutional-baseline rule

When a claim implies "the Church is uniquely X" (e.g. uniquely
high-control, uniquely wealthy, uniquely secretive), check whether an
institutional baseline (Latter-day Stats, or a comparable-institution
figure from a scholarly source) supports "uniquely" or just "also." Don't
imply uniqueness the data doesn't support, and don't manufacture a
whataboutism where none is warranted either — state what the comparison
actually shows.

## 11. Sensitive-topic handling

Topics requiring extra care: violence, abuse, death, historical
persecution (of or by members), racial history, polygamy's lived
consequences, mental-health-adjacent claims, and anything involving a
named living person's conduct. Rules:

- Facts and harm first — do not lead with a defensive reframe.
- No analogies.
- No `amused` or `happy` poses anywhere in the video (`sensitive: true`
  enforces this via `capy.poses.SENSITIVE_FORBIDDEN`).
- Do an "affected-person pass": before finalizing, ask "if someone
  personally affected by this watched it, would they feel the harm was
  taken seriously?"

## 12. Escalation triggers — stop and write `research/ESCALATION.md`

Any of these **blocks that specific claim/beat** (not necessarily the
whole video — other claims can proceed) until the user weighs in:

1. Substantial source conflict between credible sources that can't be
   resolved by better research.
2. A load-bearing quote that cannot be verified.
3. An allegation against a living, named person.
4. An especially sensitive topic (see above) where getting the tone wrong
   would cause real harm.
5. Evidence that requires heavy interpretation to support the response
   (i.e. the "fact" is really an inference dressed up).
6. A claim that turns out to be true and is only concedable, not
   rebuttable — flag this as a *design* question (should the video even
   include this claim, or pivot to "here's the honest answer") not just a
   research dead end.
7. A lint failure that can't be fixed without either dropping the claim or
   getting user input (e.g. the only available source is apologetic-only
   and cannot be traced further).

`ESCALATION.md` template:

```markdown
# Escalation: <slug>

## Claim
<verbatim claim + anchor (m:ss–m:ss or ¶n)>

## Trigger
<which of the 7 triggers, and why>

## What was found
<sources checked, what they show, where they conflict/fail>

## Options
<2-3 concrete ways to proceed, with tradeoffs>

## Blocking
This claim/beat is blocked pending your input. [Rest of the video may / may
not proceed independently -- state which.]
```

An `ESCALATION.md` file present in `research/` blocks Gate A for the
affected beat(s) — the project cannot be presented as "ready for review"
while one is open and unresolved.

## 13. Source-record rules (`research/sources.yaml`)

One entry per source actually consulted, whether or not it ends up cited
on screen (unused sources are kept — `capy_check_sources.py` reports them
as info, not an error, since "researched but decided not to use" is a
legitimate outcome). Fields — see
`assets/saint-capybara/templates/sources.yaml` for the schema with
comments: `id, type, title, author, date, locator, accessed, inspected,
inspected_via, quote, verification, grade_supports, traced_to,
used_on_screen, counter, notes`. Optional, for article sources:
`source_kind` (`video` default | `article`), `url`, `archive_url`,
`publication`. `capy_check_sources.py` requires the responded-to
article's `critic` entry to carry `url` (error) and `archive_url`
(warning; `--strict` error), and reports `quote:` set on it as a warning
since excerpts are checked against `source/source.md` instead.

## 14. Adversarial review

Before finalizing `claims.md`, write answers to these two questions for
each claim the video responds to, and revise once if the first pass turns
up something real:

1. "What is the strongest objection a knowledgeable critic could still
   make after this response?"
2. "What did I leave out of the critic's original clip that changes how
   fair this response is?"
3. (Added 2026-09-13.) "Where does the standard the critic is applying,
   applied consistently, cut against the critic's own tradition — a
   canon, a confession, a council, a dated statement, their own
   scholarship?" This is the **turnabout**: the raw material for the
   script's one permitted jab (`apologetics-playbook.md`, "Sharpness").
   "None found" is an acceptable answer; a forced one is not.

Record all three answers directly in `claims.md` next to the claim
(`Turnabout:` line). If the adversarial pass surfaces a real problem, fix
the response and repeat the pass once more before moving on.

**When `/capy-research` (sec 15) was used for a claim**, these answers
are not self-assessed — they are seeded by the `capy-red-team` subagent's
independent brief ("Strongest objection after the response," "Omitted
from the clip," and "Turnabout" sections) and pasted into `claims.md` by
the orchestrator.
The orchestrator still owns the "fix and repeat once" step: if the
red-team brief surfaces a real problem, fix the response and re-check
before moving on, same as a self-assessed pass would. For a claim
researched without the fan-out (rare — e.g. a trivial concede-only claim),
this section's original self-assessed procedure still applies.

## 15. Multi-angle research (`/capy-research`)

For every claim triaged `Chosen: yes`, research it from 2-3 independent
expert angles plus an always-on adversarial angle, run in parallel as
Claude Code subagents, rather than one agent researching and self-checking
alone. This section is the roster, the mapping from claim category to
roster, and the contract between a researcher subagent and the orchestrator
(the main session) that merges their output. The skill that runs this
procedure is `.claude/skills/capy-research/SKILL.md` (invoke as
`/capy-research`); the subagent definitions are `.claude/agents/capy-*.md`.

### Roster

- **capy-historian** — primary documents, dating, what contemporaries
  understood, what has been exaggerated (the historical-controversy
  formula from `apologetics-playbook.md`).
- **capy-scripture-theologian** — biblical text in context, early-Christian
  parallels, Catholic/Protestant interpretive-framework analysis, and
  Book of Mormon/JST textual questions.
- **capy-doctrine-scholar** — what LDS leaders have actually taught over
  time (Pulpit), current handbook position, the sec 5 doctrine tier + date.
- **capy-philosopher** — evidential/philosophical argument structure,
  double standards, epistemic-standard analysis for atheist/ex-Mormon
  trust objections.
- **capy-data-analyst** — Latter-day Stats datasets/studies for
  statistical claims and "uniquely X" baseline comparisons (sec 10).
- **capy-red-team** — always runs, on every chosen claim, regardless of
  category. Picks a persona (catholic / protestant / exmo / atheist /
  secular-journalist / believing-member) and argues the critic's case
  *better than the critic did*; its brief seeds sec 14's two adversarial
  questions.

### Category → roster mapping (red-team always added; hard cap 3 researchers + red-team)

| Category | Always | + if catholic/protestant | + if exmo | + if atheist | + if numbers / "uniquely X" |
|---|---|---|---|---|---|
| historical-fact | historian, doctrine-scholar | scripture-theologian | — | — | data-analyst |
| doctrinal | doctrine-scholar, scripture-theologian | — | historian (if "changed over time") | philosopher | — |
| scriptural-textual | scripture-theologian, historian | — | — | — | — |
| statistical | data-analyst, historian | — | doctrine-scholar (if about practice) | — | — |
| philosophical | philosopher, scripture-theologian | — | historian (trust claims) | — | — |
| anecdotal | historian only | — | — | — | — |
| opinion (respond) | doctrine-scholar only | — | — | — | — |

Concede/skip claims get no fan-out. A typical video (2-3 chosen claims)
launches roughly 6-12 subagents total, in one parallel batch.

### The brief contract

A researcher subagent never writes to `sources.yaml`, `claims.md`, or
`ESCALATION.md` directly — it writes one file,
`research/briefs/claim<N>-<role>.md`, and returns a ≤200-word summary to
the orchestrator. This exists because an earlier ad-hoc use of a research
subagent produced `sources.yaml` entries marked `inspected: true` with
`inspected_via: "Research agent WebFetch"` — the orchestrator trusted the
subagent's word instead of the subagent's own tool-verified provenance
being checked. Every agent definition carries the rule explicitly: a
source may be marked `inspected: true` only if the agent itself opened it
with a tool (`read_paragraphs`, `verify_quote`, `read_pages`, `cite_page`,
`get_dataset`/`get_study`, `WebFetch`) in that run; anything recalled from
memory goes under "Could not verify" with `inspected: false`.

`tools/capy_merge_briefs.py --project <dir>` is the only thing that ever
writes a brief's sources into `sources.yaml`. It re-validates
`inspected_via` against a list of real tool-name patterns (a vague phrase
like "research agent" does not pass), requires a `verification.link` or
`verify_quote`/`cite_page` tool for any set `quote`, refuses `type: critic`
unless the id is the real `critic-article` entry (so a researcher-added
entry can't get picked up first by `find_critic_article_entry`'s
first-match logic in `capy_check_sources.py`), and **appends** rather than
prepends to `sources.yaml`. Anything that fails validation is imported
anyway, but with `inspected: false` — `capy_check_sources.py`'s existing
"not inspected" error then blocks citing it until someone actually
verifies it. See the brief's required section structure in each
`.claude/agents/capy-*.md` file, or `.claude/skills/capy-research/SKILL.md`.

### Merging into claims.md

The orchestrator reads each claim's brief files (not all of them at once —
one claim's worth at a time) and fills in Research / Grading (most
cautious grade when briefs disagree, with the disagreement noted) /
Doctrine tier / the two adversarial questions (from the red-team brief) /
a `Briefs:` line listing the files used. An unresolvable grade
disagreement is sec 12 trigger 1; a brief with `status: blocked` also
escalates. `tools/capy_check_sources.py` must still pass on the merged
`sources.yaml` before `beats.yaml` is written.
