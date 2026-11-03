"""Run Urim's local route (translate_file: Argos draft + Ollama post-edit) directly, with no agent in the loop.

    URIM_HOME=bench/home-argos python bench/local_run.py urim-argos es 2        # tag, lang, how many talks

Writes bench/out/<tag>/<lang>/<talk>.md and a runs.csv row (no agent tokens or cost). Score with run.py --score.
"""
import sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "mcp"))
import run as bench                                  # noqa: E402
from urim_translate.translator import Translator    # noqa: E402
from urim_translate import segment                   # noqa: E402

tag, lang, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
tr = Translator()
print([(b["backend"], b["available"]) for b in tr.status()])
for talk in bench.TALKS[:n]:
    src = bench.VAULT / "talks" / "english" / "modern" / talk[:4] / f"{talk}.md"
    out = bench.OUT / tag / lang / f"{talk}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    blocks, results = tr.translate_document(src.read_text(encoding="utf-8"), lang)
    out.write_text(segment.join_blocks(blocks), encoding="utf-8")
    row = {"arm": tag, "lang": lang, "talk": talk, "wall_s": round(time.time() - t0, 1), "turns": 0, "tool_calls": 0,
           "leak": False, "ok": True, "agent": "none (direct call)", "model": "local"}
    bench.append_row(row)
    print(row, tr.summarize(results)["origins"])
