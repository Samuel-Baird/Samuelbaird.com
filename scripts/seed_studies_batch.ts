/**
 * Seed/update a batch of studies submitted by the owner.
 *
 * Idempotent on slug: re-running updates the row but doesn't create duplicates.
 *
 * Usage: npx tsx scripts/seed_studies_batch.ts
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });

import { Client } from "pg";

type StudySeed = {
  slug: string;
  title: string;
  authors: string[];
  year: number | null;
  source: string;
  abstract: string | null;
  tags: string[];
  external_url: string;
  featured: boolean;
};

const STUDIES: StudySeed[] = [
  {
    slug: "pew-2023-warmth-toward-religious-groups",
    title:
      "Americans Feel More Positive Than Negative About Jews, Mainline Protestants, Catholics",
    authors: [],
    year: 2023,
    source: "Pew Research Center",
    abstract:
      "Pew Research finds Americans hold more negative views of Latter-day Saints than any other major religious group — about 1 in 4 view Latter-day Saints unfavorably. Conversely, Latter-day Saints themselves rate every other religious group more positively than they are rated in return.",
    tags: ["perception", "pew"],
    external_url:
      "https://www.pewresearch.org/religion/2023/03/15/americans-feel-more-positive-than-negative-about-jews-mainline-protestants-catholics/",
    featured: true,
  },
  {
    slug: "pope-religious-worship-attendance-cellphone-2024",
    title: "Religious Worship Attendance in America: Evidence from Cellphone Data",
    authors: ["Devin G. Pope"],
    year: 2024,
    source: "NBER Working Paper (Devin G. Pope)",
    abstract:
      "Anonymized cellphone-location data finds only ~5% of Americans actually attend religious services in a given week, despite 22% reporting that they do. Latter-day Saints are the most regular churchgoers in the U.S. — more consistent than Catholics, despite there being roughly 14× as many Catholics. Typical LDS services run about 115 minutes, tied with Orthodox Christians and Jehovah's Witnesses. Latter-day Saints also show the lowest cellphone-observed visits to tobacco shops, liquor stores, and strip clubs (1.7%). Utah ranks highest of any state for the alignment between stated religious identity and observed behavior.",
    tags: ["religious-practice", "behavior", "cellphone-data"],
    external_url: "https://www.nber.org/papers/w32127",
    featured: true,
  },
  {
    slug: "dyer-18-years-lds-mental-health-2023",
    title:
      "Perspective: What 18 Years of Research Tells Us About the Mental Health of Latter-day Saints",
    authors: ["Justin Dyer"],
    year: 2023,
    source: "Deseret News",
    abstract:
      "Reviewing 18 years of research, Justin Dyer reports that practicing Latter-day Saints show lower substance abuse, lower rates of depression, anxiety, and suicidal ideation, better body image, and — contrary to common assumptions — better mental health outcomes for LGBTQ Latter-day Saints in many measures.",
    tags: ["mental-health", "lgbtq", "review"],
    external_url:
      "https://www.deseret.com/2023/6/20/23759342/latter-day-saint-mental-health-research/",
    featured: true,
  },
  {
    slug: "sltrib-2025-pew-lds-religious-practice",
    title: "Pew Study: Latter-day Saints Among the Most Religiously Active",
    authors: [],
    year: 2025,
    source: "The Salt Lake Tribune",
    abstract:
      "Coverage of the 2025 Pew Religious Landscape Study: Latter-day Saints lead U.S. religious traditions in family-level religious practice — praying and reading scripture with family, praying more often overall, reading sacred text outside of formal worship, and attending services in person at higher rates than any other tradition.",
    tags: ["religious-practice", "pew"],
    external_url:
      "https://www.sltrib.com/religion/2025/02/26/pew-study-latter-day-saints-among/",
    featured: false,
  },
  {
    slug: "pew-2012-mormons-beliefs-practices",
    title: "Mormons in America: Beliefs and Practices",
    authors: [],
    year: 2012,
    source: "Pew Research Center",
    abstract:
      "Pew's 2012 portrait of Latter-day Saints in the United States — beliefs, religious practices, family life, and demographics. A frequently cited baseline for later comparisons.",
    tags: ["pew", "demographics", "religious-practice"],
    external_url:
      "https://www.pewresearch.org/religion/2012/01/12/mormons-in-america-beliefs-and-practices/",
    featured: false,
  },
  {
    slug: "pew-2025-decline-christianity-lds-racial",
    title:
      "Decline of Christianity in the U.S. Has Slowed, May Have Leveled Off",
    authors: [],
    year: 2025,
    source: "Pew Research Center",
    abstract:
      "Pew finds the long-running decline in U.S. Christian affiliation has slowed and may be leveling off. Within the Latter-day Saint tradition specifically, the ratio of white to non-white members is shifting — the membership is becoming more racially diverse.",
    tags: ["pew", "demographics"],
    external_url:
      "https://www.pewresearch.org/religion/2025/02/26/decline-of-christianity-in-the-us-has-slowed-may-have-leveled-off/",
    featured: false,
  },
  {
    slug: "pew-2025-religion-immigration-diversity",
    title: "Religion and Views on Immigration and Diversity",
    authors: [],
    year: 2025,
    source: "Pew Research Center",
    abstract:
      "Latter-day Saints are more likely than members of other major U.S. religious traditions to view racial and ethnic diversity as a strength for society.",
    tags: ["pew", "diversity"],
    external_url:
      "https://www.pewresearch.org/religion/2025/02/26/religion-and-views-on-immigration-and-diversity/",
    featured: false,
  },
  {
    slug: "pew-2012-mormons-family-life",
    title: "Mormons and Family Life",
    authors: [],
    year: 2012,
    source: "Pew Research Center",
    abstract:
      "Among Latter-day Saints, men are more likely than women to favor ordaining women to the priesthood. LDS respondents rate being good parents and having a successful marriage as exceptionally high life priorities relative to the general U.S. population.",
    tags: ["pew", "family"],
    external_url:
      "https://www.pewresearch.org/religion/2012/01/12/mormons-in-america-family-life/",
    featured: false,
  },
  {
    slug: "pew-2025-religious-identity",
    title: "Pew Religious Landscape Study: Religious Identity",
    authors: [],
    year: 2025,
    source: "Pew Research Center",
    abstract:
      "Pew's 2025 Religious Landscape Study finds Latter-day Saint affiliation in the United States is fairly stable — neither growing nor declining substantially over the past decade, even as broader U.S. Christian affiliation has shifted.",
    tags: ["pew", "demographics"],
    external_url:
      "https://www.pewresearch.org/religion/2025/02/26/religious-landscape-study-religious-identity/",
    featured: false,
  },
  {
    slug: "pew-2025-importance-religion-and-bible",
    title: "Importance of Religion and the Bible",
    authors: [],
    year: 2025,
    source: "Pew Research Center",
    abstract:
      "About 46% of Orthodox, Catholic, and mainline Protestant respondents say the Bible is very important in their lives. Among Latter-day Saints — alongside Evangelicals and historically Black Protestants — that figure climbs to roughly 80%.",
    tags: ["pew", "scripture"],
    external_url:
      "https://www.pewresearch.org/religion/2025/02/26/importance-of-religion-and-the-bible/",
    featured: false,
  },
  {
    slug: "pew-2010-religious-knowledge-survey",
    title: "U.S. Religious Knowledge Survey: Who Knows What About Religion",
    authors: [],
    year: 2010,
    source: "Pew Research Center",
    abstract:
      "Pew's religious knowledge survey found Latter-day Saints scored notably higher on questions about the Bible than the U.S. average — among the top-scoring religious traditions on biblical literacy.",
    tags: ["pew", "scripture"],
    external_url:
      "https://www.pewresearch.org/religion/2010/09/28/u-s-religious-knowledge-survey-who-knows-what-about-religion/",
    featured: false,
  },
  {
    slug: "pew-2025-religion-and-views-of-right-and-wrong",
    title: "Religion and Views of Right and Wrong",
    authors: [],
    year: 2025,
    source: "Pew Research Center",
    abstract:
      "Examines whether U.S. religious groups see moral rules as absolute or situational, and whether belief in God is viewed as necessary for being moral. Latter-day Saints lean strongly toward the view that belief in God matters for being moral and having good values.",
    tags: ["pew", "ethics"],
    external_url:
      "https://www.pewresearch.org/religion/2025/02/26/religion-and-views-of-right-and-wrong/",
    featured: false,
  },
  {
    slug: "pew-2025-religion-and-science-compatibility",
    title: "Religion and Science: Views on Compatibility",
    authors: [],
    year: 2025,
    source: "Pew Research Center",
    abstract:
      "Pew finds Latter-day Saints report the highest perceived compatibility between religion and science of any major U.S. religious tradition.",
    tags: ["pew", "science"],
    external_url:
      "https://www.pewresearch.org/religion/2025/02/26/religion-and-views-of-science/",
    featured: false,
  },
  {
    slug: "mormonr-polygamy-prevalence",
    title: "Latter-day Saints and Polygamy",
    authors: [],
    year: null,
    source: "MormonR",
    abstract:
      "Most historians estimate the rate of plural marriage in 19th-century Latter-day Saint communities was between 15% and 30% — meaning approximately 1 in 5 men had plural wives. The practice was never universal among Church members.",
    tags: ["history", "polygamy"],
    external_url:
      "https://mormonr.org/qnas/tM3Gfb/latter_day_saints_and_polygamy",
    featured: false,
  },
  {
    slug: "ogletree-perfectionism-adolescent-mental-health-2024",
    title: "Perfectionism's Influence on Adolescent Mental Health",
    authors: ["Mark D. Ogletree"],
    year: 2024,
    source: "BYU Studies 63, no. 4 (2024)",
    abstract:
      "Mark D. Ogletree examines how perfectionism affects adolescent mental health in Latter-day Saint contexts. Findings include that LDS suicide ideation rates are lower than commonly assumed, alongside related discussion of pornography exposure and mental health.",
    tags: ["mental-health", "youth", "scholarship"],
    external_url: "https://byustudies.byu.edu/issue/63-4",
    featured: false,
  },
  {
    slug: "times-and-seasons-2025-are-lds-happier",
    title:
      "Are Latter-day Saints Happier? The Pew Religious Landscape Survey, Relationship with the Church, and Flourishing",
    authors: [],
    year: 2025,
    source: "Times and Seasons (blog)",
    abstract:
      "An independent analysis of the 2025 Pew Religious Landscape Survey examining the relationship between active commitment to The Church of Jesus Christ of Latter-day Saints and measures of human flourishing.",
    tags: ["happiness", "flourishing", "pew"],
    external_url:
      "https://timesandseasons.org/index.php/2025/06/are-latter-day-saints-happier-the-pew-religious-landscape-survey-relationship-with-the-church-and-flourishing/",
    featured: false,
  },
  {
    slug: "fair-2024-coates-moral-foundations",
    title: "Moral Foundations and Latter-day Saints",
    authors: ["Coates"],
    year: 2024,
    source: "FAIR Conference (August 2024)",
    abstract:
      "Conference presentation applying moral foundations theory (the framework popularized by Jonathan Haidt) to Latter-day Saint thought and practice.",
    tags: ["apologetics", "scholarship"],
    external_url:
      "https://www.fairlatterdaysaints.org/conference/august-2024_fair_conference/coates-moral_foundations",
    featured: false,
  },
  {
    slug: "byustudies-religion-sexual-orientation-utah-youth-suicidality",
    title:
      "Religion and Sexual Orientation as Predictors of Utah Youth Suicidality",
    authors: [],
    year: null,
    source: "BYU Studies",
    abstract:
      "Peer-reviewed analysis examining religion and sexual orientation as predictors of suicidality among Utah youth. See the external source for full author list and findings.",
    tags: ["suicide", "utah", "lgbtq", "youth"],
    external_url:
      "https://byustudies.byu.edu/article/religion-and-sexual-orientation-as-predictors-of-utah-youth-suicidality",
    featured: false,
  },
  {
    slug: "byu-studies-issue-63-4",
    title: "BYU Studies, Volume 63 Issue 4",
    authors: [],
    year: 2024,
    source: "BYU Studies",
    abstract:
      "Latter-day Saint scholarship issue (2024) — articles include Ogletree's work on perfectionism and adolescent mental health.",
    tags: ["scholarship"],
    external_url: "https://byustudies.byu.edu/issue/63-4",
    featured: false,
  },
  {
    slug: "qsaltlake-2018-utah-faith-suicide-research",
    title: "Utah Research on Faith-Related Suicide",
    authors: [],
    year: 2018,
    source: "QSaltLake",
    abstract:
      "News coverage of research examining the relationship between faith, religious community, and suicide in Utah.",
    tags: ["suicide", "utah", "lgbtq"],
    external_url:
      "https://www.qsaltlake.com/news/2018/12/06/utah-research-on-faith-related-suicide/",
    featured: false,
  },
  {
    slug: "lds-lgb-youth-mental-health-pubmed-27633316",
    title:
      "Mental Health Among LGB Latter-day Saint Youth (PubMed 27633316)",
    authors: [],
    year: 2016,
    source: "PubMed (NIH National Library of Medicine)",
    abstract:
      "In a surprising finding, Latter-day Saint LGB youth showed lower depression than non-LGB Latter-day Saint counterparts in this sample — challenging the assumption that LDS religious context is uniformly harmful to LGB youth mental health. Open the external source for the full study.",
    tags: ["lgbtq", "mental-health", "youth"],
    external_url: "https://pubmed.ncbi.nlm.nih.gov/27633316/",
    featured: false,
  },
  {
    slug: "psycnet-apa-sgd-0000517",
    title: "Sexual Orientation, Gender Diversity, and Religion (APA)",
    authors: [],
    year: null,
    source: "Psychology of Sexual Orientation and Gender Diversity (APA)",
    abstract:
      "Peer-reviewed article in the APA's Psychology of Sexual Orientation and Gender Diversity journal. See the external source for full title, authors, and findings.",
    tags: ["lgbtq", "religion"],
    external_url:
      "https://psycnet.apa.org/doiLanding?doi=10.1037%2Fsgd0000517",
    featured: false,
  },
  {
    slug: "tandf-mhrc-13674670110059569",
    title: "Religion and Mental Health Research",
    authors: [],
    year: null,
    source: "Mental Health, Religion & Culture (Taylor & Francis)",
    abstract:
      "Peer-reviewed research in the Mental Health, Religion & Culture journal. See the external source for full title, authors, and abstract.",
    tags: ["mental-health"],
    external_url:
      "https://www.tandfonline.com/doi/abs/10.1080/13674670110059569",
    featured: false,
  },
  {
    slug: "pubmed-11867352",
    title: "PubMed 11867352 — Religion and Health Research",
    authors: [],
    year: null,
    source: "PubMed (NIH National Library of Medicine)",
    abstract:
      "Peer-reviewed research entry indexed in PubMed. See the external source for full title, authors, and abstract.",
    tags: ["mental-health"],
    external_url: "https://pubmed.ncbi.nlm.nih.gov/11867352/",
    featured: false,
  },
];

async function main() {
  const ref = process.env.SUPABASE_PROJECT_REF!;
  const password = process.env.SUPABASE_DB_PASSWORD!;

  const pg = new Client({
    connectionString: `postgresql://postgres:${encodeURIComponent(
      password,
    )}@db.${ref}.supabase.co:5432/postgres`,
    ssl: { rejectUnauthorized: false },
  });
  await pg.connect();

  try {
    let inserted = 0;
    let updated = 0;
    for (const s of STUDIES) {
      const { rows } = await pg.query<{ xmax: string }>(
        `
        insert into public.studies
          (slug, title, authors, year, source, abstract, tags, external_url, featured)
        values
          ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        on conflict (slug) do update set
          title = excluded.title,
          authors = excluded.authors,
          year = excluded.year,
          source = excluded.source,
          abstract = excluded.abstract,
          tags = excluded.tags,
          external_url = excluded.external_url,
          featured = excluded.featured
        returning xmax::text;
        `,
        [
          s.slug,
          s.title,
          s.authors,
          s.year,
          s.source,
          s.abstract,
          s.tags,
          s.external_url,
          s.featured,
        ],
      );
      if (rows[0].xmax === "0") inserted++;
      else updated++;
    }
    console.log(`Done. Inserted: ${inserted}, updated: ${updated}.`);
  } finally {
    await pg.end();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
