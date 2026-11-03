"""Build the static site, search index, MCP glossary and CSV export from concepts + attestations."""
import csv
import html
import json
import re
import sys
from collections import defaultdict

import yaml

from .config import CONCEPTS, DATA, LANGS, PULPIT, SITE
from .textutil import fold

E = html.escape
LANG_DIR = {"pt": "portuguese", "es": "spanish"}
CHURCH = {"pt": "por", "es": "spa"}
MIN_USES = 3          # an attested rendering needs this many uses to count as "real"
VARY_SHARE = 0.10


def uses(r):
    return r.get("paragraphs", 0) + r.get("verses", 0)


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
FIDELITY = {
    "verbatim": ("verbatim", "Official word-for-word text"),
    "authoritative_print": ("authoritative print", "Officially published record, lightly edited for print"),
    "contemporaneous_report": ("contemporaneous report", "Recorded at the time by a reporter or scribe; the speaker often did not review it"),
    "reconstructed": ("reconstructed", "Assembled from partial witnesses"),
    "fragmentary": ("fragmentary", "Only part of the record survives (often minutes or notes)"),
}
EF = {"concepts": {}, "decade_totals": {}}
FOOTNOTE = re.compile(r"\s*\[\^\d+\]")


def fmt_date(date, precision=""):
    y, _, rest = date.partition("-")
    m, _, d = rest.partition("-")
    if precision == "approximate":
        return f"c. {y}"
    if m.isdigit() and d.isdigit() and precision != "month":
        return f"{int(d)} {MONTHS[int(m) - 1]} {y}"
    if m.isdigit():
        return f"{MONTHS[int(m) - 1]} {y}"
    return y


def fidelity_badge(f):
    label, tip = FIDELITY.get(f, (f or "unknown", ""))
    return f'<span class="badge fid" title="{E(tip)}">{E(label)}</span>'


def good_url(u):
    """A bare host (no path) is not a usable source link."""
    return u if u and not re.fullmatch(r"https?://[^/]+/?", u) else ""


def english_source(rec):
    who = rec["speaker"] if rec["speaker"] and rec["speaker"] != "Conference record" else ""
    title = E(rec["title"])
    u = good_url(rec["source_url"])
    t = f'<a href="{E(u)}">{title}</a>' if u else title
    return f'<b>{E(fmt_date(rec["date"], rec["precision"]))}</b> &middot; {(E(who) + ", ") if who else ""}{t} {fidelity_badge(rec["fidelity"])}'


def decade_chart(first):
    tot = EF["decade_totals"]
    decs = sorted(tot)
    share = {d: first["decades"].get(d, 0) / tot[d] for d in decs}
    top = max(share.values()) or 1
    bars = "".join(
        f'<div class="dbar" title="{d}s: {first["decades"].get(d, 0)} of {tot[d]} talks ({round(share[d] * 100)}%)">'
        f'<i style="height:{max(2, round(share[d] / top * 100)) if share[d] else 0}%"></i><span>{d[2:] if d != "1830" else "30"}</span></div>'
        for d in decs)
    return f'<div class="decades" role="img" aria-label="Share of talks per decade that use this term">{bars}</div>'


def earliest_section(c):
    f = c.get("first")
    if not f:
        return ""
    first = f["first"]
    en = c["en"]["term"]
    out = ['<section class="earliest"><h2>Earliest attested use</h2>'
           '<p class="hint">English use in the General Conference corpus (1830 onward). The earliest witnesses are often minutes or '
           'reconstructions, so the source grade is shown, and early records can include editorial notes as well as a speaker&rsquo;s words. The first full-text source is listed separately when it differs.</p>',
           '<div class="snips">',
           f'<div class="snip"><div class="src">First appearance &middot; {english_source(first)}</div>'
           f'<p>{hl(first["snippet"], c["en"]["match"][0], "en")}</p></div>']
    ft = f.get("first_fulltext")
    if ft:
        out.append(f'<div class="snip"><div class="src">First in a full-text source &middot; {english_source(ft)}</div>'
                   f'<p>{hl(ft["snippet"], c["en"]["match"][0], "en")}</p></div>')
    out.append("</div>")
    out.append(f'<p class="hint">&ldquo;{E(en)}&rdquo; appears in {f["talks"]:,} of {EF["talks_scanned"]:,} talks, most recently in {f["last_year"]}. '
               'Share of each decade&rsquo;s talks that use it:</p>')
    out.append(decade_chart(f))
    out.append("</section>")
    return "".join(out)


