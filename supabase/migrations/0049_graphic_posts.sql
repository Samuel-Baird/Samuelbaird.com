-- Graphic post tracking: which Data Explorer graphics the site owner has
-- posted to social media. Graphics live in code (src/lib/data-explorer.ts)
-- keyed by (dataset slug, imageSrc basename); this table stores only the
-- posting state, keyed the same way.
--
-- RLS posture: deny-all, like the hub tables (0039/0040). Reads and writes
-- go exclusively through createSupabaseServiceClient() behind requireAdmin()
-- (src/app/actions/graphic-posts.ts); nothing here is public.

create table if not exists public.graphic_posts (
  id uuid primary key default gen_random_uuid(),
  dataset_slug text not null,
  graphic_id text not null,
  posted boolean not null default false,
  -- Free text on purpose - the owner types dates however they like
  -- ("8/12, 8/27 IG + X"). Structure can come later if ever needed.
  posted_dates text not null default '',
  created_by uuid references public.profiles(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (dataset_slug, graphic_id),
  constraint graphic_posts_dataset_slug_format
    check (dataset_slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  -- Basenames include underscores (state-of-theology quiz item ids).
  constraint graphic_posts_graphic_id_format
    check (graphic_id ~ '^[a-z0-9][a-z0-9_-]*$')
);

drop trigger if exists graphic_posts_set_updated_at on public.graphic_posts;
create trigger graphic_posts_set_updated_at
  before update on public.graphic_posts
  for each row execute function public.set_updated_at();

alter table public.graphic_posts enable row level security;

drop policy if exists "graphic_posts: no public access" on public.graphic_posts;
create policy "graphic_posts: no public access" on public.graphic_posts
  as restrictive for all using (false) with check (false);
