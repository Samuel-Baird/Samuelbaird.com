# Apologetics Hub Ingest — Claude Instructions

The Apologetics Hub (`/apologetics-hub`, gated to accounts with apologist
access) is a feed of critical-channel videos, each with claim-level rebuttals
and sources, so apologist content creators can divide coverage and respond
with good material. There is no scraping cron — ingest is run **manually, in
a Claude Code session**, following this document. When the user asks Claude
to "run the apologetics hub ingest" (or similar), Claude should work through
the five steps below end to end without asking for confirmation at each step,
per the user's standing preference to ship rather than pause for approval.

## Prerequisites

- `.env.local` must have `YOUTUBE_API_KEY`, `NEXT_PUBLIC_SUPABASE_URL`,
  `SUPABASE_SERVICE_ROLE_KEY` set (the app's usual `.env.local`; the ingest
  scripts do not need `SUPABASE_PROJECT_REF`/`SUPABASE_DB_PASSWORD` — those
  are only for schema migrations).
- The session should have these MCPs connected, since claim responses must
  cite real sources through them rather than from memory:
  - **Gospel Scholar Archive** — scholarly volumes, page-level citations.
  - **pulpit-vault** (General Conference corpus) — `verify_quote` before
    repeating any attributed quotation; `search_concordance` for topical
    sourcing.
  - **latter-day-stats** (this site's own MCP) — channel/study context.
- Tracked channels live in `public.channels`. The pilot channel is **Mormon
  Stories Podcast** (`youtube_channel_id` `UCx6OgmoqJbOVRq-Lv1P7SzA`,
  `channel_type = 'Critical'`). Adding another channel to the hub just means
  running the steps below against its `channels` row — no new channel-tagging
  work is required as long as it's already tracked as `Critical`.

## Step 0 — Pick a channel to work on

Every tracked `Critical` channel should get periodic passes, not just the
pilot channel. `public.hub_channel_state` records `last_ingested_at` per
channel — the last time `hub-list-new-videos.ts` scanned it, whether or not
that scan found anything new. Before starting a session, check which tracked
channels are most overdue:

```sql
select c.name, c.slug, hcs.last_ingested_at
from public.channels c
left join public.hub_channel_state hcs on hcs.channel_id = c.id
where c.channel_type = 'Critical'
order by hcs.last_ingested_at asc nulls first;
```

`last_ingested_at` is a per-channel checkpoint, not a per-video one — it
tells you a channel was checked as of that time, so a channel with no new
uploads since its last scan doesn't look identical to one that's never been
scanned at all. `hub-list-new-videos.ts` (below) prints the prior value at
the top of its run and updates it automatically at the end, success or not
— you don't set it by hand.

## Step 1 — Find new videos

```bash
npx tsx scripts/hub-list-new-videos.ts --channel UCx6OgmoqJbOVRq-Lv1P7SzA --out new-videos.json
```

`--channel` accepts a `channels.slug` or a raw YouTube channel id. This scans
the channel's most recent uploads (2 pages / 100 videos by default — raise
with `--pages`), computes a view-count baseline (`expected_views`, the median
of the 15 most recent qualifying uploads — shorts and videos under 14 days
old are excluded), and prints/writes the videos not yet in `hub_videos`.

Optional flags for channels already in the hub:
- `--refresh-stats` — update `view_count` on existing rows for this channel.
- `--mark-removed` — flip rows the API no longer returns to
  `video_status = 'removed'`. Deleted and private videos look identical to
  the public API (both are just absent), so a row flagged `removed` may
  actually be `private` — spot-check before trusting the label at scale.

Read `new-videos.json`. Each entry has `youtube_video_id`, `title`,
`published_at`, `duration_seconds`, `view_count`, `thumbnail_url`, and the
computed `expected_views`. The output also carries `channel.id` — the
`channel_id` value every analysis JSON in step 4 needs.

If the console warns "low-confidence" baseline (fewer than 8 qualifying
videos), either widen `--pages` and rerun, or set `expected_views` by hand in
the analysis JSON with a note in the summary about why.

## Steps 2–5 — run as one per-video loop

Work videos one at a time — fetch a transcript, analyze, write the JSON,
insert — rather than batch-fetching every transcript up front. Analysis
takes 10–30+ minutes per video, so fetching each transcript immediately
before its own analysis spaces the YouTube requests naturally. Batch-fetching
is what triggers YouTube's per-IP "unusual traffic" block: observed
2026-08-12, three transcript fetches in quick succession tripped it, after
which every watch-page request from this machine — browser or script alike —
got HTTP 429 for hours.

## Step 2 — Fetch the transcript

Never fetch transcripts by driving the YouTube watch page in a browser (e.g.
clicking "Show transcript" in the Browser pane): it is the heaviest request
pattern, trips the anti-bot interstitial fastest, and the resulting block is
IP-wide, killing tier 0 for the rest of the session. If an anti-bot
challenge does appear anywhere, never attempt to click through it — solving
it is strictly for the user, by hand, in their own browser.

