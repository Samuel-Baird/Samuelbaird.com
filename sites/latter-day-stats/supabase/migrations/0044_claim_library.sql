-- Claim Library: the public face of the Apologetics Hub's work.
--
-- The hub (0039) produces per-video rebuttals, but the same criticism recurs
-- across many videos and many channels. `claims` is the deduped, canonical
-- form: one claim, stated at its strongest, answered once, with every citation
-- verified during a hub ingest session. A hub_claim is a per-video artifact;
-- a claim is the durable public record it feeds.
--
-- RLS posture differs deliberately from the hub's blanket deny-all:
--   * claims             — public read, but only where status = 'published'
--                          (same "for select using (...)" shape as studies in
--                          0001, narrowed by status). Drafts stay invisible
--                          until an apologist publishes them.
--   * claim_occurrences  — deny-all, like every hub table. It links a claim to
--                          the critical videos that made it; publishing that
--                          mapping would hand those videos traffic and invite
--                          brigading. The public page renders only a
--                          server-computed aggregate ("documented in N videos
--                          across M channels since YYYY").
-- Writes to both go through createSupabaseServiceClient() behind
-- requireApologist(), matching every other hub write path.

-- ============================================================================
-- claims  (canonical, deduped, publicly readable when published)
-- ============================================================================
create table if not exists public.claims (
  id uuid primary key default gen_random_uuid(),
  slug text not null,
  -- Short question-or-assertion headline, e.g. "Did Joseph Smith use a seer
  -- stone to translate?" — this is what the index lists and search matches.
  title text not null,
  -- The criticism stated at its strongest, in the critic's own terms. Kept
  -- separate from `response` so the steelman is a first-class field an editor
  -- has to fill, not a rhetorical throat-clear inside the answer.
  claim_text text not null,
  -- Markdown. Rendered as plain paragraphs today; the column does not care.
  response text not null,
  status text not null default 'draft'
    check (status in ('draft', 'published')),
  topic_tags text[] not null default '{}',
  -- [{ title, url, note }] — same shape as hub_claims.sources (0039), which
  -- is where these are copied from at promote time. jsonb for the same reason:
  -- sources are only ever read alongside their claim.
  sources jsonb not null default '[]'::jsonb
    check (jsonb_typeof(sources) = 'array'),
  -- A response video by the site owner or another apologist, when one exists.
  response_video_url text,
  published_at timestamptz,
  created_by uuid references public.profiles(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  -- A published claim must cite something. This is the publish gate expressed
  -- in the schema, so a bad write fails at the database rather than relying on
  -- the server action alone — the same belt-and-braces reasoning as the zod
  -- gate on timeline sources.json failing the build.
  constraint claims_published_needs_sources check (
    status <> 'published' or jsonb_array_length(sources) > 0
  ),
  constraint claims_slug_format check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$')
);

create unique index if not exists claims_slug_idx on public.claims (slug);
create index if not exists claims_status_idx on public.claims (status);
create index if not exists claims_published_at_idx
  on public.claims (published_at desc nulls last);
create index if not exists claims_topic_tags_gin_idx
  on public.claims using gin (topic_tags);

drop trigger if exists claims_set_updated_at on public.claims;
create trigger claims_set_updated_at
  before update on public.claims
  for each row execute function public.set_updated_at();

-- Full-text search over the public fields, mirroring studies_search_tsv
-- (0009): a trigger-maintained tsvector rather than a generated column,
-- because to_tsvector isn't immutable enough for one.
alter table public.claims
  add column if not exists search_tsv tsvector;

create or replace function public.claims_search_tsv_refresh()
returns trigger
language plpgsql
as $$
begin
  new.search_tsv :=
    to_tsvector(
      'english'::regconfig,
      coalesce(new.title, '') || ' ' ||
      coalesce(new.claim_text, '') || ' ' ||
      coalesce(new.response, '') || ' ' ||
      coalesce(array_to_string(new.topic_tags, ' '), '')
    );
  return new;
end;
$$;

drop trigger if exists claims_search_tsv_trg on public.claims;
create trigger claims_search_tsv_trg
  before insert or update of title, claim_text, response, topic_tags
  on public.claims
  for each row execute function public.claims_search_tsv_refresh();

create index if not exists claims_search_tsv_idx
  on public.claims using gin (search_tsv);

-- ============================================================================
-- claim_occurrences  (which tracked videos made this claim; private)
-- ============================================================================
create table if not exists public.claim_occurrences (
  id uuid primary key default gen_random_uuid(),
  claim_id uuid not null references public.claims(id) on delete cascade,
  video_id uuid not null references public.hub_videos(id) on delete cascade,
  -- The specific hub_claim this occurrence was promoted from, when it came
  -- from one. Null is legal: an apologist can record that a video makes a
  -- claim without a full per-video claim row existing for it.
  hub_claim_id uuid references public.hub_claims(id) on delete set null,
  timestamp_seconds integer check (timestamp_seconds >= 0),
  created_at timestamptz not null default now(),
  unique (claim_id, video_id)
);

create index if not exists claim_occurrences_claim_idx
  on public.claim_occurrences (claim_id);
create index if not exists claim_occurrences_video_idx
  on public.claim_occurrences (video_id);

-- ============================================================================
-- hub_claims -> claims mapping. Null until an apologist promotes the claim;
-- promotion is always an explicit curation step, never automatic at ingest.
-- ============================================================================
alter table public.hub_claims
  add column if not exists claim_id uuid references public.claims(id) on delete set null;

create index if not exists hub_claims_claim_idx
  on public.hub_claims (claim_id);

-- ============================================================================
-- RLS
-- ============================================================================
alter table public.claims enable row level security;
alter table public.claim_occurrences enable row level security;

-- Anon/authenticated readers see published claims only. Drafts are visible
-- exclusively through the service client behind requireApologist().
drop policy if exists "claims: public read published" on public.claims;
create policy "claims: public read published" on public.claims
  for select using (status = 'published');

drop policy if exists "claim_occurrences: no public access" on public.claim_occurrences;
create policy "claim_occurrences: no public access" on public.claim_occurrences
  as restrictive
  for all
  using (false)
  with check (false);
