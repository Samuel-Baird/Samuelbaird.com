"""Benchmark of the Urim agent pipeline (prepare_translation / get_chunk / submit_chunk / finish_translation) on the April 2026
talks, scored against the Church's official translation. The agent is headless Claude Code or OpenAI's Codex CLI.

    mcp/.venv/Scripts/python bench/heldout.py                                            # once: glossary + TM without 2026-04
    python bench/run.py --arm pipeline --agent claude --model haiku --lang es --talks 6
    python bench/run.py --arm pipeline --agent codex --lang es --talks 2                 # same tools, another vendor's agent
    python bench/run.py --score                                    # score everything in bench/out, write results.csv and results.md

Per run it records wall time, API time, turns, tokens (input, output, cache read/write), cost, tool-call counts and
whether the held-out official translation was touched. Scoring compares the output with the Church's official
translation of the same talk (chrF) and checks Church glossary compliance with Urim's own validator.
Only this harness knows about specific agents; the MCP server does not.
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
MODEL = os.environ.get("BENCH_MODEL", "haiku")
URIM_PY = URIM / "mcp" / ".venv" / "Scripts" / "python.exe"
CORPUS_WORDS = 26_228_101          # words in the 12,198 English talks of pulpit-vault (frontmatter excluded)
HELD = HERE / "heldout" / "data" / "glossary"      # glossary rebuilt without the test conference (bench/heldout.py)


def prompt(arm, talk, lang, out):
    t = (HERE / f"{arm}.prompt.md").read_text(encoding="utf-8").strip()
    return t.replace("/ROOT", ROOT.as_posix()).format(talk=talk, language=LANGS[lang][0], out=out.as_posix())


def _type(line):
    try:
        return json.loads(line).get("type")
    except ValueError:
        return None


def leaked(blob, talk, lang):
    """did a tool call touch the held-out official translation of this very talk (its file, or its corpus rows)?"""
    b = blob.replace("\\\\", "/").replace("\\", "/")
    return bool(re.search(rf"talks/{LANGS[lang][1]}/[^\"\s']*{re.escape(talk)}", b)
                or re.search(rf"parallel-corpus-{lang}[^\"]*{re.escape(talk)}", b))


def _mcp_env(arm, tag="", lang="", talk=""):
    env = dict(os.environ)
    env["URIM_HOME"] = str(HERE / "home-pipeline")              # memory seeded with the Church corpus minus the test conference
    env["URIM_GLOSSARY_DIR"] = str(HELD)                        # glossary evidence minus the test conference
    env["URIM_JOBS_DIR"] = str(HERE / "jobs" / f"{tag}-{lang}-{talk}-{int(time.time())}")   # a rerun never resumes an earlier run's job
    return env


def _claude_cmd(arm, talk, lang, out, model):
    cmd = [shutil.which("claude") or "claude", "-p", prompt(arm, talk, lang, out), "--model", model, "--output-format", "stream-json",
           "--verbose", "--no-session-persistence", "--permission-mode", "bypassPermissions"]
    cwd = HERE / "work"                                         # an empty folder: nothing but the urim tools
    cwd.mkdir(exist_ok=True)
    cfg = {"mcpServers": {"urim": {"command": str(URIM_PY), "args": ["-m", "urim_translate"]}}}
    return cmd + ["--strict-mcp-config", "--mcp-config", json.dumps(cfg)], cwd


def _codex_cmd(arm, talk, lang, out, env):
    """OpenAI's Codex CLI with the same tools: only the urim server (the server writes the file itself)."""
    cwd = HERE / "work"
    cwd.mkdir(exist_ok=True)
    srv = "mcp_servers.urim"
    cmd = [shutil.which("codex") or "codex", "exec", "--json", "--skip-git-repo-check", "--sandbox", "read-only",
           "-c", 'approval_policy="never"', "-c", 'model_reasoning_effort="low"',
           "-c", f'{srv}.default_tools_approval_mode="approve"',
           "-c", f"{srv}.command={json.dumps(str(URIM_PY))}", "-c", f'{srv}.args=["-m","urim_translate"]',
           "-c", f"{srv}.env.URIM_HOME={json.dumps(env['URIM_HOME'])}", "-c", f"{srv}.env.URIM_JOBS_DIR={json.dumps(env['URIM_JOBS_DIR'])}",
           "-c", f"{srv}.env.URIM_GLOSSARY_DIR={json.dumps(str(HELD))}",
           prompt(arm, talk, lang, out)]
    return cmd, cwd


