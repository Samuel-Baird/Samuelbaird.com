-- 2026-11-21: ticket 15, Daniel Tovar's hand-off arrived (Deseret Devs msg 8610). Appends the packet link,
-- the checked fees and the review findings. Appended only once.

update public.admin_tickets
   set notes = case when notes = '' then n.note else notes || E'\n\n' || n.note end
  from (select $$2026-11-21 hand-off received (Deseret Devs, 06:04 UTC). Nothing filed yet.
- Packet (12 pages, the current one; readable by the owner's Google account): https://drive.google.com/file/d/1XukFHh4wdm2UZEUhOK5lHKoPIzZANBpO/view . p1 steps + 1023-EZ mission line, p2-3 articles, p4 board consent, p5-9 bylaws, p10-12 IRS sample conflict-of-interest policy.
- Order and fees: name search (free) -> Utah articles at businessregistration.utah.gov ($59; matches the FY2026 Utah fee schedule) -> directors sign consent by email -> EIN at irs.gov (free; owner is responsible party as President) -> 1023-EZ on pay.gov ($275; all 34 eligibility answers must be No). Then Utah TC-160 (sales tax) and TC-161 (franchise tax; some sources say it is automatic, confirm), yearly $18 Utah renewal and 990-N.
- Open: Sid's and Eirik's addresses; Brigham as a 5th director or not.
- Review findings sent to Daniel: articles purpose has "religious", bylaws 1.3 does not; COI policy lacks an Article VII heading; bylaws 6.2 names "Telos" (unexplained); which projects (and whose code/content) move under La Sal; nonprofit AI seats must serve La Sal's work only (private-benefit risk).
- Owner note: as President and EIN responsible party, the owner carries the filings and yearly upkeep. Weigh against school-first (GOALS.md).$$::text as note) n
 where ref = '15'
   and position('2026-11-21 hand-off received (Deseret Devs' in notes) = 0;
