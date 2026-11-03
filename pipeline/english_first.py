"""Earliest English use of each concept in Pulpit's General Conference corpus (1830-present).

Scans every talks/english/**/*.md file with the same longest-match English index the
attestation pass uses. For each concept records the earliest-dated talk containing it,
a short snippet, how many talks use it, and a per-decade count (with decade totals so
the page can show a share). This is English usage in the Pulpit corpus; it says nothing
about translation. Fidelity of each source (verbatim / authoritative_print /
contemporaneous_report / fragmentary ...) is carried through so early, less certain
witnesses are labelled as such.

Output: data/english_first.json
"""
import json
import os
import re
import sys
from collections import defaultdict

from .attest import EnglishIndex, load_concepts
from .config import DATA, PULPIT
from .textutil import window

FIELDS = ("id", "title", "speaker", "conference", "date", "date_precision", "era", "fidelity",
          "source_url", "source_type", "record_type")
FM = re.compile(r"^---\n(.*?)\n---\n", re.S)
KV = re.compile(r"^([a-z_]+):\s*(.*)$", re.M)
FOOT = re.compile(r"\s*\[\^[^\]]+\]")
SOLID = ("verbatim", "authoritative_print")
BAD_HOSTS = ("jod.mrm.org",)   # Pulpit rule: never record this host as provenance


def parse(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    m = FM.match(raw)
    if not m:
        return None, raw
    meta = {}
    for k, v in KV.findall(m.group(1)):
        if k in FIELDS:
            meta[k] = v.strip().strip('"').strip("'")
    return meta, raw[m.end():]


def main():
    concepts = load_concepts()
    idx = EnglishIndex(concepts)
    root = PULPIT / "talks" / "english"
    first = {}
    solid = {}   # earliest hit in a full-text source (verbatim / authoritative_print)
    count = defaultdict(int)
    decades = defaultdict(lambda: defaultdict(int))
    last = {}
    totals = defaultdict(int)
    n = 0
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            meta, body = parse(os.path.join(dirpath, fn))
            if not meta or not meta.get("date"):
                continue
            date = meta["date"]
            year = int(date[:4])
            dec = str(year // 10 * 10)
            totals[dec] += 1
            n += 1
            for slug, (s, e) in idx.scan(body).items():
                count[slug] += 1
                decades[slug][dec] += 1
                key = (date, meta.get("id", fn))
                cur = first.get(slug)
                if cur is None or key < cur[0]:
                    first[slug] = (key, meta, FOOT.sub("", window(body, s, e)))
                if meta.get("fidelity") in SOLID and (slug not in solid or key < solid[slug][0]):
                    solid[slug] = (key, meta, FOOT.sub("", window(body, s, e)))
                if year > last.get(slug, 0):
                    last[slug] = year
            if n % 2000 == 0:
                print(f"  {n} talks", flush=True)

    def rec(meta, snip):
        url = meta.get("source_url", "")
        if any(h in url for h in BAD_HOSTS):
            url = ""
        return {
            "date": meta["date"], "precision": meta.get("date_precision", ""), "id": meta.get("id", ""),
            "title": meta.get("title", ""), "speaker": meta.get("speaker", ""),
            "conference": meta.get("conference", ""), "era": meta.get("era", ""),
            "fidelity": meta.get("fidelity", ""), "record_type": meta.get("record_type", ""),
            "source_url": url, "source_type": meta.get("source_type", ""), "snippet": snip,
        }

    out = {}
    for slug, (key, meta, snip) in first.items():
        out[slug] = {
            "talks": count[slug], "last_year": last[slug], "decades": dict(sorted(decades[slug].items())),
            "first": rec(meta, snip),
        }
        if slug in solid and solid[slug][0] != key:
            out[slug]["first_fulltext"] = rec(solid[slug][1], solid[slug][2])
    (DATA / "english_first.json").write_text(json.dumps(
        {"talks_scanned": n, "decade_totals": dict(sorted(totals.items())), "concepts": out},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"talks scanned: {n}; concepts with English use: {len(out)}")


if __name__ == "__main__":
    sys.exit(main())
