"""python -m urim_translate [serve | seed-tm [--exclude=2026-04] | build-scriptures | status]"""
import json
import sys

from . import config


def seed_tm(langs, exclude=()):
    """Load Church-official, exact-aligned conference paragraph pairs into the translation memory."""
    from .store import Store
    store = Store()
    for lang in langs:
        path = config.PULPIT / "indexes" / f"parallel-corpus-{lang}.jsonl"
        if not path.exists():
            print(f"{lang}: missing {path} (build pulpit-vault's parallel corpus first)")
            continue
        n = 0
        for line in open(path, encoding="utf-8"):
            if '"church_official"' not in line:
                continue
            r = json.loads(line)
            if r["translation_source"] != "church_official" or r.get("alignment_confidence") != "exact":
                continue
            if exclude and r["source_id"].startswith(tuple(exclude)):
                continue
            store.tm_put(lang, r["source_text"], r["target_text"], "church", commit=False)
            n += 1
        store.db.commit()
        print(f"{lang}: seeded {n} Church paragraph pairs")


def main(argv):
    cmd = argv[0] if argv else "serve"
    if cmd == "serve":
        from .server import main as serve
        serve()
    elif cmd == "seed-tm":
        args = argv[1:]
        exclude = [a.split("=", 1)[1] for a in args if a.startswith("--exclude=")]   # e.g. --exclude=2026-04 (held-out talks)
        seed_tm([a for a in args if not a.startswith("--")] or list(config.UI_LANGS), exclude)
    elif cmd == "build-scriptures":
        from . import scriptures
        scriptures.build()
    elif cmd == "status":
        from .translator import Translator
        t = Translator()
        print(json.dumps({"memory": t.store.tm_stats(), "home": str(config.HOME)}, indent=1))
    else:
        print(__doc__)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
