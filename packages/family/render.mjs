// Renders the shared "family" chrome (sidebar, top bar, panorama, colophon) to plain HTML strings,
// so every site ships crawlable links back to samuelbaird.com and to each other without client JS.
// Behaviour (open/close, focus trap, current page) is assets/family.js.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { SITES } from './sites.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
export const DATA = JSON.parse(fs.readFileSync(path.join(HERE, 'projects.json'), 'utf8'));
export const PROJECTS = DATA.projects;
export const OWNER = DATA.owner;
const asset = (f) => fs.readFileSync(path.join(HERE, 'assets', f), 'utf8');

// Latin -> Deseret, word by word, from the Deseret Wiki's phonetic table (unknown words stay Latin).
const WORDS = JSON.parse(fs.readFileSync(path.join(ROOT, 'sites/deseret-wiki/src/data/deseret-words.json'), 'utf8'));
const up = (s) => Array.from(s).map((c) => String.fromCodePoint(c.codePointAt(0) - 0x28)).join('');
export const toDeseret = (t) => t.replace(/[A-Za-z]+(?:['’][A-Za-z]+)*/g, (w) => {
  const d = WORDS[w.toLowerCase()];
  if (!d) return w;
  if (w.length > 1 && w === w.toUpperCase()) return up(d);
  if (w[0] !== w[0].toLowerCase()) { const [a, ...r] = Array.from(d); return up(a) + r.join(''); }
  return d;
});

const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const ext = (href) => /^(https?:|mailto:)/.test(href);
const host = (u) => u.replace(/^https?:\/\//, '').replace(/\/$/, '');
const VIEWBOX = Object.fromEntries([...asset('sprite.svg').matchAll(/<symbol id="([^"]+)" viewBox="([^"]+)"/g)].map((m) => [m[1], m[2]]));
const icon = (id) => {
  if (!VIEWBOX[id]) throw new Error(`icon ${id} is not in assets/sprite.svg`);
  return `<svg viewBox="${VIEWBOX[id]}" aria-hidden="true"><use href="#${id}"/></svg>`;
};

export const FONTS_HREF = 'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Grenze+Gotisch:wght@500;600&display=swap';

/** <head> additions: fonts and the family stylesheet. */
export function renderHead(siteId = 'samuelbaird.com') {
  const bp = SITES[siteId] ? siteBase(siteId).bp : '';
  return `<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="${FONTS_HREF}">
<link rel="preload" href="${bp}/_family/NotoSansDeseret.ttf" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="${bp}/_family/family.css">`;
}

function current(item, pagePath) {
  if (!pagePath || ext(item.href)) return '';
  const p = pagePath.replace(/\/index$/, '/').replace(/(.)\/$/, '$1');
  const h = item.href.replace(/(.)\/$/, '$1');
  return (item.exact ? p === h : p === h || p.startsWith(h + '/')) ? ' aria-current="page"' : '';
}
const link = (item, pagePath, inner) => `<a class="side-link" href="${esc(item.href)}"${current(item, pagePath)}${ext(item.href) ? ' rel="noopener"' : ''}${item.exact ? ' data-exact' : ''}>${inner}</a>`;

/** Where a site lives: its base path on samuelbaird.com ('' for the hub and for other domains). */
export function siteBase(siteId) {
  const s = SITES[siteId];
  const p = PROJECTS.find((x) => x.id === s.project);
  return { bp: p?.basePath || '', onHub: siteId === 'samuelbaird.com' || !!p?.basePath, project: p };
}
// Internal hrefs get the site's base path; samuelbaird.com URLs become root-relative on sites served there.
const localize = (href, bp, onHub) => {
  if (onHub && href.startsWith(OWNER.url)) return href.slice(OWNER.url.length) || '/';
  if (href.startsWith('/')) return href === '/' ? (bp || '/') : bp + href;
  return /^https?:\/\/[^/]+$/.test(href) ? href + '/' : href;
};

/** The sidebar, top bar and panorama. Goes right after <body>. pagePath is the URL path without the base path. */
export function renderTop(siteId, pagePath = '') {
  const s = SITES[siteId];
  if (!s) throw new Error('unknown family site ' + siteId);
  const isHub = siteId === 'samuelbaird.com';
  const { bp, onHub } = siteBase(siteId);
  const here = pagePath ? (pagePath === '/' ? (bp || '/') : bp + pagePath) : '';
  const L = (m) => ({ ...m, href: localize(m.href, bp, onHub) });
  const projects = PROJECTS.map((p) => {
    const cur = p.id === s.project;
    const href = localize(p.url, bp, onHub);
    return `<li><a class="side-link" href="${esc(href)}"${cur ? ' aria-current="true"' : ''}${ext(href) ? ' rel="noopener"' : ''}><i class="bar" style="background:${p.color}"></i><span>${esc(p.name)}</span>${p.role === 'contributor' ? '<small class="side-note">contributor</small>' : ''}</a></li>`;
  }).join('');
  const main = s.main.map(L).map((m) => `<li>${link(m, here, `${icon(m.icon)}<span>${esc(m.label)}</span>`)}</li>`).join('');
  const shelves = (s.shelves || []).map(L).map((m) => `<li>${link(m, here, `<i class="bar" style="background:${m.color}"></i><span>${esc(m.label)}</span>`)}</li>`).join('');
  const home = onHub ? '/' : OWNER.url + '/';
  const all = onHub ? '/projects' : OWNER.projectsUrl;
  const foot = [
    ...(s.foot || []).map(L).map((m) => `<li>${link(m, here, `${icon(m.icon)}<span>${esc(m.label)}</span>`)}</li>`),
    isHub ? '' : `<li><a class="side-link" href="${home}"><svg viewBox="0 0 10 10" aria-hidden="true"><use href="#i-star"/></svg><span>samuelbaird.com</span></a></li>`,
  ].join('');
  const brand = isHub ? 'Samuel Baird' : s.name;
  return `${asset('sprite.svg')}
<button class="fam-toggle iconbtn" type="button" aria-expanded="false" aria-controls="fam-sidebar" aria-label="Open menu"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-panel"/></svg></button>
<div class="fam-scrim" hidden></div>
<aside id="fam-sidebar" class="fam-sidebar" aria-label="Menu" hidden>
  <div class="side-top"><button class="side-close iconbtn" type="button" aria-label="Close menu"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-panel"/></svg></button><span class="side-site">${esc(brand)}</span></div>
  <nav class="side-nav" aria-label="${esc(brand)}">
    <ul class="side-list">${main}</ul>
    ${shelves ? `<p class="side-label">Shelves</p><ul class="side-list">${shelves}</ul>` : ''}
    <p class="side-label">${isHub ? 'Projects' : 'Samuel Baird projects'}</p>
    <ul class="side-list side-projects">${projects}</ul>
    <a class="side-all" href="${all}">All projects &rarr;</a>
  </nav>
  <div class="side-foot"><ul class="side-list">${foot}</ul><p class="side-dsrt" lang="en-Dsrt">${esc(toDeseret(brand))}</p></div>
</aside>
<header class="fam-head">
  <div class="fam-topbar fam-wrap">
    <a class="fam-brand" href="${bp || '/'}" aria-label="${esc(brand)}, home">${asset('seal.svg').replace('class="seal"', 'class="seal fam-seal"')}<span class="fam-brand-name">${esc(brand)}</span></a>
    <a class="fam-family smallcaps" href="${isHub ? '/projects' : home}">${isHub ? 'All projects' : 'A Samuel Baird project'}</a>
  </div>
  <div class="fam-pano">${asset('mountains.svg')}</div>
  <div class="fam-wrap"><div class="rule-double"></div></div>
</header>`;
}

/** Colophon footer and the behaviour script. Goes right before </body>. */
export function renderFoot(siteId) {
  const s = SITES[siteId];
  const isHub = siteId === 'samuelbaird.com';
  const { bp, onHub, project: p } = siteBase(siteId);
  const brand = isHub ? 'Samuel Baird' : s.name;
  const year = new Date().getUTCFullYear();
  const U = (u) => localize(u, bp, onHub);
  const a = (href, text) => `<a href="${esc(href)}"${ext(href) ? ' rel="noopener"' : ''}>${text}</a>`;
  const sisters = PROJECTS.filter((x) => x.kind !== 'page' && x.id !== s.project).map((x) => a(U(x.url), esc(x.name))).join(' · ');
  return `<footer class="fam-foot">
  <div class="fam-wrap">
    <div class="fam-ornament" aria-hidden="true"><svg class="flourish" viewBox="0 0 120 16"><use href="#i-flourish"/></svg><svg class="bee" viewBox="0 0 32 32"><use href="#i-bee"/></svg><svg class="flourish flip" viewBox="0 0 120 16"><use href="#i-flourish"/></svg></div>
    <div class="fam-colophon">
      ${asset('seal.svg').replace('class="seal"', 'class="seal fam-seal-lg"')}
      <div>
        <p class="fam-foot-title">${esc(brand)}</p>
        <p class="fam-foot-dsrt" lang="en-Dsrt">${esc(toDeseret(brand))}</p>
        ${p ? `<p class="small">${esc(p.tagline)} ${p.role === 'contributor' ? 'Samuel Baird is a contributor.' : `Made by ${a(U(OWNER.url), 'Samuel Baird')}.`} Free, independent and ad-free.</p>` : `<p class="small">Data tools and videos about religion, history and ideas. Free, independent and ad-free.</p>`}
        <p class="small fam-foot-links">${a(U(OWNER.url), 'samuelbaird.com')} · ${a(U(OWNER.projectsUrl), 'All projects')}${p ? ` · ${a(U(OWNER.projectsUrl + '/' + p.id), 'About ' + esc(p.name))}` : ''}</p>
        <p class="small fam-foot-links">Also by Samuel Baird: ${sisters}</p>
        <p class="small">&copy; ${year} Samuel Baird. Set in IM Fell English, Libre Baskerville, Cinzel &amp; Noto Sans Deseret, after the ${siteId === 'deseret-wiki' ? 'Deseret Wiki' : a('https://deseret.wiki/', 'Deseret Wiki')}.</p>
      </div>
    </div>
  </div>
</footer>
<script src="${bp}/_family/family.js" defer></script>`;
}

/** Everything a framework site needs, for the generated component. */
export function renderAll(siteId) {
  return { head: renderHead(siteId), top: renderTop(siteId), foot: renderFoot(siteId).replace(/<script[^>]*><\/script>$/, '') };
}

/** Plain data for the Deseret Wiki's own Astro sidebar. */
export function familyData(siteId) {
  const s = SITES[siteId];
  return {
    owner: OWNER,
    projects: PROJECTS.map(({ id, name, url, color, role, kind }) => ({ id, name, url: url + (kind === 'page' ? '' : '/'), color, role, current: id === s.project })),
    about: `${OWNER.projectsUrl}/${s.project}`,
  };
}

export { SITES, host };
