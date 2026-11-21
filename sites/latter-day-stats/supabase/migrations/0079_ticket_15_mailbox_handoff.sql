-- 2026-11-21: ticket 15 (La Sal Institute), Relay item #115 (GitHub agent mailbox Noah-Airmet/ddevs-agents#1).
-- Appends mailbox packet review, new files (ai-programs.md, purpose.md option, filing-steps.md), and COI cleanup catch.
-- Appends once; status unchanged.

update public.admin_tickets
   set notes = case when notes = '' then n.note else notes || E'\n\n' || n.note end
  from (select $$2026-11-21 mailbox handoff reviewed (Relay item #115, github.com/Noah-Airmet/ddevs-agents#1, cloned into tasks/la-sal-institute-filing/ddevs-agents). Nothing filed, paid, signed, or registered.

What is new in the mailbox repo beyond the 12-page Drive PDF:
- Editable markdown sources for all packet docs (README.md, filing-steps.md, articles-clauses.md, purpose.md, bylaws.md, conflict-of-interest-policy.md, first-board-consent.md) plus la-sal-institute-filing-packet.pdf.
- ai-programs.md: confirms no major AI/cloud nonprofit discount (Claude Team $8/seat + $20-$100 monthly API credits up to $500 via Goodstack, ChatGPT Business $8-$10/seat, Google Workspace+Gemini, Microsoft 365+Azure $2k/yr, GitHub Team, AWS via TechSoup) accepts articles + EIN alone; all need IRS 501(c)(3) recognition, and fiscal hosting under All Those in Favor does not qualify. Also flags GitHub for Nonprofits Getting Started page mentioning a religious-affiliation restriction.
- purpose.md: includes a project-agnostic alternative sentence for Article Third if the owner prefers not to hardcode "Restoration Commons" in the Utah Articles.
- filing-steps.md: full 34-question Form 1023-EZ worksheet summary (including Q34 no digital assets/crypto) and Utah Code 16-1a / 16-6a / TC-160 / TC-161 / 990-N details.

Additional draft cleanup found before board adoption:
- conflict-of-interest-policy.md (and PDF pp. 10-12) still contains two bracketed "[Hospital insert — for hospitals that complete Schedule C...]" blocks and the IRS sample preamble notes, in addition to the missing "Article VII —" heading before "Periodic Reviews". Strip those before adoption.
- bylaws.md section 1.2 still has blank principal office and registered agent street address placeholders to fill before adoption.
- README.md references logo/la-sal/, which was not copied into ddevs-agents (non-blocking).

Mailbox workflow: questions for Noah's agent Relay go via `relay-mailbox reply 1 --body ...` (to:relay label); close issue #1 with `relay-mailbox close 1` once Samuel files the Utah articles. Note: overlaps with task `take-over-daniel-tovar-s-nonprofit-work` (same La Sal Institute filing / ticket 15).$$::text as note) n
 where ref = '15'
   and position('2026-11-21 mailbox handoff reviewed (Relay item #115' in notes) = 0;
