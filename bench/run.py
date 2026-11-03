"""Benchmark: Pulpit's own translation instructions vs the Urim MCP, same talks, same model, headless Claude Code.

    python bench/run.py --arm pulpit --lang es --talks 2          # run
    python bench/run.py --arm urim --lang pt --talks 2
    python bench/run.py --score                                    # score everything in bench/out, write results.csv

Per run it records wall time, API time, turns, tokens (input, output, cache read/write), cost, tool-call counts and
whether the held-out official translation was touched. Scoring compares the output with the Church's official
translation of the same talk (chrF) and checks Church glossary compliance with Urim's own validator.
"""
import argparse, csv, json, os, re, shutil, subprocess, sys, time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
URIM = HERE.parent
ROOT = URIM.parent
VAULT = ROOT / "pulpit-vault"
OUT = HERE / "out"
RUNS = HERE / "runs"
LANGS = {"es": ("Spanish", "spanish"), "pt": ("Portuguese", "portuguese")}
TALKS = [                      # April 2026, 1.3k to 1.7k words each, different speakers and themes
    "2026-04-becerra-tithingputting-god-first",
    "2026-04-hall-i-glory-in-my-jesus",
    "2026-04-mutombo-the-joy-of-a-covenant-relationship-with-god",
    "2026-04-wakolo-come-unto-christtogether",
    "2026-04-holmes-jesus-christ-is-the-way",
    "2026-04-eyring-prayers-for-peace",
]
MODEL = os.environ.get("BENCH_MODEL", "sonnet")
URIM_PY = URIM / "mcp" / ".venv" / "Scripts" / "python.exe"


def prompt(arm, talk, lang, out):
    t = (HERE / f"{arm}.prompt.md").read_text(encoding="utf-8").strip()
    return t.replace("/ROOT", ROOT.as_posix()).format(talk=talk, language=LANGS[lang][0], out=out.as_posix())


def run(arm, talk, lang):
    out = OUT / arm / lang / f"{talk}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    cmd = [shutil.which("claude") or "claude", "-p", prompt(arm, talk, lang, out), "--model", MODEL, "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--permission-mode", "bypassPermissions"]
    env = dict(os.environ)
    if arm == "pulpit":
        cwd = VAULT                                             # its CLAUDE.md / AGENTS.md load as in real use
        cmd += ["--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']
    else:
        cwd = HERE / "work"                                     # an empty folder: nothing but the urim tools
        cwd.mkdir(exist_ok=True)
        env["URIM_HOME"] = str(HERE / "home")                   # fresh memory: no Church translations of the test talks
        cfg = {"mcpServers": {"urim": {"command": str(URIM_PY), "args": ["-m", "urim_translate"]}}}
        cmd += ["--strict-mcp-config", "--mcp-config", json.dumps(cfg)]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8")
    wall = time.time() - t0
    RUNS.mkdir(exist_ok=True)
    (RUNS / f"{arm}-{lang}-{talk}.jsonl").write_text(p.stdout, encoding="utf-8")
    res, tools, leak = {}, Counter(), False
    for line in p.stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    tools[c["name"]] += 1
                    blob = json.dumps(c.get("input", {}))
                    if re.search(rf"talks/{LANGS[lang][1]}/[^\"]*{re.escape(talk[:20])}|{re.escape(talk)}.*{LANGS[lang][1]}", blob.replace("\\\\", "/")):
                        leak = True
        elif ev.get("type") == "result":
            res = ev
    u = res.get("usage", {})
    row = {"arm": arm, "lang": lang, "talk": talk, "wall_s": round(wall, 1), "api_s": round(res.get("duration_api_ms", 0) / 1000, 1),
           "turns": res.get("num_turns"), "input": u.get("input_tokens"), "output": u.get("output_tokens"),
           "cache_read": u.get("cache_read_input_tokens"), "cache_write": u.get("cache_creation_input_tokens"),
           "cost_usd": round(res.get("total_cost_usd", 0), 4), "tool_calls": sum(tools.values()),
           "tools": json.dumps(dict(tools)), "leak": leak, "ok": out.exists() and not res.get("is_error")}
    with (HERE / "runs.csv").open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if f.tell() == 0:
            w.writeheader()
        w.writerow(row)
    print(row)


# ---------------------------------------------------------------- scoring
def body(path):
    s = Path(path).read_text(encoding="utf-8")
    s = re.sub(r"\A---\n.*?\n---\n", "", s, flags=re.S)
    return re.sub(r"\s+", " ", s).strip()


def chrf(hyp, ref, n=6, beta=2.0):
    """character n-gram F-score (chrF, whitespace ignored), averaged over n = 1..6"""
    h, r = hyp.replace(" ", ""), ref.replace(" ", "")
    ps, rs = [], []
    for k in range(1, n + 1):
        hc = Counter(h[i:i + k] for i in range(len(h) - k + 1))
        rc = Counter(r[i:i + k] for i in range(len(r) - k + 1))
        m = sum((hc & rc).values())
        ps.append(m / max(sum(hc.values()), 1))
        rs.append(m / max(sum(rc.values()), 1))
    p, rr = sum(ps) / n, sum(rs) / n
    return 0 if p + rr == 0 else (1 + beta ** 2) * p * rr / (beta ** 2 * p + rr)


def score():
    sys.path.insert(0, str(URIM / "mcp"))
    from urim_translate.translator import Seg, Translator
    tr = Translator()
    runs = {}
    rp = HERE / "runs.csv"
    for r in csv.DictReader(rp.open(encoding="utf-8")):
        runs[(r["arm"], r["lang"], r["talk"])] = r                  # the latest run of each wins
    rows = []
    for (arm, lang, talk), r in sorted(runs.items()):
        out = OUT / arm / lang / f"{talk}.md"
        year = talk[:4]
        ref = VAULT / "talks" / LANGS[lang][1] / "modern" / year / f"{talk}.md"
        src = VAULT / "talks" / "english" / "modern" / year / f"{talk}.md"
        row = dict(r)
        if out.exists() and ref.exists():
            h, rb, sb = body(out), body(ref), body(src)
            g = tr.glossary(lang)
            ms = g.match(sb)
            seg = Seg(sb, masked=sb, matches=ms)
            probs = tr.problems(seg, h, g)
            terms = len({m.entry.id for m in ms})
            row.update(chrf=round(chrf(h, rb) * 100, 1), glossary_terms=terms, glossary_problems=len(probs),
                       length_ratio=round(len(h) / max(len(rb), 1), 2))
        rows.append(row)
    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    with (HERE / "results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    # summary per arm and language
    for key in sorted({(r["arm"], r["lang"]) for r in rows}):
        rs = [r for r in rows if (r["arm"], r["lang"]) == key and r.get("chrf") is not None]
        if not rs:
            continue
        f = lambda c: sum(float(r[c]) for r in rs) / len(rs)
        print(f"{key[0]:6} {key[1]}  n={len(rs)}  wall {f('wall_s'):6.0f}s  out {f('output'):7.0f} tok  cost ${f('cost_usd'):.3f}"
              f"  chrF {f('chrf'):.1f}  glossary problems {f('glossary_problems'):.1f}/{f('glossary_terms'):.0f}"
              f"  leaks {sum(1 for r in rs if r['leak'] == 'True')}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["pulpit", "urim"])
    ap.add_argument("--lang", choices=list(LANGS), default="es")
    ap.add_argument("--talks", type=int, default=1, help="how many of the listed talks")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.score:
        score()
    else:
        for t in TALKS[: a.talks]:
            run(a.arm, t, a.lang)
