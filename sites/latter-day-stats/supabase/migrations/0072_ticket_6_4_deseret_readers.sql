-- Ticket 6.4: revamp the 1868 Deseret Readers with less archaic spelling (future project).
insert into public.admin_tickets
  (ref, parent_ref, title, summary, notes, category, status, visibility,
   priority, impact, traffic, revenue, ease, monetization, tags, links)
values
('6.4', '6', 'Revamp the Deseret Readers with less archaic spelling',
 'New editions of the Deseret First and Second Readers (1868) respelled in modern, consistent Deseret, so learners are not tripped up by 1860s spellings and dialect.',
$$Re-transliterate the readers'' text with the site''s modern spelling (CMU-based, see the deseret/spelling-fonts-mobile work) and keep the 1868 original side by side for comparison.
Feeds the 6.1 graded passages. Money: free online; printed primer edition (ties to 6''s print idea).$$,
 'deseret', 'idea', 'public', 2, 3, 2, 2, 3, '{print}', '{deseret,learning,readers}', '[]')
on conflict (ref) do nothing;
