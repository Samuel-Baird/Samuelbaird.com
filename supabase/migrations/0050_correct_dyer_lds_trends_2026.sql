-- Correct 'dyer-lds-trends-us-byu-studies-2026' with data read directly from the
-- primary source (BYU Studies report page + full report PDF) rather than the
-- secondary Deseret News op-ed originally used in 0030_seed_studies_batch3.sql.
--
-- Notably drops the unverified "peer-reviewed (double-blind review)" claim —
-- the report itself makes no mention of peer review; it is published directly
-- by BYU Studies as a report, not through a journal review process.

update public.studies
set
  authors = array[
    'W. Justin Dyer',
    'Jenet Jacob Erickson',
    'Sam A. Hardy',
    'Barbara Morgan Gardner',
    'David C. Dollahite'
  ],
  source = 'BYU Studies',
  abstract = 'A BYU Studies report synthesizing five national/longitudinal datasets — the General Social Survey (1977-2022), the 2024 Pew Religious Landscape Study, the Cooperative Election Survey, the 2025 Spiritual Seismology Survey, and the BYU Family Foundations of Youth Development panel (2016-2024) — to describe US Latter-day Saint religious practice, well-being, and retention relative to other faiths. It finds Latter-day Saints lead major US religious groups on church attendance, personal/family scripture reading and prayer, and "active" retention (identifying as LDS and attending monthly as adults), while also documenting a long-run decline in overall identification retention since the 1980s. Using the longitudinal FFYD panel, it identifies not feeling God''s presence daily and political-ideology misalignment as the strongest predictors of Latter-day Saint youth deidentifying in their early twenties. It also finds most who leave remain open to religion generally and to returning to the Church specifically.',
  findings = array[
    '76% of Latter-day Saint Millennials/Gen Z attend religious services at least monthly (69% at least weekly) -- the highest of any US religious group measured (Pew Religious Landscape Study 2024, n=35,652).',
    '42% of those raised Latter-day Saint still identify as LDS and attend monthly as adults ("active retention") -- the highest active-retention rate of any US religion; among Millennial+ Christians only Adventists retain active members at a higher rate.',
    'Overall identification-retention rate is ~50% today, down from 82% in the 1980s and 58% by the 2000s (General Social Survey) -- still higher than every other Christian denomination except Catholics and Orthodox Christians.',
    '80% of Latter-day Saint parents pray and/or read scripture with their children, the highest of any faith surveyed (vs. 73% Evangelical, 70% Muslim).',
    'Among LDS youth who deidentify in their early 20s, not feeling God''s presence in daily life and political ideology were the strongest predictors (Family Foundations of Youth Development panel, 2016-2024).',
    'Of those who deidentify from the Church, 54% still say religion or spirituality is important to them and roughly two-thirds remain open to someday returning; on mental-health measures (Healthy Minds Study 2021-22), current LDS members'' depression, anxiety, and suicide-attempt rates are statistically similar to most other faiths, not distinctly better or worse.'
  ],
  tags = array['Demographics', 'Retention', 'Attendance', 'Wellbeing', 'BYU'],
  external_url = 'https://byustudies.byu.edu/latter-day-saint-trends',
  secondary_url = 'https://website-files-bucket.s3.us-west-2.amazonaws.com/books/book_pdf/LDS%20Religiousness%20Report.pdf',
  source_type = 'study',
  category = 'Major Demographic Surveys',
  featured = true,
  limitations = 'All five authors are BYU Religious Education/Family Life faculty and the report is published directly by BYU Studies rather than through a journal with a documented peer-review process -- institutional and faith affiliation may shape framing and emphasis, though the headline comparisons rely on established third-party probability samples (GSS, Pew RLS, CES). The 2025 Spiritual Seismology Survey component is a Qualtrics opt-in online panel (quota-matched to ACS benchmarks, not a true random sample) with only 1,668 current/former LDS respondents. The Family Foundations of Youth Development panel is geographically concentrated in Utah, Arizona, and Southern California and is not nationally representative. Some comparisons (e.g., retention across denominations) are sensitive to which comparison group -- broad tradition vs. specific denomination -- is used, a choice the authors make explicit but that affects the headline numbers.'
where slug = 'dyer-lds-trends-us-byu-studies-2026';
