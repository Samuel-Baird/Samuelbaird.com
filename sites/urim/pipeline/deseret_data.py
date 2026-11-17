"""Build the Deseret package's data and vendored modules from a pulpit-vault checkout.

Pulpit's Deseret engine (docs/deseret.md) resolves English words to Deseret spellings in
two stages. Stage A (CMUdict + G2P, offline) produced indexes/deseret/wordlist.tsv; stage B
(this package's runtime) only looks words up and resolves a few heteronyms by context. We
vendor stage B and its data. Nothing here invents a pronunciation.

Writes:
  deseret/data/words.tsv        word <TAB> deseret <TAB> confident(1|0)
  deseret/data/heteronyms.json  schema/deseret/heteronyms.yaml as JSON
  deseret/data/PROVENANCE.json  pulpit commit, counts
  deseret/src/{arpabet,case,tokens,schwa,html,heteronyms}.mjs  vendored with a header
"""
import json
import subprocess
import sys

import yaml

from .config import PULPIT, ROOT

PKG = ROOT / "deseret"
VENDORED = ["arpabet", "case", "tokens", "schwa", "html", "heteronyms"]
LF = chr(10)


def write(path, text):
    """Always LF, so the data parses identically on every platform."""
    with open(path, "w", encoding="utf-8", newline=LF) as fh:
        fh.write(text.replace(chr(13) + LF, LF))


def main():
    commit = subprocess.run(["git", "-C", str(PULPIT), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    (PKG / "data").mkdir(parents=True, exist_ok=True)
    (PKG / "src").mkdir(parents=True, exist_ok=True)

    rows, conf = [], 0
    with open(PULPIT / "indexes" / "deseret" / "wordlist.tsv", encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            cells = line.rstrip("\r\n").split("\t")
            if len(cells) < 5 or not cells[2]:
                continue
            word, deseret, confident = cells[0], cells[2], cells[4] == "true"
            rows.append((word, deseret, "1" if confident else "0"))
            conf += confident
    rows.sort()
    write(PKG / "data" / "words.tsv", LF.join("\t".join(r) for r in rows) + LF)

    spec = yaml.safe_load((PULPIT / "schema" / "deseret" / "heteronyms.yaml").read_text(encoding="utf-8"))
    write(PKG / "data" / "heteronyms.json", json.dumps(spec, ensure_ascii=False, indent=1))

    for name in VENDORED:
        src = (PULPIT / "scripts" / "deseret" / f"{name}.mjs").read_text(encoding="utf-8")
        header = (f"// Vendored from pulpit-vault scripts/deseret/{name}.mjs @ {commit}.{LF}"
                  f"// Do not edit here: regenerate with `python -m pipeline.deseret_data`. See deseret/README.md.{LF}")
        write(PKG / "src" / f"{name}.mjs", header + src)

    write(PKG / "data" / "PROVENANCE.json", json.dumps({
        "pulpit_commit": commit, "words": len(rows), "confident_words": conf,
        "heteronym_entries": len([k for k, v in spec.items() if isinstance(v, dict) and v.get("senses")]),
        "source": "pulpit-vault indexes/deseret/wordlist.tsv and schema/deseret/heteronyms.yaml",
    }, indent=1))
    print(f"words: {len(rows)} ({conf} confident); vendored {len(VENDORED)} modules @ {commit}")


if __name__ == "__main__":
    sys.exit(main())
