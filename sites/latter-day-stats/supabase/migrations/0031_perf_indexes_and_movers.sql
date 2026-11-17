-- Performance: indexes for time-range and recency queries, plus a SQL
-- function that computes the risers/fallers baseline + daily history in the
-- database instead of shipping 30 days of channel_stats rows to the app.

create index if not exists channel_stats_captured_idx
  on public.channel_stats (captured_at desc);

create index if not exists studies_created_idx
  on public.studies (created_at desc);

create index if not exists channels_active_created_idx
  on public.channels (created_at desc)
  where is_active = true;

-- One row per channel that has stats inside the window: the earliest capture
-- (baseline) and a daily-deduped history (latest capture per UTC day, so
-- manual refreshes don't double-count).
create or replace function public.get_channel_movers(window_days int default 30)
returns table (
  channel_id uuid,
  baseline_subscribers bigint,
  baseline_captured_at timestamptz,
  history jsonb
)
language sql
stable
set search_path = public
as $$
  with daily as (
    select distinct on (channel_id, (captured_at::date))
      channel_id, captured_at, subscribers
    from channel_stats
    where captured_at >= now() - make_interval(days => window_days)
    order by channel_id, (captured_at::date), captured_at desc
  )
  select
    channel_id,
    (array_agg(subscribers order by captured_at))[1]::bigint,
    min(captured_at),
    jsonb_agg(
      jsonb_build_object('captured_at', captured_at, 'subscribers', subscribers)
      order by captured_at
    )
  from daily
  group by channel_id;
$$;

grant execute on function public.get_channel_movers(int) to anon, authenticated;