def earliest_translation(lang, rs, meta):
    """Earliest official-translation use of each attested rendering (the corpus starts around 1990)."""
    items = []
    for r in rs:
        e = r.get("earliest")
        if not e or "attested" not in r["evidence"]:
            continue
        u = talk_url(lang, e["year"], e["talk"])
        conf = E(e["conference"])
        items.append(f'<li><b lang="{lang}">{E(r["term"])}</b>: {(f"<a href={chr(34)}{E(u)}{chr(34)}>{conf}</a>") if u else conf} '
                     f'<span class="muted">(para. {e["para"] + 1})</span></li>')
    if not items:
        return ""
    top = next((r for r in rs if r.get("earliest")), None)
    pair = ""
    if top:
        e = top["earliest"]
        pair = (f'<div class="snip"><div class="src">Earliest passage for &ldquo;{E(top["term"])}&rdquo;</div><div class="pair">'
                f'<p><span class="l">English</span>{E(re.sub(r"\\s*\\[\\^\\d+\\]", "", e["en"]))}</p>'
                f'<p lang="{lang}"><span class="l">{E(meta["name"])}</span>{hl(e["tr"], top["term"], lang)}</p></div></div>')
    return ('<h3>Earliest official use</h3><p class="hint">First appearance of each rendering in the Church&rsquo;s official translations in this corpus. '
            'Official translations of conference talks begin around 1990, so this shows when a rendering is first <em>recorded here</em>, '
            'not when it was coined.</p><ul class="plainlist">' + "".join(items) + "</ul>" + pair)


def load():
    out = []
    EF.update(json.loads((DATA / "english_first.json").read_text(encoding="utf-8")))
    prov = json.loads((DATA / "provenance.json").read_text(encoding="utf-8"))
    for p in sorted(CONCEPTS.glob("*.yaml")):
        c = yaml.safe_load(p.read_text(encoding="utf-8"))
        a = json.loads((DATA / "attestations" / f"{p.stem}.json").read_text(encoding="utf-8"))
        c["slug"] = p.stem
        c["first"] = EF["concepts"].get(p.stem)
        c["att"] = a
        c["has"] = {l: [r for r in a[l]["renderings"] if r["evidence"]] for l in LANGS}
        c["evidence"] = any(c["has"][l] for l in LANGS)
        out.append(c)
    return out, prov


def talk_url(lang, year, talk_id, cache={}):
    key = (lang, talk_id)
    if key not in cache:
        url = None
        f = PULPIT / "talks" / LANG_DIR[lang] / "modern" / str(year) / f"{talk_id}.md"
        if f.exists():
            head = f.read_text(encoding="utf-8", errors="replace")[:3000]
            m = re.search(r'^source_url:\s*"?([^"\n]+)"?', head, re.M)
            url = m.group(1).strip() if m else None
        cache[key] = url
    return cache[key]


def hl(text, term, lang):
    """Escape and highlight the first match of `term` (inflection-tolerant for pt/es)."""
    from .textutil import target_pattern
    text = re.sub(r"\s*\[\^\d+\]", "", text)
    if not term:
        return E(text)
    f = fold(text)
    m = target_pattern(term).search(f) if lang != "en" else re.search(r"(?<!\w)" + re.escape(fold(term)) + r"\w*", f)
    if not m:
        return E(text)
    return E(text[:m.start()]) + "<mark>" + E(text[m.start():m.end()]) + "</mark>" + E(text[m.end():])


_ICONS = {
    "home": '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h5v-6h4v6h5V10"/>',
    "variants": '<path d="M7 4v13"/><path d="M3 8l4-4 4 4"/><path d="M17 20V7"/><path d="M13 16l4 4 4-4"/>',
    "ai": '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
    "about": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><path d="M12 7.5v.01"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "heart": '<path d="M12 20s-8-5-8-11a4.5 4.5 0 018-2.7A4.5 4.5 0 0120 9c0 6-8 11-8 11z"/>',
    "code": '<path d="M8 8l-5 4 5 4"/><path d="M16 8l5 4-5 4"/><path d="M14 5l-4 14"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
}


