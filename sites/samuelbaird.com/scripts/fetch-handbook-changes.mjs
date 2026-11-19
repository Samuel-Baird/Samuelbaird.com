#!/usr/bin/env node
// Build sites/samuelbaird.com/data/lds-handbook-changes.{json,csv} from the
// Church's published General Handbook "Summary of Recent Updates" page
// (live + historical Wayback Machine snapshots) and official Church Newsroom
// release announcements, paired with curated own-words descriptions in
// handbook-overrides.json.
//
// No dependencies. Run:
//   node sites/samuelbaird.com/scripts/fetch-handbook-changes.mjs           # use cache if present
//   node sites/samuelbaird.com/scripts/fetch-handbook-changes.mjs --refresh # refetch live summary page
//   node sites/samuelbaird.com/scripts/fetch-handbook-changes.mjs --refresh-archive # refetch Wayback snapshots too

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const CACHE_DIR = path.join(__dirname, 'cache');
const CACHE_FILE = path.join(CACHE_DIR, 'handbook-changes.json');
const OVERRIDES_FILE = path.join(__dirname, 'handbook-overrides.json');
const OUT_JSON = path.join(ROOT, 'data', 'lds-handbook-changes.json');
const OUT_CSV = path.join(ROOT, 'data', 'lds-handbook-changes.csv');

const REFRESH = process.argv.includes('--refresh');
const REFRESH_ARCHIVE = process.argv.includes('--refresh-archive');
const UA = 'samuelbaird.com-handbook-changes-dataset/1.0 (+https://samuelbaird.com/handbook-changes)';

const LIVE_SUMMARY_URL = 'https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng';

const SNAPSHOT_SOURCES = {
  '2020-08': 'https://web.archive.org/web/20200803201714id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2020-12': 'https://web.archive.org/web/20210112030606id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2021-03': 'https://web.archive.org/web/20210503073637id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2021-08': 'https://web.archive.org/web/20210816041623id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2022-08': 'https://web.archive.org/web/20220925232334id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2023-08': 'https://web.archive.org/web/20230909055210id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2024-05': 'https://web.archive.org/web/20240601002903id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2024-08': 'https://web.archive.org/web/20240821010756id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2025-02': 'https://web.archive.org/web/20250324181604id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2025-11': 'https://web.archive.org/web/20251216051714id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2026-03': 'https://web.archive.org/web/20260318201205id_/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=eng',
  '2026-10': LIVE_SUMMARY_URL,
};

// Official release metadata: publication date (from Church Newsroom release
// announcement or official release PDF) and primary announcement URL.
const RELEASE_META = {
  'February 2020': {
    date: '2020-02-19',
    release: 'February 2020',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/new-general-handbook',
  },
  'March 2020': {
    date: '2020-03-25',
    release: 'March 2020',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/handbook-update-primary-young-women-aaronic-priesthood-march-2020',
  },
  'July 2020': {
    date: '2020-07-31',
    release: 'July 2020',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/handbook-update-july-2020',
  },
  'December 2020': {
    date: '2020-12-18',
    release: 'December 2020',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/general-handbook-update-december-2020',
  },
  'March 2021': {
    date: '2021-03-31',
    release: 'March 2021',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/general-handbook-update-march-2021',
  },
  'July 2021': {
    date: '2021-08-04',
    release: 'August 2021',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/august-2021-update-general-handbook',
  },
  'August 2021': {
    date: '2021-08-04',
    release: 'August 2021',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/august-2021-update-general-handbook',
  },
  'December 2021': {
    date: '2021-12-15',
    release: 'December 2021',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/general-handbook-complete-english',
  },
  'August 2022': {
    date: '2022-08-01',
    release: 'August 2022',
    announcementUrl: 'https://assets.churchofjesuschrist.org/98/11/98117693393311ed8703eeeeac1e47465ba0e161/general_handbook_august_2022.pdf',
  },
  'August 2023': {
    date: '2023-08-31',
    release: 'August 2023',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/general-handbook-august-2023-update',
  },
  'May 2024': {
    date: '2024-05-31',
    release: 'May 2024',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/may-2024-update-general-handbook',
  },
  'August 2024': {
    date: '2024-08-19',
    release: 'August 2024',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/august-2024-general-handbook-update',
  },
  'February 2025': {
    date: '2025-03-21',
    release: 'March 2025',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/general-handbook-artificial-intelligence-search-assistant',
  },
  'March 2025': {
    date: '2025-03-21',
    release: 'March 2025',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/general-handbook-artificial-intelligence-search-assistant',
  },
  'November 2025': {
    date: '2025-12-16',
    release: 'December 2025',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/general-handbook-update-december-2025',
  },
  'December 2025': {
    date: '2025-12-16',
    release: 'December 2025',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/general-handbook-update-december-2025',
  },
  'March 2026': {
    date: '2026-03-18',
    release: 'March 2026',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/general-handbook-march-2026',
  },
  'October 2026': {
    date: '2026-10-22',
    release: 'October 2026',
    announcementUrl: 'https://newsroom.churchofjesuschrist.org/article/general-handbook-october-2026-update',
  },
};

