"""Agent-driven translation workflow: prepare -> get_chunk -> submit_chunk -> finish.

The calling agent writes the target-language text; everything deterministic happens here: splitting the talk into
chunks at paragraph boundaries, reusing the Church's own paragraphs from the translation memory, filling in the Church's
scripture text for quotations, listing only the glossary terms each chunk needs, and validating what comes back.
No model is called by this module.

Job folder (`<URIM_HOME>/jobs/<job_id>/`): `job.json` (the document skeleton, written once) and
`chunks/NNN.json` (one file per chunk, rewritten atomically, so chunks can be submitted in any order or in parallel).
"""
import hashlib
import json
import os
import re
import time
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from . import config, scriptures, segment
from .textutil import fold

FORMAT = 2                  # bump when the job files change shape: it is part of the job id, so old jobs are never resumed
MAX_WORDS = 450            # target words per chunk (a paragraph is never split)
SOFT_ATTEMPTS = 3          # on this attempt, chunks whose only problems are soft (glossary, numbers, length) are accepted
QUOTE = re.compile(r"“([^”]{12,}?)”|\"([^\"]{12,}?)\"")
FN_AFTER = re.compile(r"^[.,;:!?]{0,2}((?:\[\^\w+\])+)")
URL = re.compile(r"(?<=\]\()[^)\s]+(?=\))|https?://[^\s)\]>]+")
FN_DEF = re.compile(r"^\[\^(\w+)\]:\s*")
FN_REF = re.compile(r"\[\^\w+\]")
TRAIL = re.compile(r"[.,;:!?]+$")
ENGLISH = set("the and of to that is was for with are this his her have has not but they you your their which who "
              "from will would our we be by as it in on at an or".split())
STYLE = {
    "es": "Spanish for Latin America in the formal register of the Church's own translations (address the audience as 'ustedes').",
    "pt": "Brazilian Portuguese in the formal register of the Church's own translations (address the audience as 'vocês').",
}
INSTRUCTIONS = (
    "For each chunk number in `todo`: call get_chunk(job_id, n), translate every line of `source` (one output line per "
    "input line, same order; keep a leading '## ', '- ' or '[^n]: ' marker), then call submit_chunk(job_id, n, translation). "
    "Keep [^n] marks, ids like [[S1]], URLs and scripture citations exactly as written, and use each rendering listed in "
    "`terms`. If submit_chunk reports problems, fix those lines and resubmit only that chunk. Chunks are independent: "
    "translate them in parallel if you can, otherwise one by one. When nothing is left to do, call finish_translation(job_id)."
)


