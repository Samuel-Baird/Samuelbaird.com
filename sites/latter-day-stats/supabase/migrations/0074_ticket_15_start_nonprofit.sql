-- 2026-11-21: new ticket 15, starting a nonprofit (owner asked via Relay, item #99).
-- Private: about the owner's own plans. On conflict do nothing.
-- Inserted directly on 2026-11-21 (live DB had 0062-0073 unapplied); safe to re-run.

insert into public.admin_tickets
  (ref, parent_ref, title, summary, notes, category, status, visibility,
   priority, impact, traffic, revenue, ease, monetization, tags, links)
values
('15', null, 'Start a nonprofit',
 'Look into starting a nonprofit. Nonprofit status opens grant and discount programs, as MTA''s status just did for ElevenLabs.',
$$Source: the Deseret Devs Messenger chat, read 2026-11-21 (about 160 messages back to 2026-11-21 00:35 UTC). The chat says little about starting a new nonprofit. The only related item:
- MTA's nonprofit status qualified it for ElevenLabs' Impact Program (a free year of voice agents, about $240 a year). Carl submitted the application and finished the Goodstack verification; ElevenLabs said it would answer in 2–3 days (applied, not approved yet).
That shows why nonprofit status is useful: programs like ElevenLabs Impact, verified through Goodstack, give software free or at a discount.

Open questions (the chat did not answer these):
- Purpose and mission: what would the nonprofit do, and how is it different from MTA? (Candidates in this repo: the Deseret Wiki/MCP, Latter-day Stats, Urim, Pulpit and the theology research tools.)
- New entity or not: start a new one, or run the projects under an existing nonprofit (for example MTA, or a fiscal sponsor)?
- Name.
- Who is involved: founders and board (a Utah nonprofit corporation needs at least 3 directors).
- Legal steps and costs: Utah nonprofit corporation filing, EIN, then IRS Form 1023-EZ (if eligible) or Form 1023 for 501(c)(3) status, plus annual renewal and Form 990-N. Check current fees before filing.
- Time: GOALS.md puts school first until graduating in spring 2027. Decide whether this waits until then.

Agent brief:
- Read GOALS.md and the root CLAUDE.md first. This is a planning ticket, not code.
- Ask the owner for the purpose, the name and who would be on the board before doing anything else.
- Then write a one-page plan: new entity or fiscal sponsor, the steps in order, current fees from official sources (Utah Division of Corporations, IRS), and the yearly upkeep.
- Spend no money and file nothing without the owner's OK.$$,
 'business', 'idea', 'private', 2, 3, 1, 2, 2, '{}', '{nonprofit,legal,mta}', '[]')
on conflict (ref) do nothing;