def icon(name):
    return ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_ICONS[name]}</svg>')


def _link(href, label, ic, current, ext=False):
    cur = ' aria-current="page"' if href == current else ""
    tgt = ' target="_blank" rel="noopener"' if ext else ""
    return f'<a href="{href}"{cur}{tgt}>{icon(ic)}<span>{label}</span></a>'


def page(title, body, desc, path="", current=""):
    top = [("/", "Atlas", "home"), ("/variants", "Variants", "variants")]
    low = [("/connect", "Use with AI", "ai"), ("/about", "Method &amp; data", "about"),
           ("mailto:ithinksamofficial@gmail.com?subject=Urim", "Contact", "mail"), ("/donate", "Donate", "heart")]
    top_html = "".join(_link(h, n, i, current) for h, n, i in top)
    low_html = ('<button type="button" id="scriptbtn" aria-pressed="false" title="Show English text in the Deseret Alphabet">'
                '<span class="ic glyph" aria-hidden="true">𐐔</span><span>Deseret script</span></button>'
                + "".join(_link(h, n, i, current) for h, n, i in low))
    gh = _link("https://github.com/Samuel-Baird/urim", "Source", "code", current, ext=True)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0f1115">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&family=Noto+Sans+Deseret&display=swap" rel="stylesheet">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='6' fill='%230f1115'/%3E%3Crect x='4' y='4' width='92' height='92' rx='4' fill='none' stroke='%23d9a441' stroke-width='3'/%3E%3Ctext x='50' y='66' font-size='50' text-anchor='middle' fill='%23d9a441' font-family='Georgia,serif' font-weight='600'%3EU%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="/tokens.css">
<link rel="stylesheet" href="/site.css">
<link rel="stylesheet" href="/pages.css">
<link rel="stylesheet" href="/bg/bg.css">
<script src="/bg/glyphwind.js" charset="utf-8" defer></script><script src="/bg/bg.js" defer></script>
<script src="/deseret.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mobilebar">
  <a class="wordmark" href="/" aria-label="Urim, home"><span class="mono" aria-hidden="true">U</span>Urim</a>
  <button type="button" class="menubtn" id="menubtn" aria-expanded="false" aria-controls="sidebar" aria-label="Menu">{icon("menu")}</button>
</header>
<div class="shell">
<aside class="sidebar" id="sidebar">
  <a class="wordmark" href="/" aria-label="Urim, home"><span class="mono" aria-hidden="true">U</span>Urim</a>
  <form class="side-search" action="/" method="get" role="search">{icon("search")}<input type="search" name="q" placeholder="Search&hellip;" aria-label="Search terms" autocomplete="off"></form>
  <nav class="side-nav" aria-label="Main">{top_html}</nav>
  <nav class="side-nav lower" aria-label="More">{low_html}</nav>
  <nav class="side-nav last" aria-label="Source">{gh}</nav>
