-- Scheduled publishing for graphics. `publish_at` is the moment a graphic
-- goes live on the site; visibility is derived at read time as
--   published = true AND (publish_at IS NULL OR publish_at <= now())
-- (src/lib/graphic-publish.ts), so no cron is needed to flip anything - a
-- scheduled graphic simply becomes visible on the first request after its
-- time arrives. The timestamp is kept when a graphic is later hidden, so it
-- doubles as the record of when it was published (which the owner lines up
-- with social-media posts).
--
-- Existing published rows get an approximate publish_at from updated_at so
-- the admin views can show *something*; NULL stays NULL for never-published
-- rows.
alter table public.graphic_posts
  add column if not exists publish_at timestamptz;

update public.graphic_posts
  set publish_at = updated_at
  where published and publish_at is null;
