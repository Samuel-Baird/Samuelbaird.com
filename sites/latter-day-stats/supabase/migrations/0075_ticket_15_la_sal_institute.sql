-- 2026-11-21: ticket 15 correction. The nonprofit already has a name and a filing packet:
-- La Sal Institute (Deseret Devs, 2026-11-20). Renames the ticket, sets status 'doing',
-- appends what is done and what is left. No addresses or ID numbers in the notes. Safe to re-run
-- (the note is appended only once).

update public.admin_tickets
   set title = 'Start La Sal Institute (nonprofit)',
       summary = 'File La Sal Institute as a Utah nonprofit corporation, get an EIN, then 501(c)(3) status. Daniel Tovar drafted the packet; Warren Jeffs (Relay) takes it over.',
       status = 'doing',
       notes = case when notes = '' then n.note else notes || E'\n\n' || n.note end
  from (select $$2026-11-21 correction (Relay task take-over-daniel-tovar-s-nonprofit-work): the first note above missed the 2026-11-20 messages. Facts from Deseret Devs:
- Name: La Sal Institute (Noah picked it on 2026-11-20; Wasatch Labs and Uinta were taken). Commons Institute and Commons Laboratory came up later; Noah kept La Sal. La Sal Institute .org and .com were free on 2026-11-20 (not bought).
- Officers (agreed 2026-11-18): Samuel president, Sid VP, Eirik treasurer, Noah secretary. Four directors. Samuel is incorporator; Noah is registered agent.
- Packet (Daniel's Google Drive, not shared with Samuel's connected Google account on 2026-11-21): steps on page 1, board consent on page 4, bylaws pages 5-9. Links: https://drive.google.com/file/d/1vmyTpPb6m6avYli6xU5ivYTtKOSxj-cE/view (first) and https://drive.google.com/file/d/1Tnt4fc-zRCvovYKtC-Eodtv2yHXTInxn/view (filled in).
- Cost Daniel gave: $334 total. Verify against the Utah Division of Corporations and IRS fee pages before paying.
- Purpose (from the chat): parent org for the "restoration commons" projects; one reason given is nonprofit pricing for Claude seats.

Left to do:
1. Sid's and Eirik's addresses go in the packet (only blanks left).
2. Samuel files the articles in Utah's portal himself (UtahID) and signs as incorporator. Not filed as of 2026-11-21 00:00 UTC.
3. Samuel gets the EIN himself (he types his SSN; never give it to an agent).
4. All four directors sign the board consent (an email reply counts, bylaws 4.7). Records only; nothing uploads.
5. IRS 501(c)(3) application (1023-EZ if eligible). Then nonprofit programs (Claude, ElevenLabs-type).

Agent brief: Daniel Tovar is posting a single hand-off in Deseret Devs. Read it before you act. Spend no money and file nothing without the owner's OK.$$::text as note) n
 where ref = '15'
   and position('2026-11-21 correction (Relay task take-over-daniel' in notes) = 0;