Work down this ladder. The session's first tier-0 run doubles as the probe
that tells you whether the IP is currently blocked.

**Tier 0 — caption scrape** (lightest: two bare HTTP requests, no external
tools):

```bash
npx tsx scripts/hub-fetch-transcript.ts --video <youtube_video_id> --out <youtube_video_id>.transcript.json
```

Prefers manual English captions, falls back to auto-generated. Its exit code
tells you the next move:

| Exit | Meaning | Next move |
|---|---|---|
| 0 | Transcript written | Continue to step 3 |
| 2 | Video has no captions | Tier 2 — yt-dlp has nothing to download either |
| 3 | Rate-limited (429 / interstitial / empty timedtext body) | **Circuit-break:** skip tier 0 for every remaining video this session; use tier 1 |
| 1 | Anything else (payload shape changed, network error) | Try tier 1 |

**Tier 1 — yt-dlp** (different request path — its Innertube "android" client
kept working while the watch page 429'd, verified 2026-08-12):

```bash
yt-dlp --write-sub --write-auto-sub --sub-lang en --skip-download --sleep-requests 2 -o "<youtube_video_id>" "https://www.youtube.com/watch?v=<youtube_video_id>"
```

then convert the resulting `.vtt` into the transcript-JSON shape:

```bash
npx tsx scripts/hub-fetch-transcript.ts --video <youtube_video_id> --from-vtt <youtube_video_id>.en.vtt --out <youtube_video_id>.transcript.json
```

If yt-dlp itself starts failing, run `yt-dlp -U` first — YouTube churns
these internals constantly. Its "no supported JavaScript runtime" warning is
harmless (installing deno silences it).

**Tier 2 — manual:** watch the video (or the parts around likely claims) and
write the transcript into the JSON by hand, setting `"source": "manual"`.

A transcript fetch failure is **not blocking** — mark the video and keep the
queue moving; analysis can still proceed from watching the video directly
and noting timestamps manually. Always store whatever transcript text is
available (full transcript, private, re-analysis only) even though the hub
UI never renders it.

## Step 3 — Analyze

This is the substantive part of the session. Watch/read the video via the
transcript and produce:

**Relevance** — first decide whether the video actually addresses Latter-day
Saints/Mormonism at all. Not every tracked Critical channel stays on-topic in
every upload — a general Christian-apologetics or ex-high-demand-religion
channel, for instance, may post plenty of videos with nothing to do with the
Church. Set `lds_relevant: false` for those; the video's row, transcript, and
any partial claims are still retained (for the record and so it isn't
rescanned as "new" later), but it's hidden from the public feed. When
`lds_relevant` is `false`, `claims` can be left empty and `debunkability`
omitted — there's nothing here for an apologist to act on. Only set
`lds_relevant: true` and continue to full analysis below when the video does
engage the Church, its doctrine, history, or members.

**Summary** — 2–4 sentences, neutral register. Describe what the video
argues, not whether it's right. No editorializing, no "this dishonest video…".

**Claims** — extract the video's specific, checkable claims (not every
opinion or personal-experience statement — those aren't "debunkable" and
don't belong here). For each:
- `timestamp_seconds` — to the nearest ~10 seconds, taken from the
  transcript segment where the claim starts.
- `excerpt` — a verbatim quote, ≤ ~40 words, taken directly from the
  transcript (do not paraphrase into a quote).
- `claim_summary` — one sentence stating the claim being made.
- `response` — the written rebuttal. Name the specific flaw: false
  dichotomy, presentism, a misquote or missing context, an unsupported
  causal leap, a cherry-picked source, etc. Be specific, not "this is wrong."
- `sources` — **every response must cite at least one source obtained
  through the GSA, pulpit-vault, or latter-day-stats MCPs during this
  session**, not from memory. Use the cite/verify URLs those tools return —
  they open the exact page or paragraph. Run `verify_quote` before repeating
  any attributed General Conference quotation. Each source is
  `{ title, url, note }`, where `note` states what the source shows and the
  specific flaw it exposes — not just a description of the source.

**Debunkability** (1–10) — how worth an apologist's time this video is to
respond to:

| Score | Meaning |
|---|---|
| 1–2 | Subjective / personal-experience territory — don't engage. |
| 3–4 | Contested interpretation without a clear factual error. |
| 5–6 | Misleading framing, but good counter-sources exist. |
| 7–8 | Contains a factual error refutable with primary sources. |
| 9–10 | Demonstrably false, with a document the audience can be shown directly. |

Score the video overall (its weakest defensible claims pull the score up;
purely subjective videos stay low even if popular).

**View ranking** — `expected_views` comes from step 1's baseline (median of
the channel's recent normal-length uploads). Override it by hand only when
you have a specific reason (e.g. the channel just had a viral unrelated
video skew the baseline) — note the reason in the summary if you do.

## Step 4 — Write the analysis JSON

One file per video. Full shape (validated by
`scripts/hub-insert-analysis.ts`):

```json
{
  "channel_id": "1c6d2d1d-823e-4311-b0a9-c504f81a2c5a",
  "youtube_video_id": "dQw4w9WgXcQ",
  "title": "Video title exactly as on YouTube",
  "published_at": "2026-08-01T18:00:00Z",
  "duration_seconds": 5400,
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
  "view_count": 42000,
  "expected_views": 31000,
  "summary": "Two-to-four neutral sentences describing what the video argues.",
  "lds_relevant": true,
  "debunkability": 7,
  "claims": [
    {
      "timestamp_seconds": 1830,
      "excerpt": "Verbatim ~40-word quote from the transcript.",
      "claim_summary": "One sentence stating the claim.",
      "response": "The written rebuttal, naming the specific flaw in the argument.",
      "sources": [
        {
          "title": "Short source title",
          "url": "https://the-mcp-tool-returned-this-exact-url",
          "note": "What the source shows and the flaw it exposes."
        }
      ]
    }
  ],
  "transcript_file": "dQw4w9WgXcQ.transcript.json"
}
```

`transcript_file` points at step 2's output; use an inline `transcript`
object with the same `{ source, transcript, segments }` shape instead if you
wrote one by hand. `channel_id`, `youtube_video_id`, `title`, `published_at`,
`view_count` normally come straight from step 1's `new-videos.json` — copy
them rather than retyping.

## Step 5 — Insert and verify

```bash
npx tsx scripts/hub-insert-analysis.ts <analysis-file.json>
```

The script validates the JSON, computes
`priority_score = (view_count / max(expected_views, 1)) * (debunkability / 10)`,
and upserts `hub_videos` / `hub_claims` / `hub_transcripts`. It prints the
video's hub URL (`/apologetics-hub/<youtube_video_id>`) — open it (as an
apologist or admin account) and check the summary, claim timestamps (the
video should seek correctly), and sources render as expected before
reporting the run done.