</aside>
<div class="content">
<main id="main" class="rail">
{body}
</main>
<footer><div class="rail">Urim is an independent project by <a href="https://samuelbaird.com">Samuel Baird</a> and is not affiliated with The Church of Jesus Christ of Latter-day Saints. Evidence is drawn only from Church-published translations.</div></footer>
</div>
</div>
<script src="/nav.js" defer></script>
<script src="/script.js" defer></script>
</body>
</html>
"""


def study_links(c):
    out = []
    s = c.get("sources", {})
    for slug in s.get("GS", []):
        out.append(f'<a href="https://www.churchofjesuschrist.org/study/scriptures/gs/{E(slug)}?lang=eng">Guide to the Scriptures</a>')
    for slug in s.get("Topics", []):
        out.append(f'<a href="https://www.churchofjesuschrist.org/study/manual/gospel-topics/{E(slug)}?lang=eng">Gospel Topics</a>')
    for slug in s.get("TtF", []):
        out.append(f'<a href="https://www.churchofjesuschrist.org/study/manual/true-to-the-faith/{E(slug)}?lang=eng">True to the Faith</a>')
    return out


def badges(r):
    b = []
    if "approved_term" in r["evidence"]:
        b.append('<span class="badge approved" title="On the Church\'s Approved Terms for Interpretation list">approved term</span>')
    if "attested" in r["evidence"]:
        b.append('<span class="badge attested" title="Found in aligned Church text">attested</span>')
    return "".join(b)


def concept_page(c, signals):
    en = c["en"]["term"]
    flags = "".join(f'<span class="flag">{E(f)}</span>' for f in signals.get(c["slug"], []))
    parts = [f'<div class="hero"><p class="crumbs"><a href="/">&larr; Atlas</a></p>'
             f'<p class="eyebrow small-caps">{E(c["category"])}</p><h1>{E(en)}</h1>']
    if flags:
        parts.append(f'<div class="flags">{flags}</div>')
    if c.get("note") and "Pulpit" not in c["note"]:
        parts.append(f'<p class="note">{E(c["note"])}</p>')
    parts.append("</div>")
    parts.append(earliest_section(c))
    for lang, meta in LANGS.items():
        a = c["att"][lang]
        parts.append(f'<section class="lang" id="{lang}"><h2 lang="{lang}">{E(meta["name"])}</h2>')
        rs = c["has"][lang]
        if not rs:
            n = a["en_paragraphs"] + a["en_verses"]
            msg = ("No rendering from this concept's candidate list could be confirmed in aligned Church text."
                   if n else "The English term was not found in the aligned Church texts used for this atlas.")
            parts.append(f'<p class="muted">{msg}</p>')
        else:
            rows = []
            for r in rs:
                span = f'{r["first_year"]}&ndash;{r["last_year"]}' if r.get("first_year") else "&mdash;"
                rows.append(
                    f'<tr><td class="term" lang="{lang}">{E(r["term"])}</td><td>{badges(r)}</td>'
                    f'<td>{r["paragraphs"]} <span class="muted">in {r["talks"]} talks</span><br>{r["verses"]} <span class="muted">scripture verses</span></td>'
                    f'<td>{span}</td><td><div class="bar" title="{round(r["share"]*100)}% of confirmed uses"><i style="width:{round(r["share"]*100)}%"></i></div></td></tr>')
            parts.append('<div class="tablewrap"><table><thead><tr><th>Rendering</th><th>Evidence</th><th>Uses</th><th>Years</th><th>Share</th></tr></thead><tbody>'
                         + "".join(rows) + "</tbody></table></div>")
            parts.append(f'<p class="hint">English term found in {a["en_paragraphs"]} aligned conference paragraphs ({a["en_talks"]} talks) and {a["en_verses"]} scripture verses. {a["uncovered_paragraphs"]} had none of the renderings above.</p>')
            snips = []
            for r in rs[:2]:
                for s in r.get("snippets", []):
                    if s["kind"] == "scripture":
                        src = f'<a href="{E(s["url"])}">{E(s["ref"])}</a> &middot; scripture'
                    else:
                        u = talk_url(lang, s["year"], s["talk"])
                        label = E(s["conference"])
                        src = (f'<a href="{E(u)}">{label}</a>' if u else label) + " &middot; conference talk"
                    snips.append(
                        f'<div class="snip"><div class="src">{src}</div><div class="pair">'
                        f'<p><span class="l">English</span>{hl(s["en"], en if s["kind"] == "talk" else c["en"]["match"][0], "en")}</p>'
                        f'<p lang="{lang}"><span class="l">{E(meta["name"])}</span>{hl(s["tr"], r["term"], lang)}</p></div></div>')
            if snips:
                parts.append('<h3>In the Church&rsquo;s own words</h3><div class="snips">' + "".join(snips) + "</div>")
            parts.append(earliest_translation(lang, rs, meta))
        inf = a.get("inferred", [])
        if inf:
            li = "".join(
                f'<li><b lang="{lang}">{E(i["term"])}</b> &mdash; {i["paragraphs"]} uncovered passages '
                f'({"scripture" if i["kind"] == "scripture" else "conference"}); '
                f'<span class="muted" lang="{lang}">&hellip;{E(re.sub(r"\s*\[\^\d+\]", "", i["sample"]))}&hellip;</span></li>' for i in inf)
            parts.append('<details><summary><span class="badge inferred">inferred</span> Unreviewed candidates from alignment</summary>'
                         '<p class="hint">Mined automatically from Church text where none of the known renderings appeared. '
                         'These are statistical leads, not verified translations, and often include noise.</p>'
                         f'<ul>{li}</ul></details>')
        un = [r["term"] for r in a["renderings"] if not r["evidence"]]
        if un:
            parts.append(f'<p class="hint">Listed in other Church-adjacent glossaries but not confirmed here: <span lang="{lang}">{E(", ".join(un))}</span>.</p>')
        parts.append("</section>")
    sl = study_links(c)
    if sl:
        parts.append('<div class="src-links"><span class="muted">Church study helps (English):</span> ' + " ".join(sl) + "</div>")
    return page(f'{en} in Portuguese and Spanish | Urim', "\n".join(parts),
                f'How the Church translates "{en}" into Portuguese and Spanish, with counts and sources.')


def signals(concepts):
    sig = defaultdict(list)
    collapse = defaultdict(lambda: defaultdict(list))
    for c in concepts:
        for lang in LANGS:
            real = [r for r in c["has"][lang] if "attested" in r["evidence"] and uses(r) >= MIN_USES]
            if len(real) >= 2 and real[1]["share"] >= VARY_SHARE:
                sig[c["slug"]].append(f'varies in {lang}: ' + " / ".join(r["term"] for r in real[:3]))
            for r in real:
                collapse[lang][fold(r["term"])].append((c, r))
    collapses = {}
    for lang, d in collapse.items():
        for k, lst in d.items():
            if len({c["slug"] for c, _ in lst}) >= 2:
                collapses[(lang, k)] = lst
                for c, r in lst:
                    sig[c["slug"]].append(f'shares "{r["term"]}" with other terms ({lang})')
    return sig, collapses


def variants_page(concepts, sig, collapses):
    parts = ['<div class="hero"><p class="eyebrow small-caps">Inconsistency explorer</p><h1>Variants &amp; collisions</h1>'
             '<p class="lede">Where one English term has several Church renderings, where distinct English terms collapse into one, '
             'and where scripture and conference usage diverge. These are observations from published text, not judgments of correctness.</p></div>']
    parts.append('<section><h2>One English term, several renderings</h2>')
    rows = []
    for c in concepts:
        for lang in LANGS:
            real = [r for r in c["has"][lang] if "attested" in r["evidence"] and uses(r) >= MIN_USES]
            if len(real) >= 2 and real[1]["share"] >= VARY_SHARE:
                rows.append(f'<tr><td class="term"><a href="/c/{c["slug"]}#{lang}">{E(c["en"]["term"])}</a></td><td>{lang}</td><td lang="{lang}">'
                            + "; ".join(f'{E(r["term"])} ({uses(r)})' for r in real[:4]) + "</td></tr>")
    parts.append('<div class="tablewrap"><table><thead><tr><th>English</th><th>Lang</th><th>Renderings (uses)</th></tr></thead><tbody>'
                 + ("".join(rows) or '<tr><td colspan="3" class="muted">None found.</td></tr>') + "</tbody></table></div></section>")
    parts.append('<section><h2>Several English terms, one rendering</h2>')
    rows = []
    for (lang, k), lst in sorted(collapses.items(), key=lambda x: -len(x[1])):
        rows.append(f'<tr><td class="term" lang="{lang}">{E(lst[0][1]["term"])}</td><td>{lang}</td><td>'
                    + "; ".join(f'<a href="/c/{c["slug"]}#{lang}">{E(c["en"]["term"])}</a>' for c, _ in lst) + "</td></tr>")
    parts.append('<div class="tablewrap"><table><thead><tr><th>Rendering</th><th>Lang</th><th>English terms</th></tr></thead><tbody>'
                 + ("".join(rows) or '<tr><td colspan="3" class="muted">None found.</td></tr>') + "</tbody></table></div></section>")
    parts.append('<section><h2>Scripture and conference differ (unreviewed)</h2>'
                 '<p class="muted">Concepts where scripture verses contain an unlisted rendering that the miner flagged, next to the conference rendering. Verify before relying on these.</p>')
    rows = []
    for c in concepts:
        for lang in LANGS:
            sc = [i for i in c["att"][lang].get("inferred", []) if i["kind"] == "scripture"]
            top = c["has"][lang][:1]
            if sc and top:
                rows.append(f'<tr><td class="term"><a href="/c/{c["slug"]}#{lang}">{E(c["en"]["term"])}</a></td><td>{lang}</td>'
                            f'<td lang="{lang}">{E(top[0]["term"])}</td><td lang="{lang}">{E(sc[0]["term"])}</td></tr>')
    parts.append('<div class="tablewrap"><table><thead><tr><th>English</th><th>Lang</th><th>Conference</th><th>Scripture lead</th></tr></thead><tbody>'
                 + ("".join(rows) or '<tr><td colspan="4" class="muted">None found.</td></tr>') + "</tbody></table></div></section>")
    return page("Variants & collisions | Urim", "\n".join(parts),
                "Where Church translations of Latter-day Saint terms vary or collapse.", current="/variants")


def about_page(prov, n_all, n_ev):
    s = prov["stats"]
    s_first = EF.get("talks_scanned", 0)
    body = f"""<div class="hero"><p class="eyebrow small-caps">Method &amp; data</p><h1>How Urim works</h1>
