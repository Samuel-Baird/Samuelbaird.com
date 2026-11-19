-- 2026-11-19 ticket cleanup: close every ticket whose work is merged, carry any manual step left
-- over into its own sub-ticket, and delete 0.2 (shared premium/paywall) at the owner's request.
-- Notes are appended, never replaced. Status changes skip rows already closed in the UI;
-- new tickets use on conflict do nothing.

create or replace function pg_temp.ticket_note(p_ref text, p_status text, p_note text)
returns void language sql as $$
  update public.admin_tickets
     set status = case when p_status is null or status in ('done', 'dropped') then status else p_status end,
         notes = case when notes = '' then p_note else notes || E'\n\n' || p_note end
   where ref = p_ref;
$$;

-- Merged: close --------------------------------------------------------------------------------
select pg_temp.ticket_note('0.1', 'done',
  '2026-11-19: closed. Sign-in is shared across everything under samuelbaird.com (PR #52). Only Latter-day Stats (bookmarks, upvotes, study progress, notifications, donations, its admin) and /admin use a login; deseret.wiki and mcp.deseret.wiki have no signed-in features, so cross-domain sign-in waits until one of them needs it.');

select pg_temp.ticket_note('0.3', 'done',
  '2026-11-19: closed. PR #58 merged; the Amazon tag is live on every referral link. The eBay Partner Network signup moves to 0.3.1.');

select pg_temp.ticket_note('0.4', 'done',
  '2026-11-19: closed. Dashboard merged in PR #56 (moved to Cloudflare in PR #67). The read-only Cloudflare token for the Deploys panel stays open as 0.4.1.');

select pg_temp.ticket_note('2.1', 'done',
  '2026-11-19: closed. Extension merged in PR #54 and submitted to the Chrome Web Store. Waiting on store review moves to 2.1.1.');

select pg_temp.ticket_note('4', 'done',
  '2026-11-19: closed. /wishlist is live, synced daily from Amazon, with the Associates tag on every link (PR #58). Set priorities in wishlist/priorities.json any time.');

-- Manual steps carried out of the closed tickets ----------------------------------------------
insert into public.admin_tickets
  (ref, parent_ref, title, summary, notes, category, status, visibility,
   priority, impact, traffic, revenue, ease, monetization, tags, links)
values
('0.3.1', '0.3', 'Apply to eBay Partner Network and set EBAY_CAMPAIGN_ID',
 'Once approved, put the campaign ID in packages/family/referrals.mjs (EBAY_CAMPAIGN_ID, currently null) so eBay links earn.',
 'Needed by the collection page (7) for eBay links.',
 'admin', 'next', 'private', 3, 2, 1, 3, 5, '{referral}', '{money,ebay}',
 '[{"label":"eBay Partner Network","url":"https://partnernetwork.ebay.com/"}]'),
('2.1.1', '2.1', 'Chrome Web Store: Deseret extension goes live',
 'Submitted 2026-11-18; waiting on review. Close when the listing is public and linked from deseret.wiki.', '',
 'deseret', 'blocked', 'public', 3, 3, 2, 1, 5, '{}', '{deseret,extension}', '[]')
on conflict (ref) do nothing;

-- Deleted at the owner's request --------------------------------------------------------------
delete from public.admin_tickets where ref = '0.2';