## Ingest-stage tags

Every video on the hub feed shows exactly one stage tag, whichever step is
furthest along — not a checklist of completed steps. A video with claims
shows only "AI rankings/claims provided," not also "Metadata ingested" and
"Script ingested." The stage is derived, not hand-set: `hubIngestStage()` in
`src/lib/types.ts` computes it from whether `hub_transcripts` has a row and
whether `hub_videos.analyzed_at`/`debunkability` is set, so it can never
drift out of sync with the actual data.

| Tag | Meaning | Set by |
|---|---|---|
| Metadata ingested | Row exists in `hub_videos` (title, views, thumbnail...); no transcript yet | `hub-list-new-videos.ts` |
| Script ingested | Transcript fetched into `hub_transcripts` | `hub-fetch-transcript.ts` |
| AI rankings/claims provided | Full analysis done — claims, debunkability, priority | `hub-insert-analysis.ts` |

Admin accounts get a stage filter on `/apologetics-hub` (non-admin
apologists don't see the filter, though everyone sees the tags) — useful for
finding exactly what still needs the next pipeline step, e.g. filter to
"Metadata ingested" to see everything still waiting on a transcript.

## Reference

- Schema: `supabase/migrations/0039_apologetics_hub.sql`,
  `0041_hub_channel_state.sql`, `0042_hub_lds_relevant.sql`.
- Access control: `requireApologist()` / `isApologistUser()` in
  `src/lib/permissions.ts`; grant/revoke apologist (and premium, admin)
  status at `/admin/access`.
- Scripts: `scripts/hub-list-new-videos.ts`, `scripts/hub-fetch-transcript.ts`,
  `scripts/hub-insert-analysis.ts`.
- `hub-fetch-transcript.ts` exit codes (0 ok / 2 no captions / 3
  rate-limited / 1 other) and its `--from-vtt` converter mode: see Step 2.
- Priority formula (may evolve — it lives in the insert script, not the
  schema): `(view_count / max(expected_views, 1)) * (debunkability / 10)`.
- `video_status`: `active` | `removed` | `private` — set by
  `--mark-removed` in step 1, not by the analysis JSON.
- `hub_channel_state.last_ingested_at`: per-channel scan checkpoint, see
  Step 0 above.
- `hub_videos.lds_relevant`: set during analysis, see Step 3's Relevance
  section above. Null (not yet analyzed) and `true` both show in the public
  feed; `false` hides the video from the feed while keeping the row,
  transcript, and any claims.
- Ingest-stage tags: see above; derivation lives in `hubIngestStage()` in
  `src/lib/types.ts`.
- Per-creator status (working on it / responded + link) is set from the hub
  UI itself, not by these scripts — see `src/app/actions/hub-status.ts`.
