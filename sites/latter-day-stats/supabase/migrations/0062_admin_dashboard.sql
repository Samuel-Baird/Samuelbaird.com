-- Numbers for the owner's dashboard at samuelbaird.com/admin (ticket 0.4).
--
-- donations, premium_users and profiles are service-role-only, and the hub's functions
-- deliberately hold only the anon key plus the signed-in user's JWT (see
-- sites/samuelbaird.com/api/_lib/session.js). So instead of giving the hub a service key,
-- this security-definer function returns aggregates only (no emails, no rows), and only
-- to the site owner (public.is_site_owner(), migration 0061).

create or replace function public.admin_dashboard_summary()
returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  d30 timestamptz := now() - interval '30 days';
  d365 timestamptz := now() - interval '365 days';
begin
  if not public.is_site_owner() then
    raise exception 'not_owner' using errcode = '42501';
  end if;

  return jsonb_build_object(
    'generated_at', now(),
    'donations', (
      select jsonb_build_object(
        'count_all',   count(*),
        'cents_all',   coalesce(sum(amount_cents), 0),
        'count_30d',   count(*) filter (where created_at >= d30),
        'cents_30d',   coalesce(sum(amount_cents) filter (where created_at >= d30), 0),
        'cents_365d',  coalesce(sum(amount_cents) filter (where created_at >= d365), 0),
        'recurring_donors', count(distinct coalesce(email, stripe_customer_id)) filter (where recurring),
        'last_at',     max(created_at),
        'by_month', coalesce((
          select jsonb_agg(m order by m->>'month')
          from (
            select jsonb_build_object('month', to_char(date_trunc('month', created_at), 'YYYY-MM'),
                                      'cents', sum(amount_cents), 'count', count(*)) as m
            from public.donations
            where refunded_at is null and created_at >= date_trunc('month', now()) - interval '11 months'
            group by date_trunc('month', created_at)
          ) months
        ), '[]'::jsonb)
      )
      from public.donations
      where refunded_at is null
    ),
    'refunds', (select count(*) from public.donations where refunded_at is not null),
    'premium', (
      select jsonb_build_object(
        'count', count(*),
        'added_30d', count(*) filter (where created_at >= d30),
        'from_stripe', count(*) filter (where stripe_granted)
      ) from public.premium_users
    ),
    'accounts', (
      select jsonb_build_object(
        'count', count(*),
        'added_30d', count(*) filter (where created_at >= d30),
        'added_7d', count(*) filter (where created_at >= now() - interval '7 days')
      ) from public.profiles
    ),
    'tickets', (
      select jsonb_object_agg(status, n) from (
        select status, count(*) as n from public.admin_tickets group by status
      ) s
    )
  );
end;
$$;

revoke all on function public.admin_dashboard_summary() from public;
grant execute on function public.admin_dashboard_summary() to authenticated;