def _is_final(agent, line):
    if not line.startswith("{"):
        return False
    t = _type(line)
    return t == "result" if agent == "claude" else t == "turn.completed"


def _metrics_claude(stdout, talk, lang):
    res, tools, leak = {}, Counter(), False
    for line in stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    tools[c["name"]] += 1
                    leak |= leaked(json.dumps(c.get("input", {})), talk, lang)
        elif ev.get("type") == "result":
            res = ev
    u = res.get("usage", {})
    return {"api_s": round(res.get("duration_api_ms", 0) / 1000, 1), "turns": res.get("num_turns"), "input": u.get("input_tokens"),
            "output": u.get("output_tokens"), "cache_read": u.get("cache_read_input_tokens"),
            "cache_write": u.get("cache_creation_input_tokens"), "cost_usd": round(res.get("total_cost_usd", 0), 4),
            "tool_calls": sum(tools.values()), "tools": json.dumps(dict(tools)), "leak": leak, "error": bool(res.get("is_error"))}


def _metrics_codex(stdout, talk, lang):
    """Codex reports tokens but no dollars (ChatGPT subscription) and no API time."""
    tools, msgs, usage, leak = Counter(), 0, Counter(), False
    for line in stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        it = ev.get("item", {})
        if ev.get("type") == "item.completed" and it.get("type") == "mcp_tool_call":
            tools[it.get("tool", "?")] += 1
            leak |= leaked(json.dumps(it.get("arguments", {})), talk, lang)
        elif ev.get("type") == "item.completed" and it.get("type") == "command_execution":
            tools["shell"] += 1
            leak |= leaked(it.get("command", ""), talk, lang)
        elif ev.get("type") == "item.completed" and it.get("type") == "agent_message":
            msgs += 1
        elif ev.get("type") == "turn.completed":
            usage.update({k: v for k, v in ev.get("usage", {}).items() if isinstance(v, int)})
    return {"api_s": "", "turns": msgs + sum(tools.values()), "input": usage["input_tokens"] - usage["cached_input_tokens"],
            "output": usage["output_tokens"], "cache_read": usage["cached_input_tokens"], "cache_write": "",
            "cost_usd": "", "tool_calls": sum(tools.values()), "tools": json.dumps(dict(tools)), "leak": leak, "error": False}


def append_row(row):
    """runs.csv grows new columns over time: rewrite the file with the union header when needed."""
    rp = HERE / "runs.csv"
    lock = HERE / "runs.lock"
    for _ in range(300):                        # one writer at a time: two runs finishing together must not drop a row
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL))
            break
        except FileExistsError:
            time.sleep(0.1)
    try:
        _append(rp, row)
    finally:
        lock.unlink(missing_ok=True)


def _append(rp, row):
    old = list(csv.DictReader(rp.open(encoding="utf-8"))) if rp.exists() and rp.stat().st_size else []
    cols = list(old[0]) if old else []
    cols += [k for k in row if k not in cols]
    with rp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, restval="")
        w.writeheader()
        w.writerows(old + [row])


def run(arm, talk, lang, agent="claude", model=MODEL):
    tag = f"{arm}-claude-{model}" if agent == "claude" else f"{arm}-{agent}"
    out = OUT / tag / lang / f"{talk}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    env = _mcp_env(arm, tag, lang, talk)
    cmd, cwd = _claude_cmd(arm, talk, lang, out, model) if agent == "claude" else _codex_cmd(arm, talk, lang, out, env)
    t0 = time.time()
    lines = []
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
    for line in p.stdout:                       # the MCP server can outlive the agent and hold the pipe open: stop at the final event
        lines.append(line)
        if _is_final(agent, line):
            break
    wall = time.time() - t0
    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)   # this process tree only
    p.stdout.close()
    stdout = "".join(lines)
    RUNS.mkdir(exist_ok=True)
    (RUNS / f"{tag}-{lang}-{talk}.jsonl").write_text(stdout, encoding="utf-8")
    m = (_metrics_claude if agent == "claude" else _metrics_codex)(stdout, talk, lang)
    err = m.pop("error")
    row = {"arm": tag, "lang": lang, "talk": talk, "wall_s": round(wall, 1), **m, "ok": out.exists() and not err,
           "agent": agent, "model": model if agent == "claude" else "codex (account default)"}
    append_row(row)
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