<p class="lede">Urim records how the Church&rsquo;s own published translations render Latter-day Saint vocabulary. It does not judge translations; it shows what was published, how often, and where.</p></div>
<section class="prose"><h2>Evidence</h2>
<ul>
<li><b>Conference talks:</b> {s['pt']['talk_pairs_used']:,} Portuguese and {s['es']['talk_pairs_used']:,} Spanish paragraph pairs from official Church translations of General Conference talks, aligned paragraph by paragraph. Pairs whose paragraph counts do not match are excluded, as is any machine-translated text.</li>
<li><b>Scriptures:</b> verse-aligned Church editions of the Bible, Book of Mormon, Doctrine and Covenants and Pearl of Great Price ({s['pt']['scripture_verse_pairs']:,} verses).</li>
<li><b>Approved terms:</b> for Spanish, the Church&rsquo;s &ldquo;Approved Terms for Interpretation&rdquo; list.</li>
</ul>
<h2>Statuses</h2>
<ul>
<li><span class="badge approved">approved term</span> on the Church&rsquo;s approved list.</li>
<li><span class="badge attested">attested</span> found in aligned Church text; counts and snippets link to the official page.</li>
<li><span class="badge inferred">inferred</span> mined automatically, not reviewed. Never treated as verified.</li>
</ul>
<h2>Earliest attested use</h2>
<ul>
<li><b>English:</b> the earliest talk in the General Conference corpus (1830 onward, {s_first:,} talks) that contains the term, plus the earliest in a full-text source (<em>verbatim</em> or <em>authoritative print</em>). Early records are often minutes, notes or reconstructions and can include editorial notes, so each source&rsquo;s grade is shown.</li>
<li><b>Translations:</b> the first appearance of each rendering in the Church&rsquo;s official translations in this corpus. These begin around 1990, so the date means &ldquo;first recorded here&rdquo;, not &ldquo;first coined&rdquo;. Earlier translated usage is not represented.</li>
<li>Matching is by word form, so an early hit may use the word in an ordinary sense rather than as a technical term.</li>
</ul>
<h2>Deseret script</h2>
<p>The sidebar&rsquo;s <b>Deseret script</b> button shows English text on the site in the Deseret Alphabet. It uses the same engine as <a href="https://github.com/Noah-Airmet/pulpit-vault">pulpit-vault</a>&rsquo;s Deseret edition (dictionary spellings, context-resolved heteronyms, 38-letter standard). Words with no spelling stay in Latin script, and Portuguese and Spanish text is never converted. The package is in <a href="https://github.com/Samuel-Baird/urim/tree/main/deseret">deseret/</a>.</p>
<h2>Limits</h2>
<ul>
<li>Counts show published usage, not correctness or doctrine. A rendering that is common in one era may be rare in another.</li>
<li>Matching is by word form and ignores context, so a count can include uses that do not carry the technical sense of the term.</li>
<li>Official translations begin around 1990 for these languages, so earlier talks are not represented.</li>
<li>{n_ev} of {n_all} seeded concepts currently have confirmed evidence in at least one language.</li>
</ul>
<h2>Data</h2>
<p>Built from a snapshot of <a href="https://github.com/Noah-Airmet/pulpit-vault">pulpit-vault</a> (commit <code>{E(prov['pulpit_commit'])}</code>, {E(prov['generated'])}).
Download the table as <a href="/data/urim.csv">CSV</a> or the full index as <a href="/data/index.json">JSON</a>. Source code and pipeline: <a href="https://github.com/Samuel-Baird/urim">github.com/Samuel-Baird/urim</a>.</p>
</section>"""
    return page("Method & data | Urim", body, "How Urim gathers and labels evidence from Church translations.", current="/about")


def home_page(concepts, prov):
    cats = defaultdict(list)
    for c in concepts:
        if c["evidence"]:
            cats[c["category"]].append(c)
    s = prov["stats"]
    chips = "".join(
        f'<div class="cat"><h3 class="small-caps">{E(cat)}</h3><div class="chips">'
        + "".join(f'<a href="/c/{c["slug"]}">{E(c["en"]["term"])}</a>' for c in sorted(lst, key=lambda x: x["en"]["term"].lower()))
        + "</div></div>" for cat, lst in cats.items())
    n = sum(len(v) for v in cats.values())
    body = f"""<div class="hero"><p class="eyebrow small-caps">Mormon Translation Atlas</p>
