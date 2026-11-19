-- 2026-11-18: new ticket 0.4.1. The sites moved from Vercel to Cloudflare Workers; the /admin deploys
-- panel now reads the Cloudflare API and needs a read-only token. On conflict do nothing.

insert into public.admin_tickets
  (ref, parent_ref, title, summary, notes, category, status, visibility,
   priority, impact, traffic, revenue, ease, monetization, tags, links)
values
('0.4.1', '0.4', 'Admin dashboard: add the read-only Cloudflare token for the deploys panel',
 'The /admin "Deploys" panel shows each Worker''s latest Cloudflare deployment once samuelbaird-com has a read-only API token.',
$$Steps:
- dash.cloudflare.com/profile/api-tokens > Create Token > Custom: one permission, Account > Workers Scripts > Read, on B13llama@gmail.com's Account. Name it "samuelbaird-admin-readonly". No zone permissions.
- Set it on the samuelbaird-com Worker: from sites/samuelbaird.com run npx wrangler secret put CLOUDFLARE_API_TOKEN (CLOUDFLARE_ACCOUNT_ID is already set).
- Check samuelbaird.com/admin: the Deploys table should list every Worker instead of the "Add CLOUDFLARE_API_TOKEN" note.
Never reuse the sb-deploy token here: it can edit DNS and Workers.$$,
 'infra', 'backlog', 'private', 2, 2, 1, 1, 5, '{}', '{admin,cloudflare}',
 '[{"label":"/admin","url":"https://samuelbaird.com/admin"},{"label":"Cloudflare API tokens","url":"https://dash.cloudflare.com/profile/api-tokens"}]')
on conflict (ref) do nothing;