def _claude_leak(tp, talk, lang):
    return any(leaked(json.dumps(c.get("input", {})), talk, lang)
               for l in tp.read_text(encoding="utf-8").splitlines() if l.startswith("{")
               for e in [json.loads(l)] if e.get("type") == "assistant"
               for c in e["message"].get("content", []) if c.get("type") == "tool_use")


def score():
    sys.path.insert(0, str(URIM / "mcp"))
    from urim_translate.translator import Seg, Translator
    tr = Translator()                    # the same full Church glossary judges every arm, whatever each arm could see
    runs = {}
    for r in csv.DictReader((HERE / "runs.csv").open(encoding="utf-8")):
        runs[(r["arm"], r["lang"], r["talk"])] = r                  # the latest run of each wins
    rows = []
    for (arm, lang, talk), r in sorted(runs.items()):
        out = OUT / arm / lang / f"{talk}.md"
        year = talk[:4]
        ref = VAULT / "talks" / LANGS[lang][1] / "modern" / year / f"{talk}.md"
        src = VAULT / "talks" / "english" / "modern" / year / f"{talk}.md"
        row = dict(r)
        tp = RUNS / f"{arm}-{lang}-{talk}.jsonl"
        if tp.exists() and "codex" not in arm:
            row["leak"] = _claude_leak(tp, talk, lang)
        if out.exists() and ref.exists():
            h, rb, sb = body(out), body(ref), body(src)
            g = tr.glossary(lang)
            ms = g.match(sb)
            probs = tr.problems(Seg(sb, masked=sb, matches=ms), h, g)
            row.update(chrf=round(chrf(h, rb) * 100, 1), glossary_terms=len({m.entry.id for m in ms}),
                       glossary_problems=len(probs), length_ratio=round(len(h) / max(len(rb), 1), 2))
        rows.append(row)
    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    with (HERE / "results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, restval="")
        w.writeheader()
        w.writerows(rows)
    table = ["| arm | lang | n | wall s | API s | turns | tool calls | output tok | cost | chrF | glossary problems / terms | length ratio | leaks | est. corpus time, 1 agent | est. corpus cost |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for key in sorted({(r["arm"], r["lang"]) for r in rows}):
        rs = [r for r in rows if (r["arm"], r["lang"]) == key and r.get("chrf") not in (None, "")]
        if not rs:
            continue

        def f(c, fmt="{:.0f}"):
            v = [float(r[c]) for r in rs if r.get(c) not in (None, "")]
            return fmt.format(sum(v) / len(v)) if v else "n/a"
        leaks = sum(1 for r in rs if str(r["leak"]) == "True")
        words = sum(len(body(VAULT / "talks" / "english" / "modern" / r["talk"][:4] / f"{r['talk']}.md").split()) for r in rs)
        secs = sum(float(r["wall_s"]) for r in rs)
        days = secs / words * CORPUS_WORDS / 86400
        costs = [r["cost_usd"] for r in rs if r.get("cost_usd") not in (None, "")]
        ecost = f"${sum(float(c) for c in costs) / words * CORPUS_WORDS:,.0f}" if len(costs) == len(rs) else "n/a"
        table.append(f"| {key[0]} | {key[1]} | {len(rs)} | {f('wall_s')} | {f('api_s')} | {f('turns', '{:.1f}')} | {f('tool_calls', '{:.1f}')} | "
                     f"{f('output')} | {('$' + f('cost_usd', '{:.3f}')) if f('cost_usd') != 'n/a' else 'n/a'} | {f('chrf', '{:.1f}')} | "
                     f"{f('glossary_problems', '{:.1f}')} / {f('glossary_terms')} | {f('length_ratio', '{:.2f}')} | {leaks} | {days:.1f} days | {ecost} |")
    (HERE / "results.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    print("\n".join(table))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["pipeline"], default="pipeline")
    ap.add_argument("--agent", choices=["claude", "codex"], default="claude")
    ap.add_argument("--model", default=MODEL, help="claude model alias (haiku, sonnet...)")
    ap.add_argument("--lang", choices=list(LANGS), default="es")
    ap.add_argument("--talks", type=int, default=1, help="how many of the listed talks")
    ap.add_argument("--start", type=int, default=0, help="index of the first talk")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.score:
        score()
    else:
        for t in TALKS[a.start: a.start + a.talks]:
            run(a.arm, t, a.lang, a.agent, a.model)