<h1>How the Church translates its own vocabulary</h1>
<p class="lede">Search a term in English, Portuguese or Spanish and see every rendering the Church has published, with counts, dates and links to the source.</p>
<label class="sr" for="q" style="position:absolute;left:-999px">Search terms</label>
<input id="q" class="search" type="search" placeholder="priesthood, investidura, exaltación…" autocomplete="off" autofocus>
<p class="hint">Try a Portuguese or Spanish word to find the English concept behind it.</p>
<ul id="results" class="results" aria-live="polite"></ul>
<div class="stats">
<div><b>{n}</b><span>concepts with evidence</span></div>
<div><b>{s['pt']['talk_pairs_used'] + s['es']['talk_pairs_used']:,}</b><span>aligned conference paragraphs</span></div>
<div><b>{s['pt']['scripture_verse_pairs']:,}</b><span>scripture verses</span></div>
</div></div>
<section id="browse"><h2>Browse by topic</h2>{chips}</section>
<script src="/search.js" defer></script>"""
    return page("Urim | Mormon Translation Atlas", body,
                "A searchable atlas of how the Church translates Latter-day Saint terms into Portuguese and Spanish.", current="/")


def entry_for(c, lang):
    """Preferred rendering + allowed variants for one concept/language, or None if nothing is known."""
    rs = [r for r in c["has"][lang] if "attested" in r["evidence"] or "approved_term" in r["evidence"]]
    if rs:
        approved = [r for r in rs if "approved_term" in r["evidence"]]
        pref = approved[0] if approved else rs[0]
        return {
            "preferred": pref["term"], "confidence": "approved" if approved else "attested",
            "variants": [{"term": r["term"], "share": r.get("share", 0)} for r in rs
                         if r is not pref and r.get("share", 0) >= VARY_SHARE and uses(r) >= MIN_USES],
            "uses": uses(pref),
        }
    hints = [h for h in c["candidates"].get(lang, []) if h["hint"].startswith("pulpit-glossary")]
    if hints:
        return {"preferred": hints[0]["term"], "confidence": "hint", "variants": [], "uses": 0}
    return None


def glossary(concepts):
    """Per-language machine glossary for the local translation MCP."""
    for lang in LANGS:
        entries = []
        for c in concepts:
            e = entry_for(c, lang)
            if e:
                entries.append({"id": c["id"], "slug": c["slug"], "en": c["en"]["match"],
                                "category": c["category"], **e})
        out = DATA / "glossary"
        out.mkdir(exist_ok=True)
        (out / f"{lang}.json").write_text(json.dumps({"lang": lang, "entries": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"glossary {lang}: {len(entries)} entries "
              f"({sum(e['confidence'] != 'hint' for e in entries)} evidenced)")


def api_data(concepts, sig):
    """Compact read-only dataset for the hosted MCP function (api/mcp.js)."""
    out = []
    for c in concepts:
        langs = {}
        for lang in LANGS:
            e = entry_for(c, lang)
            if not e:
                continue
            langs[lang] = {
                **e,
                "renderings": [{
                    "term": r["term"], "evidence": r["evidence"], "talk_paragraphs": r.get("paragraphs", 0),
                    "talks": r.get("talks", 0), "scripture_verses": r.get("verses", 0),
                    "years": [r.get("first_year"), r.get("last_year")], "share": r.get("share", 0),
                    **({"earliest_official": {k: r["earliest"][k] for k in ("year", "conference", "talk")}}
                       if r.get("earliest") else {}),
                } for r in c["has"][lang]],
            }
        if langs:
            f = c.get("first")
            earliest = {}
            if f:
                def brief(r):
                    return {k: (good_url(r[k]) if k == "source_url" else r[k])
                            for k in ("date", "speaker", "title", "conference", "fidelity", "source_url")
                            if r.get(k) and (k != "source_url" or good_url(r[k]))}
                earliest = {"earliest_english": {"talks": f["talks"], "last_year": f["last_year"], "first": brief(f["first"]),
                                                 **({"first_fulltext": brief(f["first_fulltext"])} if f.get("first_fulltext") else {})}}
            out.append({"slug": c["slug"], "en": c["en"]["match"], "category": c["category"],
                        "flags": sig.get(c["slug"], []), **earliest, **langs})
    (DATA / "api.json").write_text(json.dumps({"concepts": out}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"api.json: {len(out)} concepts")


def scripture_books():
    """English book name -> Church-localized name per language (for deterministic citation rewriting)."""
    from .config import SCRIPTURES
    en = {}
    for line in open(SCRIPTURES["en"], encoding="utf-8"):
        r = json.loads(line)
        en.setdefault(r["book"], r["book_name"])
    out = {n: {} for n in en.values()}
    for lang in LANGS:
        seen = set()
        for line in open(SCRIPTURES[lang], encoding="utf-8"):
            r = json.loads(line)
            if r["book"] in seen or r["book"] not in en:
                continue
            seen.add(r["book"])
            out[en[r["book"]]][lang] = r["book_name"]
    # Church citation convention observed in official pt/es conference text
    for k in ("Doctrine and Covenants", "D&C"):
        out[k] = {"pt": "D&C", "es": "D. y C."}
    (DATA / "scripture_books.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


def publish_deseret():
    """Copy the browser-safe Deseret package files into the site (lazy-loaded by /script.js)."""
    import shutil
    from .config import ROOT
    pkg, out = ROOT / "deseret", SITE / "deseret"
    (out / "lib").mkdir(parents=True, exist_ok=True)
    for f in (pkg / "src").glob("*.mjs"):
        if f.name != "node.mjs":
            shutil.copyfile(f, out / "lib" / f.name)
    for name in ("words.tsv", "heteronyms.json", "overrides.json"):
        shutil.copyfile(pkg / "data" / name, out / name)


def main():
    publish_deseret()
    scripture_books()
    concepts, prov = load()
    sig, collapses = signals(concepts)
    (SITE / "c").mkdir(exist_ok=True)
    (SITE / "data").mkdir(exist_ok=True)
    index = []
    rows = []
    n = 0
    for c in concepts:
        if not c["evidence"]:
            continue
        n += 1
        (SITE / "c" / f'{c["slug"]}.html').write_text(concept_page(c, sig), encoding="utf-8")
        index.append({
            "s": c["slug"], "en": c["en"]["term"], "cat": c["category"],
            "pt": [r["term"] for r in c["has"]["pt"]][:3], "es": [r["term"] for r in c["has"]["es"]][:3],
        })
        for lang in LANGS:
            for r in c["has"][lang]:
                rows.append([c["en"]["term"], c["category"], lang, r["term"], "+".join(r["evidence"]),
                             r.get("paragraphs", ""), r.get("verses", ""), r.get("first_year") or "",
                             r.get("last_year") or "", r.get("share", "")])
    (SITE / "data" / "index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    with open(SITE / "data" / "urim.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["english", "category", "lang", "rendering", "evidence", "talk_paragraphs", "scripture_verses",
                    "first_year", "last_year", "share"])
        w.writerows(rows)
    (SITE / "index.html").write_text(home_page(concepts, prov), encoding="utf-8")
    (SITE / "variants.html").write_text(variants_page(concepts, sig, collapses), encoding="utf-8")
    (SITE / "about.html").write_text(about_page(prov, len(concepts), n), encoding="utf-8")
    from .pages import connect_page, donate_page
    for name, fn in (("connect", connect_page), ("donate", donate_page)):
        t, b, d = fn()
        (SITE / f"{name}.html").write_text(page(t, b, d, current=f"/{name}"), encoding="utf-8")
    glossary(concepts)
    api_data(concepts, sig)
    print(f"pages: {n} concepts, {len(collapses)} collisions")


if __name__ == "__main__":
    sys.exit(main())