# ---------------------------------------------------------------- small helpers
def _write(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def jobdir(job_id: str) -> Path:
    return config.jobs_dir() / job_id


def _err(msg, hint=""):
    out = {"ok": False, "error": msg}
    if hint:
        out["hint"] = hint
    return out


def _load_job(job_id):
    job_id = str(job_id).strip()
    p = jobdir(job_id) / "job.json"
    if not job_id or not re.fullmatch(r"[\w-]+", job_id) or not p.exists():
        known = sorted(d.name for d in config.jobs_dir().glob("j*") if (d / "job.json").exists())[-5:]
        return None, _err(f"unknown job_id '{job_id}'", "call prepare_translation first" +
                          (f"; recent jobs: {', '.join(known)}" if known else ""))
    return _read(p), None


def _chunk_path(job_id, n):
    return jobdir(job_id) / "chunks" / f"{int(n):03d}.json"


def _load_chunk(job_id, n):
    try:
        p = _chunk_path(job_id, n)
    except (TypeError, ValueError):
        return None, _err(f"chunk number must be an integer, got {n!r}")
    if not p.exists():
        job, _ = _load_job(job_id)
        return None, _err(f"job {job_id} has no chunk {n}", f"chunks are numbered 1 to {job['chunks']}" if job else "")
    return _read(p), None


def _chunks(job_id, count):
    return [_read(_chunk_path(job_id, i)) for i in range(1, count + 1)]


def _pending(c):
    return [ln for ln in c["lines"] if ln["state"] == "pending"]


def _words(s):
    return len(s.split())


# ---------------------------------------------------------------- scripture quotations
def _citations(text):
    """[(localizable match, slug, chapter, [(from, to)])] for the scripture citations in `text`."""
    out = []
    rx = segment.Books.get().rx
    for m in (rx.finditer(text) if rx else ()):
        slug = scriptures.slug_of(m.group(1))
        if slug:
            out.append((m, slug, int(m.group(2)), scriptures.parse_spec(m.group(3))))
    return out


def _candidates(refs):
    """Passages a quotation might reproduce: each cited range, and a citation's ranges joined."""
    for _, slug, ch, ranges in refs:
        for a, b in ranges:
            yield slug, ch, a, b
        if len(ranges) > 1 and all(y + 1 == ranges[i + 1][0] for i, (_, y) in enumerate(ranges[:-1])):
            yield slug, ch, ranges[0][0], ranges[-1][1]


def prepare_line(text, lang, fn_defs, counter, scripture, links):
    """English line -> (shown text, tokens that must survive, partial-quote references).

    Quotations that reproduce a cited Church verse word for word become `[[Sn]]`; the Church's text for it is stored in
    `scripture`. Other citations get the Church's book names. Partial quotations are returned as references."""
    quotes = []

    def link(m):
        counter[1] += 1
        links[f"L{counter[1]}"] = m.group(0)
        return f"[[L{counter[1]}]]"
    text = URL.sub(link, text)                          # long addresses become short ids: fewer tokens, no typos
    if scriptures.available():
        hits = []
        for m in QUOTE.finditer(text):
            g = 1 if m.group(1) is not None else 2
            content, after = m.group(g), text[m.end():m.end() + 60]
            refs, token = [], None
            f = FN_AFTER.match(after)
            if f:
                ids = FN_REF.findall(f.group(1))
                token = ids[0]
                for fid in ids:
                    refs += _citations(fn_defs.get(fid[2:-1], ""))
            else:
                i = re.match(r"^\s*[(—–-]?\s*", after).end()
                refs = _citations(after[i:i + 60])[:1]
                refs = [r for r in refs if r[0].start() == 0]
                token = refs and segment.Books.get().localize(lang, refs[0][0])
            best = None
            for slug, ch, a, b in _candidates(refs):
                en = scriptures.passage("en", slug, ch, a, b)
                contained, ratio, full = scriptures.match_quote(content, en)
                if best is None or (contained, ratio) > best[0]:
                    best = ((contained, ratio), full, slug, ch, a, b)
            if not best or best[0][0] < 0.8 or len(content.split()) < 3:
                continue
            _, full, slug, ch, a, b = best
            church = scriptures.passage(lang, slug, ch, a, b)
            if not church:
                continue
            ref = f"{scriptures.book_name(lang, slug)} {ch}:{a}" + (f"–{b}" if b != a else "")
            hits.append((m.start(g), m.end(g), full, church, ref, token))
        out, pos = [], 0
        for s, e, full, church, ref, token in hits:
            if full:
                tail = TRAIL.search(text[s:e])
                e2 = e - len(tail.group(0)) if tail else e
                counter[0] += 1
                sid = f"S{counter[0]}"
                scripture[sid] = {"ref": ref, "text": church.rstrip(".,;:"), "en": text[s:e2]}
                out.append(text[pos:s] + f"[[{sid}]]")
                pos = e2
            elif token:
                quotes.append({"at": token, "ref": ref, "church_text": church[:700]})
        text = "".join(out) + text[pos:] if out else text
    keep = []
    for rx in segment._PROTECT[:1] + segment._PROTECT[3:]:      # footnote refs, inline code, html tags (links are ids)
        keep += rx.findall(text)
    books = segment.Books.get()
    if books.rx:
        def loc(m):
            s = books.localize(lang, m)
            keep.append(s)
            return s
        text = books.rx.sub(loc, text)
    keep += re.findall(r"\[\[[SL]\d+\]\]", text)
    return text, keep, quotes


def _pure_citation(text, lang):
    """A footnote that is only scripture citations ('Alma 32:21; Moroni 7:41.') -> its localized form, else None."""
    books = segment.Books.get()
    if not books.rx or not books.rx.search(text):
        return None
    if re.sub(r"[\s;,.]+", "", books.rx.sub("", text)):
        return None
    return books.rx.sub(lambda m: books.localize(lang, m), text)


# ---------------------------------------------------------------- prepare
def _front_title(raw):
    m = re.search(r'^title:\s*(.+?)\s*$', raw, flags=re.M)
    if not m:
        return None
    v = m.group(1)
    return v[1:-1] if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'" else v


def prepare(tr, path, lang, output_path="", max_words=MAX_WORDS):
    if lang not in config.UI_LANGS:
        return _err(f"unsupported language '{lang}'", f"use one of: {', '.join(config.UI_LANGS)}")
    p = Path(str(path).strip().strip('"'))
    if not p.is_file():
        return _err(f"file not found: {p}", "pass the path of a markdown or text file")
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return _err(f"cannot read {p}: {type(e).__name__}", "the file must be UTF-8 text")
    if not text.strip():
        return _err("the file is empty")
    try:
        max_words = max(80, int(max_words))
    except (TypeError, ValueError):
        max_words = MAX_WORDS
    g = tr.glossary(lang)
    job_id = "j" + hashlib.sha1(f"{FORMAT}|{p.resolve()}|{output_path}|{lang}|{g.version}|{max_words}|{text}".encode()).hexdigest()[:9]
    if (jobdir(job_id) / "job.json").exists():
        job, _ = _load_job(job_id)
        if output_path:
            job["output_path"] = str(output_path)
            _write(jobdir(job_id) / "job.json", job)
        return _summary(job, resumed=True)

    blocks = segment.split_document(text)
    fn_defs = {}
    for b in blocks:
        if b.is_seg and (m := FN_DEF.match(b.prefix)):
            fn_defs[m.group(1)] = b.text
    counter, scripture, links = [0, 0], {}, {}
    lines, skeleton, title_line = [], [], None
    for i, b in enumerate(blocks):
        if not b.is_seg:
            skeleton.append({"raw": b.raw})
            if i == 0 and b.raw.startswith("---") and (t := _front_title(b.raw)):
                title_line = {"block": 0, "prefix": "", "src": t, "shown": t, "keep": [], "quotes": [], "kind": "title",
                              "state": "pending", "target": None, "origin": None}
            continue
        kind = "footnote" if FN_DEF.match(b.prefix) else "body"
        ln = {"block": i, "prefix": b.prefix, "src": b.text, "kind": kind, "state": "pending", "target": None,
              "origin": None, "keep": [], "quotes": []}
        hit = tr.store.tm_get(lang, b.text)
        cit = _pure_citation(b.text, lang) if kind == "footnote" else None
        if hit and hit[1] == "church":
            ln.update(state="done", target=hit[0], origin="tm:church", shown=b.text)
        elif cit:
            ln.update(state="done", target=cit, origin="citation", shown=b.text)
        else:
            ln["shown"], ln["keep"], ln["quotes"] = prepare_line(b.text, lang, fn_defs, counter, scripture, links)
        skeleton.append({"seg": True, "prefix": b.prefix, "kind": kind})
        lines.append(ln)
    if title_line:
        lines.insert(0, title_line)

    # group lines into chunks: body in order (title first), footnotes apart; never split a paragraph
    groups, cur, words = [], [], 0
    for kind in ("body", "footnote"):
        for ln in [x for x in lines if x["kind"] in (("body", "title") if kind == "body" else ("footnote",))]:
            w = _words(ln["shown"]) if ln["state"] == "pending" else 0
            heading = ln["prefix"].startswith("#")
            if cur and (words + w > max_words or (heading and words >= max_words * 0.6)):
                groups.append(cur)
                cur, words = [], 0
            cur.append(ln)
            words += w
        if cur:
            groups.append(cur)
        cur, words = [], 0
    gl = {}
    for n, grp in enumerate(groups, 1):
        for k, ln in enumerate(grp):
            skel = skeleton[ln["block"]] if ln["kind"] != "title" else None
            if skel:
                skel["chunk"], skel["line"] = n, k
            ln["i"] = k
        terms, seen = [], set()
        for ln in grp:
            if ln["state"] == "pending":
                for m in g.match(ln["shown"]):
                    if m.entry.id not in seen and m.entry.confidence in ("approved", "attested", "user"):
                        seen.add(m.entry.id)
                        terms.append(m.entry.brief())
        pend = [x for x in grp if x["state"] == "pending"]
        for t in terms:
            t.pop("url", None)
            t.pop("confidence", None)
        gl[n] = {"n": n, "terms": terms, "lines": grp, "attempts": 0, "problems": [],
                 "status": "pending" if pend else "done", "words": sum(_words(x["shown"]) for x in pend)}
    job = {"job_id": job_id, "lang": lang, "source_path": str(p.resolve()), "created": time.time(),
           "output_path": str(output_path) if output_path else "", "glossary_version": g.version,
           "chunks": len(groups), "blocks": skeleton, "scripture": scripture, "links": links, "has_title": bool(title_line)}
    for n, c in gl.items():
        _write(_chunk_path(job_id, n), c)
    _write(jobdir(job_id) / "job.json", job)
    return _summary(job)


def _summary(job, resumed=False):
    cs = _chunks(job["job_id"], job["chunks"])
    done = Counter(ln["origin"].split(":")[0] if ln["origin"] else "x" for c in cs for ln in c["lines"] if ln["state"] == "done")
    out = {"ok": True, "job_id": job["job_id"], "lang": job["lang"], "resumed": resumed,
           "chunks": [{"n": c["n"], "words": c["words"], "lines": len(_pending(c)), "status": c["status"]} for c in cs],
           "todo": [c["n"] for c in cs if c["status"] != "done"],
           "already_done": {"lines_from_church_translation_memory": done.get("tm", 0),
                            "footnotes_that_are_only_scripture_citations": done.get("citation", 0),
                            "scripture_quotes_filled_from_church_text": len(job["scripture"])},
           "style": STYLE[job["lang"]], "instructions": INSTRUCTIONS}
    return out


# ---------------------------------------------------------------- get_chunk
def get_chunk(job_id, n):
    job, e = _load_job(job_id)
    if e:
        return e
    c, e = _load_chunk(job["job_id"], n)
    if e:
        return e
    pend = _pending(c)
    quotes = [q for ln in pend for q in ln["quotes"]]
    sids = [s for ln in pend for s in re.findall(r"\[\[(S\d+)\]\]", ln["shown"])]
    out = {"ok": True, "job_id": job["job_id"], "chunk": c["n"], "of": job["chunks"], "lang": job["lang"],
           "status": c["status"], "lines": len(pend), "words": c["words"],
           "source": "\n\n".join(ln["prefix"] + ln["shown"] for ln in pend), "terms": c["terms"]}
    if not pend:
        out["note"] = "nothing to translate here: every line was filled from Church text. No submission needed."
    if any(ln["kind"] == "title" for ln in pend):
        out["note"] = "the first line is the talk title"
    if sids:
        sc = job["scripture"]
        out["scripture"] = [{"id": s, "ref": sc[s]["ref"], "english": sc[s]["en"][:90]} for s in sids]
    if sids or "[[L" in out["source"]:
        out["placeholders_note"] = ("ids like [[S1]] (scripture) and [[L1]] (link address) are filled in automatically: "
                                    "copy each exactly once where it belongs, inside your quotation marks for [[Sn]]")
    if quotes:
        out["quotes"] = quotes
        out["quotes_note"] = ("each item: the words quoted just before `at` come from this Church verse; reuse its "
                              "wording for the same part")
    if c["status"] == "needs_fix":
        out["previous_problems"] = c["problems"]
    return out


# ---------------------------------------------------------------- submit_chunk
def _num_tokens(s, keep):
    for k in sorted(set(keep), key=len, reverse=True):
        s = s.replace(k, " ")
    return Counter(re.findall(r"\d+", s))


def _runs(a, b, k=3):
    """Is there a run of k consecutive words of `a` inside `b`?"""
    a, b = re.findall(r"\w+", fold(a)), " ".join(re.findall(r"\w+", fold(b)))
    return len(a) < k or any(" ".join(a[i:i + k]) in b for i in range(len(a) - k + 1))


def _restore_spaces(ln, target):
    """The Church writes citations like "2 Nefi 33:6" with a non-breaking space. Agents type an ordinary space, which
    looks identical and used to fail the 'keep exactly as written' check. Put the exact token back."""
    for tok in set(ln["keep"]):
        if " " in tok or " " in tok:
            plain = tok.replace(" ", " ").replace(" ", " ")
            if tok not in target:
                target = target.replace(plain, tok)
    return target


def _check(ln, target, tr, lang, g):
    hard, soft, warn = [], [], []
    if not target.strip():
        return ["empty"], soft, warn
    for tok, need in Counter(ln["keep"]).items():
        have = target.count(tok)
        if (tok.startswith(("[[S", "[[L")) and have != need) or have < need:
            shown = tok.replace(" ", " ").replace(" ", " ")
            hard.append(f'keep "{shown}" exactly as written' + (f" ({need}x)" if need > 1 else "")
                        + (f"; found {have}" if have else "; not found"))
    plain = re.sub(r"\[\[[SL]\d+\]\]", " ", ln["shown"])
    words = re.findall(r"[A-Za-z']+", target.lower())
    if len(ln["shown"]) > 40 and SequenceMatcher(None, fold(plain), fold(target)).quick_ratio() > 0.95 \
            and SequenceMatcher(None, fold(plain), fold(target)).ratio() > 0.9:
        hard.append("this line is still the English source; translate it")
    elif len(words) >= 8 and sum(w in ENGLISH for w in words) / len(words) > 0.3:
        hard.append("this line still looks like English; translate it")
    a, b = _num_tokens(ln["shown"], ln["keep"]), _num_tokens(target, ln["keep"])
    if a != b:
        miss, extra = sorted((a - b).elements()), sorted((b - a).elements())
        soft.append("numbers differ from the source" + (f" (missing {', '.join(miss)})" if miss else "")
                    + (f" (extra {', '.join(extra)})" if extra else ""))
    if not _len_ok(plain, target):
        soft.append("length is implausible compared with the source (omission or addition?)")
    for e in g.missing(g.match(ln["shown"]), target):
        soft.append(f'"{e.en[0]}" must be rendered as "{e.preferred}"'
                    + (f' (or: {", ".join(v["term"] for v in e.variants)})' if e.variants else ""))
    for q in ln["quotes"]:
        i = target.find(q["at"])
        if i >= 0 and not _runs(q["church_text"], target[max(0, i - 500):i]):
            warn.append(f'the quotation before {q["at"]} does not follow the Church text of {q["ref"]} (see `quotes`)')
    return hard, soft, warn


def _len_ok(src, tgt):
    from .translator import length_ok
    return length_ok(src, tgt)


def _strip_prefix(s):
    m = segment._LINE_PREFIX.match(s)
    return s[m.end():] if m else s


def submit_chunk(tr, job_id, n, translation):
    job, e = _load_job(job_id)
    if e:
        return e
    c, e = _load_chunk(job["job_id"], n)
    if e:
        return e
    pend = _pending(c)
    if not pend:
        return {"ok": True, "chunk": c["n"], "note": "this chunk needs no translation", **_progress(job)}
    if isinstance(translation, (list, tuple)):
        raw = [str(x) for x in translation]
    elif isinstance(translation, str):
        raw = translation.split("\n")
    else:
        return _err("translation must be text: one line per source line", "send a string, lines separated by newlines")
    got = [x.strip() for x in raw if x.strip()]
    if len(got) != len(pend):
        c["attempts"] += 1
        c["status"], c["problems"] = "needs_fix", [f"expected {len(pend)} lines, got {len(got)}"]
        _write(_chunk_path(job["job_id"], c["n"]), c)
        return {"ok": False, "chunk": c["n"], "attempt": c["attempts"],
                "problems": [{"line": 0, "problem": f"expected exactly {len(pend)} non-empty lines (one per source line, "
                              f"same order), got {len(got)}; do not merge or split paragraphs"}],
                "source_line_starts": [f"{i + 1}: {' '.join(ln['shown'].split()[:5])}" for i, ln in enumerate(pend)],
                "hint": "resubmit all lines of this chunk"}
    lang, g = job["lang"], tr.glossary(job["lang"])
    probs, flags, warns, cleaned = [], [], [], []
    for i, (ln, t) in enumerate(zip(pend, got), 1):
        t = _restore_spaces(ln, _strip_prefix(t))
        hard, soft, warn = _check(ln, t, tr, lang, g)
        cleaned.append(t)
        label = " ".join(ln["shown"].split()[:6])
        probs += [{"line": i, "starts": label, "problem": h, "fix": "required"} for h in hard]
        flags += [{"line": i, "starts": label, "problem": s} for s in soft]
        warns += [{"line": i, "warning": w} for w in warn]
    c["attempts"] += 1
    if probs or (flags and c["attempts"] < SOFT_ATTEMPTS):
        c["status"], c["problems"] = "needs_fix", [x["problem"] for x in probs + flags]
        _write(_chunk_path(job["job_id"], c["n"]), c)
        return {"ok": False, "chunk": c["n"], "attempt": c["attempts"], "problems": probs + flags,
                **({"warnings": warns} if warns else {}),
                "hint": "fix these lines and resubmit all lines of this chunk"
                        + ("" if probs else f"; after attempt {SOFT_ATTEMPTS} a chunk with only these problems is accepted and flagged")}
    for ln, t in zip(pend, cleaned):
        ln.update(state="agent", target=t, origin="agent")
    c["status"], c["problems"] = "done", [x["problem"] for x in flags]
    _write(_chunk_path(job["job_id"], c["n"]), c)
    out = {"ok": True, "chunk": c["n"], **_progress(job)}
    if flags:
        out["accepted_with_issues"] = flags
    if warns:
        out["warnings"] = warns
    return out


def _progress(job):
    todo = [c["n"] for c in _chunks(job["job_id"], job["chunks"]) if c["status"] != "done"]
    return {"remaining": todo, "next": todo[0] if todo else None,
            "hint": "call finish_translation" if not todo else f"{len(todo)} chunk(s) left"}


def job_status(job_id):
    job, e = _load_job(job_id)
    return e or _summary(job, resumed=True)


# ---------------------------------------------------------------- finish
def finish(tr, job_id, output_path="", fill_missing_locally=False):
    job, e = _load_job(job_id)
    if e:
        return e
    lang, jid = job["lang"], job["job_id"]
    cs = _chunks(jid, job["chunks"])
    todo = [c for c in cs if c["status"] != "done"]
    local_lines = 0
    if todo and not fill_missing_locally:
        return {"ok": False, "error": f"{len(todo)} chunk(s) are not translated yet: {[c['n'] for c in todo]}",
                "needs_fix": [c["n"] for c in todo if c["status"] == "needs_fix"],
                "hint": "translate and submit them, or call finish_translation with fill_missing_locally=true "
                        "to use the local backends (Argos/Ollama) for them"}
    if todo:
        lines = [ln for c in todo for ln in c["lines"] if ln["state"] == "pending"]
        segs = tr.translate_segments([ln["src"] for ln in lines], lang)
        for ln, s in zip(lines, segs):
            ln.update(state="local", target=s.target, origin="local:" + (s.origin or "none"), flags=s.flags)
            local_lines += 1
        for c in todo:
            _write(_chunk_path(jid, c["n"]), c)
    by = {(c["n"], ln["i"]): ln for c in cs for ln in c["lines"]}
    sc = job["scripture"]
    out_lines = []
    for sk in job["blocks"]:
        if "raw" in sk:
            out_lines.append(sk["raw"])
        else:
            ln = by[(sk["chunk"], sk["line"])]
            t = ln["target"]
            out_lines.append(sk["prefix"] + t)
    text = "\n".join(out_lines)
    text = re.sub(r"\[\[([SL]\d+)\]\]", lambda m: sc[m.group(1)]["text"] if m.group(1) in sc else
                  job["links"].get(m.group(1), m.group(0)), text)
    tl = next((ln for c in cs for ln in c["lines"] if ln["kind"] == "title"), None)
    if tl and tl["target"] and text.startswith("---"):
        t = tl["target"]
        text = re.sub(r"^title:.*$", lambda m: "title: " + json.dumps(t, ensure_ascii=False), text, count=1, flags=re.M)
        text = re.sub(r"^language:.*$", "language: " + {"es": "spa", "pt": "por"}[lang], text, count=1, flags=re.M)
    left = re.findall(r"\[\[[SL]\d+\]\]", text)
    dest = Path(output_path or job["output_path"] or jobdir(jid) / f"output.{lang}.md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    origin = Counter()
    issues = []
    for c in cs:
        for ln in c["lines"]:
            origin[(ln["origin"] or "").split(":")[0]] += 1
            if ln.get("flags"):
                issues.append({"chunk": c["n"], "line": ln["i"] + 1, "problems": ln["flags"]})
        if c["problems"]:
            issues.append({"chunk": c["n"], "problems": c["problems"]})
    body_start = text.find("\n---\n") + 5 if text.startswith("---") else 0
    return {"ok": not left, "output_path": str(dest), "words": _words(text[body_start:]),
            "chunks": job["chunks"], "lines_by_origin": dict(origin),
            "scripture_quotes_from_church_text": len(sc), "flagged": issues[:10], "flagged_total": len(issues),
            **({"error": f"unfilled scripture ids remain: {left}"} if left else {}),
            "hint": "flagged items were accepted with problems or came from the local backends; review them" if issues else ""}
