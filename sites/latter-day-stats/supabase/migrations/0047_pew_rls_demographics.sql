-- Widen the quiz's optional demographic intake to Pew Research Center's
-- 2023-24 Religious Landscape Study instrument, so answers collected here
-- read against a national sample with no recoding step in between.
--
--   Pew Research Center. 2025. "2023-24 Religious Landscape Study (RLS)
--   Dataset." doi: 10.58094/3kwb-bf52.
--
-- Source documents, the machine-readable codebook, and the field-to-
-- variable table: docs/datasets/pew-rls-2023-24/. The runtime source for
-- every list below is src/lib/evangelical-quiz/demographics.ts; these rows
-- and constraints exist for FK integrity and admin joins. Change both
-- together — 0046 promised the full Pew taxonomy would land as a data
-- change, and apart from the new columns, it does.
--
-- Additive only, deliberately. `traditions` now holds Pew's FAMILY
-- variable, a level below RELTRAD ("Baptist family in the evangelical
-- Protestant tradition" is a denominational family, not a tradition), so
-- the table and its `tradition_slug` columns are misnamed. Renaming them
-- would break every deployed read between this migration and the next
-- Vercel deploy, which is a real outage for a cosmetic gain. The names are
-- historical; the comments below say what they hold.

comment on table public.traditions is
  'Pew RLS FAMILY: religious identities at the denominational-family level. '
  'Historical name — these are families within traditions, not traditions. '
  'Runtime source is src/lib/evangelical-quiz/demographics.ts.';

alter table public.traditions
  -- RELTRAD, used as the picker's option group. Null only on 'No answer'.
  add column if not exists group_label text,
  -- The RLS FAMILY code. Null where the site's list has no Pew counterpart.
  add column if not exists rls_family int,
  -- Hidden from the picker, still resolvable for display: slugs that predate
  -- the RLS taxonomy and are still referenced by rows recorded before it.
  add column if not exists retired boolean not null default false;

-- ---------------------------------------------------------------------------
-- The full FAMILY taxonomy
-- ---------------------------------------------------------------------------
-- Every one of Pew's 52 substantive FAMILY categories, plus a
-- prefer-not-to-say Pew has no code for. sort_order is the display order and
-- matches the array order in demographics.ts. pew_category (0046's name) is
-- the quiz's matchable tradition, which is why every Protestant and Catholic
-- row has one and nothing else does.

insert into public.traditions
  (slug, display_label, sort_order, pew_category, group_label, rls_family) values
  -- Evangelical Protestant tradition (FAMILY 1-18)
  ('baptist_evangelical','Baptist',1,'Evangelical','Evangelical Protestant',1),
  ('methodist_evangelical','Methodist',2,'Evangelical','Evangelical Protestant',2),
  ('nondenominational_evangelical','Nondenominational',3,'Evangelical','Evangelical Protestant',3),
  ('lutheran_evangelical','Lutheran',4,'Evangelical','Evangelical Protestant',4),
  ('presbyterian_evangelical','Presbyterian',5,'Evangelical','Evangelical Protestant',5),
  ('pentecostal_evangelical','Pentecostal',6,'Evangelical','Evangelical Protestant',6),
  ('episcopalian_evangelical','Anglican / Episcopalian',7,'Evangelical','Evangelical Protestant',7),
  ('restorationist_evangelical','Restorationist (Churches of Christ, Christian Churches)',8,'Evangelical','Evangelical Protestant',8),
  ('congregational_evangelical','Congregational',9,'Evangelical','Evangelical Protestant',9),
  ('holiness_evangelical','Holiness (Nazarene, Free Methodist)',10,'Evangelical','Evangelical Protestant',10),
  ('reformed_evangelical','Reformed',11,'Evangelical','Evangelical Protestant',11),
  ('adventist_evangelical','Adventist',12,'Evangelical','Evangelical Protestant',12),
  ('anabaptist_evangelical','Anabaptist (Mennonite, Brethren, Amish)',13,'Evangelical','Evangelical Protestant',13),
  ('pietist_evangelical','Pietist',14,'Evangelical','Evangelical Protestant',14),
  ('friends_evangelical','Friends / Quaker',15,'Evangelical','Evangelical Protestant',15),
  ('other_evangelical_fundamentalist','Other evangelical or fundamentalist',16,'Evangelical','Evangelical Protestant',16),
  -- Reused slug: 0046's tradition-level 'evangelical_protestant' means
  -- exactly FAMILY 18, "Protestant non-specific family in the Evangelical
  -- Protestant Tradition", so rows already carrying it stay correct.
  ('evangelical_protestant','No particular denomination',17,'Evangelical','Evangelical Protestant',18),

  -- Mainline Protestant tradition (FAMILY 34-45)
  ('baptist_mainline','Baptist',18,'Mainline','Mainline Protestant',34),
  ('methodist_mainline','Methodist',19,'Mainline','Mainline Protestant',35),
  ('nondenominational_mainline','Nondenominational',20,'Mainline','Mainline Protestant',36),
  ('lutheran_mainline','Lutheran',21,'Mainline','Mainline Protestant',37),
  ('presbyterian_mainline','Presbyterian',22,'Mainline','Mainline Protestant',38),
  ('episcopalian_mainline','Anglican / Episcopalian',23,'Mainline','Mainline Protestant',39),
  ('restorationist_mainline','Restorationist (Disciples of Christ)',24,'Mainline','Mainline Protestant',40),
  ('congregational_mainline','Congregational (United Church of Christ)',25,'Mainline','Mainline Protestant',41),
  ('reformed_mainline','Reformed',26,'Mainline','Mainline Protestant',42),
  ('anabaptist_mainline','Anabaptist (Mennonite, Brethren, Amish)',27,'Mainline','Mainline Protestant',43),
  ('friends_mainline','Friends / Quaker',28,'Mainline','Mainline Protestant',44),
  ('mainline_protestant','No particular denomination',29,'Mainline','Mainline Protestant',45),

  -- Historically Black Protestant tradition (FAMILY 67-72)
  ('baptist_black_protestant','Baptist',30,'Black Protestant','Historically Black Protestant',67),
  ('methodist_black_protestant','Methodist (AME, AME Zion, CME)',31,'Black Protestant','Historically Black Protestant',68),
  ('pentecostal_black_protestant','Pentecostal (Church of God in Christ)',32,'Black Protestant','Historically Black Protestant',69),
  ('holiness_black_protestant','Holiness',33,'Black Protestant','Historically Black Protestant',70),
  ('nondenominational_black_protestant','Nondenominational',34,'Black Protestant','Historically Black Protestant',71),
  ('historically_black_protestant','No particular denomination',35,'Black Protestant','Historically Black Protestant',72),

  -- Catholic (FAMILY 101)
  ('roman_catholic','Catholic',36,'Roman Catholic','Catholic',101),

  -- Other Christian traditions (FAMILY 102-106)
  ('latter_day_saint','Latter-day Saint (Mormon)',37,null,'Other Christian',102),
  ('orthodox_christian','Orthodox Christian',38,null,'Other Christian',103),
  ('jehovahs_witness','Jehovah''s Witness',39,null,'Other Christian',104),
  ('metaphysical_christian','Metaphysical (Christian Science, Unity, New Thought)',40,null,'Other Christian',105),
  ('other_christian','Another Christian tradition',41,null,'Other Christian',106),

  -- Non-Christian faiths (FAMILY 201-208). Pew splits these across three
  -- RELTRAD categories; one group here, since the distinction is analytic
  -- rather than something a respondent would recognize about themselves.
  ('jewish','Jewish',42,null,'Non-Christian faiths',201),
  ('muslim','Muslim',43,null,'Non-Christian faiths',202),
  ('buddhist','Buddhist',44,null,'Non-Christian faiths',203),
  ('hindu','Hindu',45,null,'Non-Christian faiths',204),
  ('other_religion','Another world religion (Sikh, Bahá''í, Jain, and others)',46,null,'Non-Christian faiths',205),
  ('unitarian_liberal_faith','Unitarian or another liberal faith',47,null,'Non-Christian faiths',206),
  ('new_age','New Age, Pagan, or Wiccan',48,null,'Non-Christian faiths',207),
  ('native_american_religion','Native American religion',49,null,'Non-Christian faiths',208),

  -- Religiously unaffiliated (FAMILY 301-303, the UNAFFILDETAIL split)
  ('atheist','Atheist',50,null,'Religiously unaffiliated',301),
  ('agnostic','Agnostic',51,null,'Religiously unaffiliated',302),
  ('nothing_in_particular','Nothing in particular',52,null,'Religiously unaffiliated',303),

  -- No Pew counterpart: a refusal, not Pew's 999 "no information" back-code.
  ('prefer_not_to_say','Prefer not to say',53,null,'No answer',null)
on conflict (slug) do update set
  display_label = excluded.display_label,
  sort_order    = excluded.sort_order,
  pew_category  = excluded.pew_category,
  group_label   = excluded.group_label,
  rls_family    = excluded.rls_family,
  retired       = false;

-- 0046's only slug with no place in the RLS taxonomy, which splits it into
-- atheist (301) and agnostic (302). Retired rather than deleted: rows
-- recorded before this migration still point at it.
update public.traditions
  set retired = true, group_label = 'Religiously unaffiliated'
  where slug = 'atheist_agnostic';

-- ---------------------------------------------------------------------------
-- The rest of the RLS demographic battery
-- ---------------------------------------------------------------------------
-- Nullable adds, no backfill (the 0037 pattern), on both the profile and the
-- run snapshot — the same pair of tables 0046's age/gender live on. Value
-- lists are the RLS variables named in each comment; keep them in step with
-- demographics.ts. `age` stays on both, no longer written: birth_decade
-- (RLS BIRTHDECADE) replaced it, and old rows keep what they recorded.

alter table public.profiles
  add column if not exists birth_decade text check (birth_decade in
    ('1940s_or_earlier','1950s','1960s','1970s','1980s','1990s','2000s','prefer_not_to_say')),
  add column if not exists hispanic text
    check (hispanic in ('yes','no','prefer_not_to_say')),
  add column if not exists race text
    check (race in ('white','black','asian','mixed','other','prefer_not_to_say')),
  add column if not exists education text check (education in
    ('high_school_or_less','some_college','college_graduate','postgraduate','prefer_not_to_say')),
  add column if not exists marital_status text check (marital_status in
    ('married','living_with_partner','divorced','separated','widowed','never_married','prefer_not_to_say')),
  -- RLS STATE, stored as the postal abbreviation rather than Pew's
  -- FIPS-derived code so an export reads plainly. The 50 states and DC; the
  -- exact membership is enforced in demographics.ts.
  add column if not exists us_state text check (us_state ~ '^[A-Z]{2}$');

alter table public.evangelical_quiz_runs
  add column if not exists birth_decade text check (birth_decade in
    ('1940s_or_earlier','1950s','1960s','1970s','1980s','1990s','2000s','prefer_not_to_say')),
  add column if not exists hispanic text
    check (hispanic in ('yes','no','prefer_not_to_say')),
  add column if not exists race text
    check (race in ('white','black','asian','mixed','other','prefer_not_to_say')),
  add column if not exists education text check (education in
    ('high_school_or_less','some_college','college_graduate','postgraduate','prefer_not_to_say')),
  add column if not exists marital_status text check (marital_status in
    ('married','living_with_partner','divorced','separated','widowed','never_married','prefer_not_to_say')),
  add column if not exists us_state text check (us_state ~ '^[A-Z]{2}$');
