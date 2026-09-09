# Saint Capybara — research protocol

**Research before advocacy.** No narration line responding to a claim is
written until the claim has been triaged, researched with the tools below,
and graded. This applies even when the "obvious" answer seems well known —
verify it anyway; Saint Capybara's credibility depends on never being
caught having skipped this step.

## 1. Claim triage

Transcribe the source video (`tools/transcribe.py`, unchanged from the rest
of the pipeline). List every discrete claim in `research/claims.md` as a
table:

| # | Timestamp | Verbatim claim | Category | Triage decision | Classification | Chosen? |
|---|---|---|---|---|---|---|

- **Category**: historical-fact / doctrinal / statistical / anecdotal /
  opinion.
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

- **Primary**: the original document/discourse/record itself (Journal of
  Discourses, a diary, an official statement, a scripture text).
- **Scholarly**: peer-reviewed or university-press historical/theological
  work (Gospel Scholar Archive).
- **Official**: current Church statements, handbooks, or newsroom
  material — cite as *current practice/position*, dated.
- **Scripture**: canonical text citation.
- **Dataset**: Latter-day Stats datasets/studies for empirical/statistical
  claims — cite the dataset/study, not a paraphrase of it.
- **Apologetic-lead**: an apologetics site or forum post is a *lead only*
  — it must be traced to (and re-verified against) a primary or scholarly
  source before it can be used on screen. Record `traced_to` in
  `sources.yaml`. Never let an apologetic source be the terminal citation.
- **Critic**: the critic's own clip/video is itself a legitimate `critic`
  source when quoting or characterizing what they said.
- Screenshots are **never** sources — a screenshot of a quote is not
  verification; go to the original.

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

## 7. False-vs-misleading taxonomy

When rebutting a claim, be precise about which of these it is — the
response differs:

- **False** — the claim states something that didn't happen / isn't true.
  Rebut with the primary source that contradicts it.
- **Misleading** — technically true but creates a false impression by
  omission, framing, or decontextualization. Rebut by restoring context,
  not by disputing the literal words.
- **True but out of context** — the quote/fact is accurate; the argument
  built on it doesn't follow. Concede the fact, dispute the inference.
- **True and damaging** — sometimes the honest answer is "yes, that
  happened, and it's a fair thing to raise." Concede it; Saint Capybara's
  credibility depends on not spinning every fact into a win (see
  escalation trigger 6 below).

## 8. Argument construction rules

- **Order**: state the claim fairly (steelmanned) before responding.
- **Burden of proof**: don't demand a critic prove a negative; address
  the actual evidence they cited.
- **Symmetry**: a "same standard?" beat should compare like to like — not
  a weak version of the counterexample against a strong version of the
  original claim.
- **Consistency is support only, not proof**: "this is consistent with X"
  is weaker evidence than "this directly states X" — don't blur the two.
- **Identify the moral principle** being invoked before agreeing or
  disagreeing with how it's applied.

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
<verbatim claim + timestamp>

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
used_on_screen, counter, notes`.

## 14. Adversarial review

Before finalizing `claims.md`, write answers to these two questions for
each claim the video responds to, and revise once if the first pass turns
up something real:

1. "What is the strongest objection a knowledgeable critic could still
   make after this response?"
2. "What did I leave out of the critic's original clip that changes how
   fair this response is?"

Record both answers directly in `claims.md` next to the claim. If the
adversarial pass surfaces a real problem, fix the response and repeat the
pass once more before moving on.
