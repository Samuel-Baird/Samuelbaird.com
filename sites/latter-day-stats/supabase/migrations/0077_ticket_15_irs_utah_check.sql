-- 2026-11-21: ticket 15 (La Sal Institute), item #99 follow-up: IRS clause check, 1023-EZ eligibility,
-- Utah tax steps, cost and time table, open questions for the owner. Appends once; status unchanged.

update public.admin_tickets
   set notes = case when notes = '' then n.note else notes || E'\n\n' || n.note end
  from (select $$2026-11-21 check of Daniel's packet (Relay item #99). Not legal advice.

New from the Deseret Devs chat (beyond the notes above): first program is Restoration Commons (open-access library, citation tools and a student research journal on Latter-day Saint history and thought), inside a wider open-humanities and science portfolio. Brigham offered to join the board. Other name ideas: Commons Laboratory, Commons Institute (Noah kept La Sal). Office default: the Draper address Noah posted. Nothing filed.

IRS 501(c)(3) clauses (Publication 557 sample language):
- Purpose (articles Third, para 1): matches the IRS sample word for word. OK.
- Restrictions (Fifth: no inurement, no substantial lobbying, no campaigns, only 501(c)(3) activities): matches. OK.
- Dissolution (Sixth): matches. OK.
- Fix before filing: bylaws 1.3 leaves out "religious"; make it match the articles. The COI policy lacks the "Article VII" heading that Article VIII refers to. (Both were asked to Daniel.)

1023-EZ eligibility (all worksheet answers must be No; else full Form 1023, $600 user fee):
- Gross receipts: under $50,000 in each of the past 3 years AND projected for each of the next 3. Large grants could break this.
- Total assets under $250,000. US corporation, not an LLC. Not a church, school, hospital, or supporting org. No donor-advised funds.
- Risk: the "successor" question. If La Sal takes over substantially all the assets or activities of a for-profit (for example an owner project that earns money now), the answer is Yes and the 1023-EZ is out. Decide what moves in before filing.
- Also: nonprofit AI seats and other discounts must serve La Sal's work only. Private benefit to the founders can cost the exemption later, even after a 1023-EZ approval.

Utah steps after the IRS letter:
- TC-160: sales tax exemption number (Tax Commission, Religious and Charitable section; send the IRS letter).
- TC-161: franchise/income tax exemption. Some sources say it is automatic with 501(c)(3) status; confirm with the Tax Commission.
- Property tax: only if La Sal owns property (county application).
- Charitable solicitation: before asking the public for donations, check Utah Code 13-22 with the Division of Consumer Protection (register or file a notice of exemption; 2023 HB 119 and 2026 SB 38 changed the rules).
- Every year: Utah renewal $18, IRS 990-N (free), board annual meeting in November (bylaws 4.1).

Cost and time:
| Step | Cost | Time |
| Name search | free | minutes |
| Utah articles | $59 | online, same day to a few days |
| Board consent (email) | free | days |
| EIN | free | minutes, once Utah shows formed |
| 1023-EZ | $275 ($600 if full 1023) | about 22 days for 80% of cases |
| TC-160 / TC-161 | free | weeks (one source: about 3 months) |
| Yearly | $18 + free 990-N | |
Total to start: $334 (verified against Utah FY2026 fee schedule and IRS).

Open questions for the owner:
1. When to file. School comes first until spring 2027 (GOALS.md); the work is small but the yearly upkeep is on the officers.
2. Are you fine as President and EIN responsible party?
3. Office address: Noah's Draper address, or another?
4. Brigham as a 5th director: yes or no?
5. Which projects move under La Sal, and does any of them earn money now (successor question above)?
6. Who pays the $334, and is it paid back by La Sal later?
7. Bank account: the consent allows one; who opens it and where?

Agent brief: the packet is the filing set (link above); a step-by-step list is in tasks/take-over-daniel-tovar-s-nonprofit-work/FILING-CHECKLIST.md. Wait for Daniel's answers to the 6 packet questions and the owner's answers above. File nothing, pay nothing, contact nobody without the owner's OK.$$::text as note) n
 where ref = '15'
   and position('2026-11-21 check of Daniel''s packet (Relay item #99)' in notes) = 0;