const MONTHS = {
  january: '01', february: '02', march: '03', april: '04', may: '05', june: '06',
  july: '07', august: '08', september: '09', october: '10', november: '11', december: '12',
};

function resolveReleaseMeta(heading) {
  if (!heading) return null;
  if (RELEASE_META[heading]) return RELEASE_META[heading];
  const m = heading.match(/^([A-Za-z]+)\s+(20\d{2})$/);
  if (!m) return null;
  const mm = MONTHS[m[1].toLowerCase()];
  if (!mm) return null;
  return {
    date: `${m[2]}-${mm}-01`,
    release: `${m[1]} ${m[2]}`,
    announcementUrl: LIVE_SUMMARY_URL,
  };
}
// Known parentheticals that belong to official section titles rather than editorial notes
const TITLE_PARENS = new Set([
  'Public Affairs',
  'Stillborn and Miscarried Children',
  'Including Life Support',
  'Including Divorced',
  'Young Women',
  'Primary',
  'Relief Society',
  'Aaronic Priesthood',
  'Elders Quorum',
  'Sunday School',
  'or Risk Assessment',
]);

function decodeEntities(s) {
  return s
    .replace(/&nbsp;|&#160;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&rsquo;/g, '’')
    .replace(/&lsquo;/g, '‘')
    .replace(/&ldquo;/g, '“')
    .replace(/&rdquo;/g, '”')
    .replace(/&ndash;/g, '–')
    .replace(/&mdash;/g, '—')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');
}

function cleanText(html) {
  return decodeEntities(html.replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
}

function extractBodyBlock(html) {
  const m = html.match(/<div[^>]*class=["']?body-block["']?[^>]*>([\s\S]*?)<\/article>/i);
  return m ? m[1] : html;
}

async function loadSnapshots() {
  let cache = {};
  if (fs.existsSync(CACHE_FILE)) {
    cache = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
  }

  let updated = false;
  for (const [key, url] of Object.entries(SNAPSHOT_SOURCES)) {
    const isLive = url === LIVE_SUMMARY_URL;
    const shouldFetch = !cache[key] || (isLive && REFRESH) || (!isLive && REFRESH_ARCHIVE);
    if (!shouldFetch) continue;

    console.log(`Fetching ${key}: ${url}`);
    const res = await fetch(url, { headers: { 'user-agent': UA, 'accept-language': 'en-US,en;q=0.9' } });
    if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
    const fullHtml = await res.text();
    const html = extractBodyBlock(fullHtml);
    if (isLive) {
      // Determine the h2 release key so we never overwrite an older snapshot when a new release goes live
      const h2m = html.match(/<h2[^>]*>([\s\S]*?)<\/h2>/i);
      const h2txt = h2m ? cleanText(h2m[1]) : '';
      const meta = resolveReleaseMeta(h2txt);
      const targetKey = meta ? meta.date.slice(0, 7) : key;
      cache[targetKey] = { url, html };
    } else {
      cache[key] = { url, html };
    }
    updated = true;
  }

  if (updated) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
    fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2) + '\n');
  }
  return cache;
}

// O(n) trailing parenthetical splitter with zero regex backtracking
function splitTrailingNote(text) {
  let s = text.trim().replace(/\.\s*$/, '');
  // Handle unclosed parenthesis in official summary HTML (e.g. 38.2.9.1 in Nov 2025)
  if (!s.endsWith(')') && /\((clarified|updated|revised|new|added|removed|deleted)\b/i.test(s)) {
    s += ')';
  }
  if (!s.endsWith(')')) return { head: text.trim(), note: '' };

  let depth = 0;
  let openIdx = -1;
  for (let i = s.length - 1; i >= 0; i--) {
    if (s[i] === ')') depth++;
    else if (s[i] === '(') {
      depth--;
      if (depth === 0) {
        openIdx = i;
        break;
      }
    }
  }
  if (openIdx <= 0) return { head: text.trim(), note: '' };
  const inside = s.slice(openIdx + 1, -1).trim();
  const head = s.slice(0, openIdx).trim();
  if (TITLE_PARENS.has(inside)) return { head: text.trim(), note: '' };
  return { head, note: inside };
}

function classifyKind(head, note, rawText) {
  const n = note.toLowerCase();
  const t = `${head} ${note} ${rawText}`.toLowerCase();

  if (
    /\b(section deleted|deleted section|deleted;|deleted\b.*subsequent|deleted because|deleted to avoid)\b/.test(t) ||
    /^deleted\b/.test(n) ||
    /\breferences to .* have been removed\b/.test(t)
  ) {
    return 'removed';
  }
  if (
    (/\b(new section|new chapter|chapter \d+ is new)\b/.test(t) || /^new\b/.test(n)) &&
    !/\bnew section number\b/.test(t)
  ) {
    return 'new';
  }
  if (
    /\b(new section number|renumbered)\b/.test(t) &&
    !/\b(revised|updated|clarified|added|changed|renamed|moved|consolidated|created)\b/.test(n)
  ) {
    return 'renumbered';
  }
  return 'revised';
}

// Normalize legacy or Wayback hrefs into valid current churchofjesuschrist.org URLs
function normalizeSectionUrl(rawHref, chapter, chaptersMap, date) {
  const chapObj = chapter !== null && chapter !== undefined ? chaptersMap[String(chapter)] : null;
  let pathPart = '';
  let hash = '';

  if (rawHref) {
    let h = decodeEntities(rawHref).trim();
    // Strip Wayback wrapper if present
    const wb = h.match(/https?:\/\/web\.archive\.org\/web\/\d+(?:id_)?\/(https?:\/\/.*)$/i);
    if (wb) h = wb[1];
    h = h.replace(/^https?:\/\/(?:www\.)?churchofjesuschrist\.org/i, '');
    const hashIdx = h.indexOf('#');
    if (hashIdx !== -1) {
      hash = h.slice(hashIdx);
      h = h.slice(0, hashIdx);
    }
    const qIdx = h.indexOf('?');
    if (qIdx !== -1) h = h.slice(0, qIdx);
    pathPart = h;
  }

  // Legacy pre-August 2021 chapter slug rewrites (when Chapter 5 "General and Area Leadership"
  // was inserted, shifting old Chapter 5 Stake Leadership -> 6 and old Chapter 6 -> 7)
  if (pathPart === '/study/manual/general-handbook/5-stake-leadership') {
    pathPart = '/study/manual/general-handbook/6-stake-leadership';
  } else if (
    (pathPart === '/study/manual/general-handbook/6' || pathPart === '/study/manual/general-handbook/6-ward-leadership') &&
    date &&
    date < '2021-08-04'
  ) {
    pathPart = '/study/manual/general-handbook/7';
  } else if (pathPart === '/study/manual/general-handbook/24-preparing-and-recommending-missionaries') {
    pathPart = '/study/manual/general-handbook/24';
  } else if (pathPart === '/study/manual/general-handbook/28-temple-ordinances-for-ancestors') {
    pathPart = '/study/manual/general-handbook/28';
  } else if (pathPart === '/study/manual/general-handbook/31-interviews-and-counseling') {
    pathPart = '/study/manual/general-handbook/31';
  } else if (pathPart === '/study/manual/general-handbook/35-physical-facilities') {
    pathPart = '/study/manual/general-handbook/35';
  }

  if (!pathPart || !pathPart.startsWith('/study/manual/general-handbook/')) {
    if (chapObj) {
      pathPart = `/study/manual/general-handbook/${chapObj.slug}`;
    } else {
      pathPart = '/study/manual/general-handbook/title-page';
    }
  }

  return `https://www.churchofjesuschrist.org${pathPart}?lang=eng`;
}

// Rewrite raw parenthetical or chapter-level notes into concise, third-person
// own-words descriptions so no handbook prose is copied verbatim.
function paraphraseNote(note, title, section, chapter, kind) {
  let s = note.trim().replace(/\.\s*$/, '');
  if (!s) {
    if (kind === 'new') return `Adds section ${section} (${title}).`;
    if (kind === 'removed') return `Removes section ${section} (${title}).`;
    if (kind === 'renumbered') return `Renumbers section ${section} (${title}).`;
    return `Updates policies and instructions in section ${section} (${title}).`;
  }

  // Handle prose chapter/handbook-wide sentences
  if (/^Chapter\s+(\d+)\s+has been revised\.\s+It is now organized around the work of salvation and exaltation/i.test(s)) {
    return `Rewrites Chapter ${chapter} around the four areas of the work of salvation and exaltation and simplifies guidance for smaller units.`;
  }
  if (/^Chapter\s+(\d+)\s+has been revised and reorganized to emphasize the importance of ordinances and covenants/i.test(s)) {
    return `Reorganizes and revises Chapter ${chapter} to highlight ordinances and covenants.`;
  }
  if (/^Chapter\s+13\s+has been updated to reflect a First Presidency letter stating that a woman or a man may be called as ward Sunday School president/i.test(s)) {
    return 'Updates Chapter 13 so either a woman or a man may serve as ward Sunday School president.';
  }
  if (/^Chapter\s+24\s+has been reorganized and revised/i.test(s)) {
    return 'Reorganizes Chapter 24 to unify young teaching and service missionary calls and strengthen missionary support.';
  }
  if (/^Chapter\s+26\s+has been reorganized and revised/i.test(s)) {
    return 'Reorganizes Chapter 26 for living-ordinance recommends in LCR Ordinance Preparation and mobile temple recommends.';
  }
  if (/^Chapter\s+27\s+has been reorganized and revised/i.test(s)) {
    return 'Reorganizes Chapter 27 around updated living-ordinance recommend procedures.';
  }
  if (/^Throughout chapter 18\s*,\s*the phrase/i.test(s)) {
    return 'Replaces “ordinances and blessings” with “ordinances” across Chapter 18 to reflect that blessings are ordinances.';
  }
  if (/^Throughout chapter 19\s*,\s*language has been revised to allow worshipful children’s songs/i.test(s)) {
    return 'Allows appropriate children’s songs to be sung as congregational hymns across Chapter 19.';
  }
  if (/^Throughout chapter 19\s*,\s*references to the Sacred Music app have been removed/i.test(s)) {
    return 'Removes Sacred Music app references across Chapter 19 following its merger into Gospel Library.';
  }
  if (/^Throughout chapter 24\s*,\s*the terms “service mission”/i.test(s)) {
    return 'Updates terminology across Chapter 24 to “service missionary assignment” and “service missionary advisers.”';
  }
  if (/^Throughout chapter 24\s*,\s*the minimum age for single young women/i.test(s)) {
    return 'Lowers the minimum missionary service age for single young women from 19 to 18 and updates “temple ordinance worker” to “temple worker.”';
  }
  if (/^Throughout chapter 25\s*,\s*the term “uniting families for eternity”/i.test(s)) {
    return 'Highlights the phrase “uniting families for eternity” across Chapter 25.';
  }
  if (/^Throughout chapter 37\s*,\s*the age range of young single adults/i.test(s)) {
    return 'Expands the young single adult age range across Chapter 37 from 18–30 to 18–35.';
  }
  if (/^Throughout the handbook,\s*many instances of “the United States and Canada”/i.test(s)) {
    return 'Updates references across the handbook so leaders in Canada work with the new Canada Area office rather than Church headquarters.';
  }
  if (/^Throughout the handbook,\s*Young Women “classes” have been updated/i.test(s)) {
    return 'Replaces Young Women “classes” with “age-groups” across the handbook and updates age-group titles.';
  }
  if (/^Revised language throughout the handbook to reflect that family history centers/i.test(s)) {
    return 'Updates terminology across the handbook from family history centers and the Family History Library to FamilySearch centers and the FamilySearch Library.';
  }
  if (/^The phrases “worthily partaking of the sacrament”/i.test(s)) {
    return 'Updates sacrament participation wording across Chapter 26.';
  }
  if (/^The word “recommend” has been changed to “recommendation”/i.test(s)) {
    return 'Changes “recommend” to “recommendation” in Chapter 30 when referring to leadership recommendations for callings.';
  }
  if (/^The term “disfellowshipment” has been changed to “formal membership restrictions”/i.test(s)) {
    return 'Updates remaining references in Chapter 38 from “disfellowshipment” to “formal membership restrictions” and from “disciplinary councils” to “membership councils.”';
  }
  if (/^The chart in this section has been updated to correspond with revisions to chapter 32/i.test(s)) {
    return 'Aligns the leadership review chart with the updated membership council guidelines in Chapter 32.';
  }
  if (/^Temple ordinances for deceased persons are now referred to as “proxy” ordinances/i.test(s)) {
    return 'Adopts the term “proxy” ordinances rather than “vicarious” ordinances for temple work for the dead.';
  }
  if (/^A new section,\s*38\.8\.19/i.test(s)) {
    return 'Adds section 38.8.19 on temple ordinances and service for members with disabilities, renumbering subsequent sections.';
  }

  // Expand bare single-phrase notes ("new section", "section deleted", "revised title", etc.)
  if (/^(new section|new)$/i.test(s)) {
    return `Adds section ${section} (${title}).`;
  }
  if (/^(section deleted|deleted section|deleted)$/i.test(s)) {
    return `Removes section ${section} (${title}).`;
  }
  if (/^(revised title|title revised|title has been revised|updated title|title updated)$/i.test(s)) {
    return `Updates the heading of section ${section} to “${title}.”`;
  }
  if (/^(revised section and title|revised title and section)$/i.test(s)) {
    return `Revises section ${section} and updates its heading to “${title}.”`;
  }
  if (/^(revised section|section revised)$/i.test(s)) {
    return `Revises guidance in section ${section} (${title}).`;
  }
  if (/^(clarified language|revised language|clarified policies)$/i.test(s)) {
    return `Clarifies wording and policy guidance in section ${section} (${title}).`;
  }

  // Transform semicolon-separated editorial fragments into third-person summary clauses
  const clauses = s.split(/\s*;\s*/).map((c) => {
    let cl = c.trim();
    cl = cl
      .replace(/^new section created from\s+/i, 'Splits into a new section from ')
      .replace(/^new section;\s*/i, 'Adds a new section; ')
      .replace(/^new section\b/i, 'Adds a new section')
      .replace(/^new\b/i, 'Adds new section')
      .replace(/^section deleted\b/i, 'Removes section')
      .replace(/^deleted section\b/i, 'Removes section')
      .replace(/^deleted\b/i, 'Removes material')
      .replace(/^new section number\b/i, 'Renumbers section')
      .replace(/^formerly section\s+/i, 'Renumbers from section ')
      .replace(/^previously section\s+/i, 'Renumbers from section ')
      .replace(/^changed section title from\s+/i, 'Renames section from ')
      .replace(/^renamed from\s+/i, 'Renames from ')
      .replace(/^retitled from\s+/i, 'Renames from ')
      .replace(/^title changed from\s+/i, 'Renames section from ')
      .replace(/^title updated from\s+/i, 'Updates section title from ')
      .replace(/^title updated\b/i, 'Updates section title')
      .replace(/^title revised\b/i, 'Revises section title')
      .replace(/^divided section into\s+/i, 'Divides section into ')
      .replace(/^clarified\b/i, 'Clarifies')
      .replace(/^updated\b/i, 'Updates')
      .replace(/^revised\b/i, 'Revises')
      .replace(/^added\b/i, 'Adds')
      .replace(/^removed\b/i, 'Removes')
      .replace(/^moved\b/i, 'Moves')
      .replace(/^some content moved\b/i, 'Moves part of the content')
      .replace(/^content moved\b/i, 'Moves content')
      .replace(/^information moved\b/i, 'Moves guidance')
      .replace(/^combined\b/i, 'Combines')
      .replace(/^consolidated\b/i, 'Consolidates')
      .replace(/^expanded\b/i, 'Expands')
      .replace(/^simplified\b/i, 'Simplifies')
      .replace(/^shortened\b/i, 'Condenses')
      .replace(/^reorganized\b/i, 'Reorganizes')
      .replace(/^restructured\b/i, 'Restructures')
      .replace(/^reformatted\b/i, 'Reformats')
      .replace(/^replaced\b/i, 'Replaces')
      .replace(/^adjusted\b/i, 'Adjusts')
      .replace(/^corrected\b/i, 'Corrects')
      .replace(/^emphasized\b/i, 'Emphasizes')
      .replace(/^addressed\b/i, 'Addresses')
      .replace(/^provided\b/i, 'Provides')
      .replace(/^included\b/i, 'Includes')
      .replace(/^changed\b/i, 'Changes')
      .replace(/^subsequent sections have been renumbered\b/i, 'renumbers following sections')
      .replace(/^subsequent sections renumbered\b/i, 'renumbers following sections');
    return cl;
  });

  let out = clauses.join('; ');
  out = out.charAt(0).toUpperCase() + out.slice(1);
  if (!/[.!?]$/.test(out)) out += '.';
  return out;
}

function parseSnapshotItems(snapshots, overrides) {
  const chaptersMap = overrides.chapters;
  const itemOverrides = overrides.itemOverrides || {};
  const records = [];

  for (const [snapKey, snap] of Object.entries(snapshots)) {
    const blocks = [...snap.html.matchAll(/<(h2|p)[^>]*>([\s\S]*?)<\/\1>/gi)];
    let currentReleaseHeading = null;
    let currentChapter = null;
    let currentChapterTitle = null;

    for (const m of blocks) {
      const tag = m[1].toLowerCase();
      const rawHtml = m[2];
      const txt = cleanText(rawHtml);
      if (!txt) continue;

      if (tag === 'h2') {
        currentReleaseHeading = txt;
        currentChapter = null;
        currentChapterTitle = null;
        continue;
      }

      const relMeta = resolveReleaseMeta(currentReleaseHeading);
      if (!relMeta) continue;

      // Chapter heading paragraph: "Chapter 5: Stake Leadership"
      const chapMatch = txt.match(/^Chapter\s+(\d+):\s+(.*)$/i);
      if (chapMatch) {
        currentChapter = Number(chapMatch[1]);
        currentChapterTitle = chapMatch[2].trim();
        continue;
      }

      // Skip Chapter 38 sub-headers ("Section 38.2: Policies on Ordinances and Blessings")
      // unless the sub-header itself announces a deleted section ("Section 38.9: ... (section deleted)")
      if (/^(Section\s+)?38\.\d+:\s+/i.test(txt) && !/\(section deleted\)/i.test(txt)) {
        continue;
      }

      // Skip standalone continuation paragraphs that explain the immediately preceding item
      if (/^This section has been (renamed and almost completely revised|divided into two new sections)/i.test(txt)) {
        continue;
      }

      // Extract first <a href="..."> in paragraph if present
      const hrefMatch = rawHtml.match(/<a[^>]+href=["']([^"']+)["']/i);
      const rawHref = hrefMatch ? hrefMatch[1] : '';

      // Prose paragraph (chapter-wide or handbook-wide update note)
      const isProse =
        /^(Chapter\s+\d+\b|Throughout\s+(chapter|the\s+handbook)\b|Revised\s+language\s+throughout\s+the\s+handbook\b|A\s+new\s+section,\s*38\.8\.19\b|The\s+(phrases?|word|term|chart)\b|Temple\s+ordinances\s+for\s+deceased\b)/i.test(
          txt
        );

      let section = 'All';
      let title = '';
      let note = '';

      if (isProse) {
        const newSecM = txt.match(/^A\s+new\s+section,\s*(\d+(?:\.\d+)+)\s*,\s*has been added/i);
        if (newSecM) {
          section = newSecM[1];
          title = 'Members with Disabilities';
          note = txt;
        } else if (currentChapter !== null) {
          section = String(currentChapter);
          title = currentChapterTitle ? `Chapter ${currentChapter}: ${currentChapterTitle}` : `Chapter ${currentChapter}`;
          note = txt;
        } else {
          section = 'All';
          title = 'General Handbook (all chapters)';
          note = txt;
        }
      } else {
        const split = splitTrailingNote(txt);
        const head = split.head;
        note = split.note;

        const secMatch = head.match(/^(?:Section\s+)?(\d+(?:\.\d+)*(?:[–-]\d+(?:\.\d+)*)?)\s*[.:]?\s*(.*)$/i);
        if (secMatch) {
          section = secMatch[1].replace(/-/g, '–');
          title = secMatch[2].trim();
        } else if (/^Table:\s+/i.test(head)) {
          section = currentChapter === 32 ? '32.6' : String(currentChapter ?? 'All');
          title = head;
        } else if (currentChapter !== null) {
          section = String(currentChapter);
          title = head;
        } else {
          section = 'All';
          title = head;
        }
      }

      // Determine chapter from currentChapter or leading section number
      let chapter = currentChapter;
      if (chapter === null && /^\d+/.test(section)) {
        chapter = Number(section.split(/[.–-]/)[0]);
      }
      const chapInfo = chapter !== null ? chaptersMap[String(chapter)] : null;
      const chapterTitle = currentChapterTitle || (chapInfo ? chapInfo.title : chapter === null ? 'Handbook-wide' : `Chapter ${chapter}`);

      if (!title) {
        title = chapInfo ? chapInfo.title : `Section ${section}`;
      }

      const ovKey = `${relMeta.date}|${section}`;
      const ov = itemOverrides[ovKey];

      const kind = (ov && ov.kind) || classifyKind(title, note, txt);
      const description = (ov && ov.description) || paraphraseNote(note, title, section, chapter, kind);
      const sectionUrl = normalizeSectionUrl(rawHref, chapter, chaptersMap, relMeta.date);

      records.push({
        date: relMeta.date,
        release: relMeta.release,
        chapter,
        chapterTitle,
        section,
        title,
        kind,
        description,
        sectionUrl,
        announcementUrl: relMeta.announcementUrl,
        source: snap.url,
      });
    }
  }

  // Merge extraRecords from overrides (February 2020 initial release & December 2021 English completion)
  for (const extra of overrides.extraRecords || []) {
    records.push({
      date: extra.date,
      release: extra.release,
      chapter: extra.chapter,
      chapterTitle: extra.chapterTitle,
      section: extra.section,
      title: extra.title,
      kind: extra.kind,
      description: extra.description,
      sectionUrl: extra.sectionUrl,
      announcementUrl: extra.announcementUrl,
      source: extra.source,
    });
  }

  return records;
}

// Compare section numbers in natural dot-numeric order (e.g. 5.2.1 < 5.2.10, "All" first)
function compareSections(a, b) {
  if (a === b) return 0;
  if (a === 'All') return -1;
  if (b === 'All') return 1;
  const pa = a.split(/[.–-]/).map((n) => (Number.isNaN(Number(n)) ? n : Number(n)));
  const pb = b.split(/[.–-]/).map((n) => (Number.isNaN(Number(n)) ? n : Number(n)));
  const len = Math.max(pa.length, pb.length);
  for (let i = 0; i < len; i++) {
    if (pa[i] === undefined) return -1;
    if (pb[i] === undefined) return 1;
    if (pa[i] !== pb[i]) {
      return typeof pa[i] === 'number' && typeof pb[i] === 'number'
        ? pa[i] - pb[i]
        : String(pa[i]).localeCompare(String(pb[i]));
    }
  }
  return 0;
}

function csvCell(v) {
  if (v === null || v === undefined) return '';
  const s = String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

async function main() {
  const overrides = JSON.parse(fs.readFileSync(OVERRIDES_FILE, 'utf8'));
  const snapshots = await loadSnapshots();
  const rawRecords = parseSnapshotItems(snapshots, overrides);

  // Deduplicate identical (date, section, title, description) records if any
  const seenKey = new Set();
  const deduped = [];
  for (const r of rawRecords) {
    const k = `${r.date}|${r.section}|${r.title}|${r.description}`;
    if (seenKey.has(k)) continue;
    seenKey.add(k);
    deduped.push(r);
  }

  // Sort newest release first; within a release, handbook-wide first, then by chapter and section
  deduped.sort((a, b) => {
    const d = b.date.localeCompare(a.date);
    if (d !== 0) return d;
    const ca = a.chapter === null ? -1 : a.chapter;
    const cb = b.chapter === null ? -1 : b.chapter;
    if (ca !== cb) return ca - cb;
    const sc = compareSections(a.section, b.section);
    if (sc !== 0) return sc;
    return a.title.localeCompare(b.title);
  });

  // Assign deterministic IDs
  const idCounts = new Map();
  const changes = deduped.map((r) => {
    const slugSec = r.section.toLowerCase().replace(/[^a-z0-9.]+/g, '-').replace(/^-|-$/g, '') || 'all';
    const baseId = `${r.date}-${slugSec}`;
    const count = (idCounts.get(baseId) || 0) + 1;
    idCounts.set(baseId, count);
    const id = count === 1 ? baseId : `${baseId}-${count}`;
    return { id, ...r };
  });

  // Compute summary aggregations
  const byKind = { new: 0, revised: 0, removed: 0, renumbered: 0 };
  const releaseMap = new Map();
  const chapterCounts = {};

  for (const c of changes) {
    byKind[c.kind] = (byKind[c.kind] || 0) + 1;
    if (!releaseMap.has(c.date)) {
      releaseMap.set(c.date, {
        date: c.date,
        release: c.release,
        count: 0,
        announcementUrl: c.announcementUrl,
      });
    }
    releaseMap.get(c.date).count++;
    const ck = c.chapter === null ? 'all' : String(c.chapter);
    chapterCounts[ck] = (chapterCounts[ck] || 0) + 1;
  }

  const releases = [...releaseMap.values()].sort((a, b) => b.date.localeCompare(a.date));
  const dates = changes.map((c) => c.date).sort();
  const firstDate = dates[0];
  const lastDate = dates[dates.length - 1];

  const payload = {
    name: 'General Handbook of The Church of Jesus Christ of Latter-day Saints — Change Log',
    description:
      'Every published update to the digital General Handbook: Serving in The Church of Jesus Christ of Latter-day Saints since its February 2020 launch, compiled from the Church’s official Summary of Recent Updates (live and archived editions) and Church Newsroom release announcements, with original one-line descriptions.',
    url: 'https://samuelbaird.com/handbook-changes',
    license: 'https://creativecommons.org/licenses/by/4.0/',
    generated: new Date().toISOString().slice(0, 10),
    count: changes.length,
    releaseCount: releases.length,
    firstDate,
    lastDate,
    byKind,
    releases,
    chapters: overrides.chapters,
    byChapter: chapterCounts,
    sources: [
      {
        name: 'The Church of Jesus Christ of Latter-day Saints — General Handbook: Summary of Recent Updates',
        url: LIVE_SUMMARY_URL,
      },
      {
        name: 'Internet Archive Wayback Machine — Historical Snapshots of General Handbook Summary of Recent Updates (2020–2026)',
        url: 'https://web.archive.org/web/*/https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates*',
      },
      {
        name: 'Church Newsroom — General Handbook Release Announcements (2020–2026)',
        url: 'https://newsroom.churchofjesuschrist.org/article/new-general-handbook',
      },
    ],
    fields: {
      id: 'Stable identifier combining the ISO publication date and section number.',
      date: 'ISO 8601 publication date (YYYY-MM-DD) of the General Handbook update release.',
      release: 'Official release label (for example, "October 2026" or "February 2020").',
      chapter: 'General Handbook chapter number (0–38), or null for handbook-wide changes.',
      chapterTitle: 'Chapter title at the time of the update (or "Handbook-wide").',
      section: 'Handbook section number (for example, "38.6.2.1", "24", or "All" for handbook-wide changes).',
      title: 'Section or chapter title.',
      kind: 'Change classification: "new", "revised", "removed", or "renumbered".',
      description: 'Concise one-line summary of the policy or text change in original wording.',
      sectionUrl: 'Official URL of the chapter or section on churchofjesuschrist.org.',
      announcementUrl: 'Official URL of the Church Newsroom release announcement or update summary PDF.',
      source: 'Exact source URL (live summary page, Wayback Machine archive snapshot, or Newsroom release) from which the record was compiled.',
    },
    changes,
  };

  fs.mkdirSync(path.dirname(OUT_JSON), { recursive: true });
  fs.writeFileSync(OUT_JSON, JSON.stringify(payload, null, 2) + '\n');

  const cols = [
    'id',
    'date',
    'release',
    'chapter',
    'chapterTitle',
    'section',
    'title',
    'kind',
    'description',
    'sectionUrl',
    'announcementUrl',
    'source',
  ];
  const lines = [cols.join(',')];
  for (const r of changes) {
    lines.push(cols.map((c) => csvCell(r[c])).join(','));
  }
  fs.writeFileSync(OUT_CSV, lines.join('\n') + '\n');

  console.log(`Wrote ${changes.length} changes across ${releases.length} releases (${firstDate} to ${lastDate}):`, byKind);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
