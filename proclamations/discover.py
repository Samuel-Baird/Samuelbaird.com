"""Survey which languages the Church has translated the proclamations into, and in which script.

    python -m proclamations.discover            # probe every language in church-languages.yaml
    python -m proclamations.discover --report   # print the saved survey

For each language code on the Church site it requests the four proclamation pages. A missing
translation is a 404; a translated page has a localized title. Results go to language-survey.json.
church-languages.yaml is a snapshot of Pulpit's list of the Church's site languages (150 at the time).
"""
import json
import re
import sys
import unicodedata
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from .fetch_texts import BASE, PAGES

HERE = Path(__file__).resolve().parent
LIST = HERE / "church-languages.yaml"
SURVEY = HERE / "language-survey.json"

# Writing systems by the first word of a Unicode character name
SCRIPT_NAMES = {
    "LATIN": "Latin", "CYRILLIC": "Cyrillic", "GREEK": "Greek", "ARABIC": "Arabic", "HEBREW": "Hebrew",
    "DEVANAGARI": "Devanagari", "BENGALI": "Bengali", "GUJARATI": "Gujarati", "GURMUKHI": "Gurmukhi",
    "TAMIL": "Tamil", "TELUGU": "Telugu", "KANNADA": "Kannada", "MALAYALAM": "Malayalam", "SINHALA": "Sinhala",
    "THAI": "Thai", "LAO": "Lao", "KHMER": "Khmer", "MYANMAR": "Myanmar", "TIBETAN": "Tibetan",
    "GEORGIAN": "Georgian", "ARMENIAN": "Armenian", "ETHIOPIC": "Ethiopic", "HANGUL": "Hangul",
    "HIRAGANA": "Japanese", "KATAKANA": "Japanese", "CJK": "Han",
}


def script_of(text):
    counts = Counter()
    for ch in text:
        if ch.isalpha():
            name = unicodedata.name(ch, "")
            counts[SCRIPT_NAMES.get(name.split(" ")[0], name.split(" ")[0].title())] += 1
    if not counts:
        return "unknown"
    top = [s for s, _ in counts.most_common()]
    if "Japanese" in counts:
        return "Japanese"                  # kana mixed with Han
    return top[0]


def probe(code, slug):
    url = BASE + PAGES[slug] + f"?lang={code}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code}
    except Exception as e:                                           # network trouble: not the same as "not translated"
        return {"ok": None, "error": type(e).__name__}
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S)
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h1.group(1))).strip() if h1 else ""
    return {"ok": bool(title), "title": title, "html_bytes": len(raw)}


def survey():
    langs = yaml.safe_load(LIST.read_text(encoding="utf-8"))
    jobs = [(l["site_code"], slug) for l in langs if not l.get("signed") for slug in PAGES]
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(lambda j: probe(*j), jobs))
    out = {}
    for (code, slug), res in zip(jobs, results):
        e = out.setdefault(code, {"code": code, "name": next(l["name"] for l in langs if l["site_code"] == code), "docs": {}})
        e["docs"][slug] = res
    for e in out.values():
        titles = [d["title"] for d in e["docs"].values() if d.get("ok")]
        e["documents"] = sum(1 for d in e["docs"].values() if d.get("ok"))
        e["script"] = script_of(" ".join(titles)) if titles else None
    SURVEY.write_text(json.dumps(list(out.values()), indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    return list(out.values())


def report(data):
    done = [e for e in data if e["documents"]]
    print(f"{len(done)} of {len(data)} languages have at least one proclamation; "
          f"{sum(1 for e in data if e['documents'] == 4)} have all four.")
    by_script = {}
    for e in done:
        by_script.setdefault(e["script"], []).append(e)
    for script, es in sorted(by_script.items(), key=lambda kv: -len(kv[1])):
        print(f"\n{script} ({len(es)}):")
        for e in sorted(es, key=lambda e: e["name"]):
            print(f"  {e['code']:9} {e['name']:32} {e['documents']}/4")
    errors = [(e["code"], s) for e in data for s, d in e["docs"].items() if d.get("ok") is None]
    if errors:
        print("\nnetwork errors (retry):", errors[:10])


if __name__ == "__main__":
    data = json.loads(SURVEY.read_text(encoding="utf-8")) if "--report" in sys.argv else survey()
    report(data)
