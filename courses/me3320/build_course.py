"""Assemble courses/me3320/course.json.

usage: python courses/me3320/build_course.py [--verify-videos]

Inputs : content.py (hand-written study content), problems/part*.py (computed practice problems),
         textbook/toc.json (section / example page map made by scripts/build_toc.py).
Output : course.json  (published by scripts/publish.mjs to Samuelbaird.com/learn/me3320/)
No textbook text and no instructor-file text is written into the output; only section/page references and links.
"""
import json, os, re, sys, datetime, concurrent.futures, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "problems"))

import content as C                       # noqa: E402
import learning as LR                     # noqa: E402  (recall cards, review links, method labels, contrasts)
import part1, part2, part3, warmups       # noqa: E402

toc = json.load(open(os.path.join(HERE, "textbook", "toc.json"), encoding="utf-8"))
sec_info = {s["sec"]: s for c in toc["chapters"] for s in c["sections"]}
ex_by_sec = {}
for e in toc["examples"]:
    ex_by_sec.setdefault(e["sec"], []).append(e)

problems = {}
for mod in (part1, part2, part3):
    problems.update(mod.build())

assert not [u["id"] for u in C.UNITS if u["id"] not in problems], "unit without problems"

# warm-ups go first in their unit: easy single-idea problem, then the exam-style ones (playbook rule 5)
for uid, lst in warmups.build().items():
    problems[uid] = lst + problems[uid]
for lst in problems.values():
    for p in lst:
        assert p["id"] in LR.METHODS, f"no method label for {p['id']}"
        p["method"] = LR.METHODS[p["id"]]
assert set(LR.METHODS) == {p["id"] for lst in problems.values() for p in lst}, "method label for a missing problem"
unit_order = {u["id"]: i for i, u in enumerate(C.UNITS)}
owner = {p["id"]: uid for uid, lst in problems.items() for p in lst}
for uid, ids in LR.REVIEW.items():
    for pid in ids:
        assert pid in owner and unit_order[owner[pid]] < unit_order[uid], f"review {pid} in {uid} must come from an earlier unit"
assert set(LR.RECALL) == {u["id"] for u in C.UNITS}, "every unit needs recall cards"


def canvas_links(unit):
    files = [{"label": C.F[k][1], "url": f"{C.CANVAS}/files/{C.F[k][0]}"} for k in unit.get("files", [])]
    hws = [{"label": C.HW[n][0], "url": f"{C.CANVAS}/assignments/{C.HW[n][1]}", "due": C.HW[n][2]} for n in unit.get("hw", [])]
    return {"files": files, "hw": hws}


units = []
for i, u in enumerate(C.UNITS, 1):
    book = [{"sec": s, "title": sec_info[s]["title"], "page": sec_info[s]["printed"]} for s in u["sections"] if s in sec_info]
    exs = []
    for s in u["sections"]:
        for e in ex_by_sec.get(s, []):
            exs.append({"ex": e["ex"], "page": e["printed"]})
    units.append({
        "id": u["id"], "num": i, "ch": u["ch"], "title": u["title"], "tag": u["tag"], "sched": u["sched"],
        "why": u["why"], "sections": u["sections"], "book": book, "examples": exs,
        "videos": [{"id": v[0], "title": v[1], "channel": v[2], "len": v[3], "note": v[4]} for v in u["videos"]],
        "know": u["know"], "eq": [{"label": a, "tex": b} for a, b in u["eq"]], "pitfalls": u["pitfalls"],
        "tables": u.get("tables", []), "samples": u["samples"], "canvas": canvas_links(u),
        "recall": [{"q": q, "a": a} for q, a in LR.RECALL[u["id"]]],
        "review": LR.REVIEW.get(u["id"], []),
        "problems": problems[u["id"]],
    })

all_ids = [p["id"] for u in units for p in u["problems"]]
assert len(all_ids) == len(set(all_ids)), "duplicate problem ids"
for m in C.MOCKS:
    for pid in m["problems"]:
        assert pid in all_ids, f"mock references missing problem {pid}"

course = {
    "id": "me3320", "title": "ME 3320 Heat Transfer", "term": "Fall 2026",
    "text": "Fundamentals of Heat and Mass Transfer, 8th ed. (Bergman, Lavine, Incropera, DeWitt)",
    "pageOffset": toc["offset"],
    "canvas": C.CANVAS,
    "dates": {
        "test1": {"label": "Test 1", "when": "2026-10-09T23:59:00-06:00", "done": True},
        "test2": {"label": "Test 2", "when": "2026-11-13T23:59:00-07:00", "done": False},
        "final": {"label": "Final (in class, comprehensive)", "when": "2026-12-08T13:00:00-07:00", "done": False, "where": "SE-326, 1:00–2:50 pm"},
    },
    "tests": {
        "T2": ["Ch 4: §4.3 + Table 4.1 first four cases; finite difference (§4.4–4.5)",
               "Ch 5: §5.1, 5.2, 5.4, 5.5 with first half of Table 5.1; finite-difference transient",
               "Ch 6: §6.1–6.7, Tables 6.1–6.3, the four boundary-layer equations",
               "Know area/volume of a sphere and cylinder; average quantities; conservation of mass and energy"],
    },
    "units": units,
    "mocks": C.MOCKS,
    "tableGuide": [{"need": a, "where": b} for a, b in C.TABLE_GUIDE],
    "mistakes": C.COMMON_MISTAKES,
    "contrasts": LR.CONTRASTS,
    "routine": LR.ROUTINE,
    "policy": "Built from concepts, videos and original practice problems only. It contains no solutions to assigned homework or test problems. "
              "The syllabus allows AI for finding information and brainstorming, and forbids it on tests, quizzes and for solving assigned work.",
    "generated": datetime.date.today().isoformat(),
}

# ---- validation ----
txt = json.dumps(course, ensure_ascii=False)
assert "<<" not in txt, "unfilled placeholder left in course.json"
for u in units:
    assert u["videos"] and u["know"] and u["eq"] and u["problems"], u["id"]
    for p in u["problems"]:
        assert p["solution"]["steps"] and p["solution"]["answers"], p["id"]
        assert "nan" not in " ".join(p["solution"]["answers"]).lower().split(), p["id"]

# ---- optional: verify each video exists and is embeddable ----
if "--verify-videos" in sys.argv:
    vids = {v["id"]: v for u in units for v in u["videos"]}

    def check(vid):
        url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}", safe="")
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "course-builder"}), timeout=20) as r:
                j = json.load(r)
                return vid, True, j.get("title", ""), j.get("author_name", "")
        except Exception as e:  # 401 = embedding disabled, 404 = missing
            return vid, False, str(e), ""
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        results = list(ex.map(check, vids))
    bad = [r for r in results if not r[1]]
    for vid, ok, title, author in results:
        vids[vid]["verified"] = ok
        if ok:
            vids[vid]["ytTitle"], vids[vid]["ytAuthor"] = title, author
    print(f"videos: {len(results)-len(bad)}/{len(results)} verified")
    for b in bad:
        print("  BAD", b[0], b[2])
    # drop unembeddable / missing videos from the published data
    for u in units:
        u["videos"] = [v for v in u["videos"] if v.get("verified", True)]
        assert u["videos"], f"{u['id']} has no working videos"

out = os.path.join(HERE, "course.json")
json.dump(course, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"wrote {out}: {len(units)} units, {len(all_ids)} practice problems, {sum(len(u['videos']) for u in units)} videos, {os.path.getsize(out)//1024} KB")
