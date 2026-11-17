"""Pages for the proclamations section: a filterable index of language folders, and one page per language.

Built to stay usable at 100+ languages: the index is a compact grid with a live filter, and every document
for a language lives on that language's own page instead of in one long list."""
import html

E = html.escape

ENGLISH_NAMES = {"family": "The Family", "living-christ": "The Living Christ",
                 "restoration": "The Restoration", "articles-of-faith": "The Articles of Faith"}
SHORT = {"letter": "Letter", "a4": "A4", "11x17": "11×17", "18x24": "18×24", "24x36": "24×36",
         "27x40": "27×40", "40x60": "40×60", "a3": "A3", "a2": "A2", "a1": "A1", "a0": "A0"}
FOLDER = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
          'stroke-linejoin="round" aria-hidden="true"><path d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>')

NOTICE = ("<strong>Unofficial.</strong> The text of each language is the Church&rsquo;s own, taken from its website; "
          "the Deseret Alphabet edition is a transliteration of the English. They are typeset with the "
          "<a href=\"https://github.com/Samuel-Baird/urim/tree/main/proclamations\">proclamations generator</a> in this project "
          "and are not published or approved by The Church of Jesus Christ of Latter-day Saints; each PDF says so in its "
          "bottom margin. The Church&rsquo;s own versions, logo and signatures are on its website. "
          "For personal and non-commercial use.")


def _code(entry):
    return "en-Dsrt" if entry["kind"] == "script" else entry["code"]


def _folder(entry):
    n = len(entry["docs"])
    q = " ".join([entry["native"], entry["english"], entry["code"], entry["slug"]]).lower()
    return (f'<li><a class="folder" href="/proclamations/{E(entry["slug"])}" data-q="{E(q)}">{FOLDER}'
            f'<span class="fname"><b lang="{E(_code(entry))}">{E(entry["native"])}</b>'
            f'<small>{E(entry["english"])} &middot; {n} document{"s" if n != 1 else ""}</small></span></a></li>')


def index_page(manifest):
    langs = [e for e in manifest if e["kind"] == "language"]
    scripts = [e for e in manifest if e["kind"] == "script"]
    sections = []
    if langs:
        sections.append(f'<section class="fsec" data-section><h2>Languages <span class="muted">({len(langs)})</span></h2>'
                        f'<ul class="folders">{"".join(_folder(e) for e in langs)}</ul></section>')
    if scripts:
        sections.append(f'<section class="fsec" data-section><h2>Alphabets</h2><p class="muted">The English text written in another alphabet.</p>'
                        f'<ul class="folders">{"".join(_folder(e) for e in scripts)}</ul></section>')
    body = f"""<div class="pagehead">
  <p class="eyebrow small-caps" style="color:var(--honey)">Proclamations</p>
  <h1>Proclamations by language</h1>
  <p class="lede">Choose a language to open its folder. Each one holds the Church&rsquo;s proclamations in that language as PDFs for printing: US Letter and A4, with poster sizes up to A0 on Google Drive.</p>
  <label class="sr" for="lang-filter">Filter languages</label>
  <input id="lang-filter" class="search" type="search" placeholder="Filter languages: español, portuguese, pt&hellip;" autocomplete="off">
  <p class="hint" id="lang-count" aria-live="polite"></p>
</div>
<div class="notice"><p>{NOTICE}</p></div>
{"".join(sections)}
<p class="muted" id="lang-none" hidden>No language matches. Try the English or the native name.</p>
<script src="/pfilter.js" defer></script>"""
    return ("Proclamations by language | Urim", body,
            "The Church's proclamations in many languages, laid out like the official PDFs and sized for printing.")


def _chips(slug, files, posters_url=None):
    def chip(k):
        f = files[k]
        return (f'<a class="chip" href="/posters/{E(slug)}/{E(f["file"])}" download title="{E(f["label"])}, {f["kb"]} KB">'
                f'{E(SHORT[k])}</a>')
    row = f'<div class="sizerow"><span class="small-caps muted">Print</span>{"".join(chip(k) for k in files)}</div>'
    if posters_url:
        row += (f'<div class="sizerow"><span class="small-caps muted">Posters</span>'
                f'<a class="chip" href="{E(posters_url)}" rel="noopener">Poster-size PDFs (Google Drive)</a></div>')
    return row


def language_page(entry):
    slug, code = entry["slug"], _code(entry)
    cards = []
    for doc, d in entry["docs"].items():
        official = (f'<p><a href="{E(d["source_url"])}">Official page on churchofjesuschrist.org</a></p>'
                    if entry["kind"] == "language" else "")
        big = f'/posters/{E(slug)}/{E(d["files"]["letter"]["file"])}'
        cards.append(f"""<article class="pcard" id="{E(doc)}">
  <a class="thumb" href="{big}"><img src="/posters/{E(slug)}/{E(d["preview"])}" width="210" alt="Preview of {E(ENGLISH_NAMES[doc])} in {E(entry["english"])}" loading="lazy"></a>
  <div>
    <h2 lang="{E(code)}">{E(d["title"])}</h2>
    <p class="muted">{E(ENGLISH_NAMES[doc])}</p>
    {official}{_chips(slug, d["files"], entry.get("posters_url"))}
  </div>
</article>""")
    lede = ("The English text written in the Deseret Alphabet." if entry["kind"] == "script"
            else f"The Church&rsquo;s proclamations in {E(entry['english'])}, as PDFs for printing.")
    body = f"""<div class="pagehead">
  <p class="back"><a href="/proclamations">&larr; All languages</a></p>
  <p class="eyebrow small-caps" style="color:var(--honey)">Proclamations</p>
  <h1 lang="{E(code)}">{E(entry["native"])}</h1>
  <p class="lede">{E(entry["english"]) if entry["english"] != entry["native"] else ""}{" &middot; " if entry["english"] != entry["native"] else ""}{lede}</p>
</div>
<div class="notice"><p>{NOTICE}</p></div>
<div class="pgrid">{"".join(cards)}</div>"""
    title = f'Proclamations in {entry["english"]} | Urim'
    return (title, body, f"The Church's proclamations in {entry['english']}, laid out like the official PDFs and sized for printing.")
