"""Unit tests for the clips type's planner (docs/types/clips.md):
clips.yaml lint, the numbered review doc, the approval gate, and the
Resolve build plan / caption SRTs.

    python -m pytest tools/tests/test_clips_plan.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import clips_plan as cp  # noqa: E402

# Two sentences, one word per second: "w0 w1 ... w4." then "w5 ... w9."
WORDS = [{"word": f"w{i}" + ("." if i in (4, 9) else ""), "start": float(i), "end": i + 0.8}
         for i in range(10)]
SEGMENTS = [
    {"start": 0.0, "end": 4.8, "text": " w0 w1 w2 w3 w4.", "words": WORDS[:5]},
    {"start": 5.0, "end": 9.8, "text": " w5 w6 w7 w8 w9.", "words": WORDS[5:]},
]


def _project(tmp_path: Path, plan: dict) -> Path:
    (tmp_path / "script").mkdir()
    (tmp_path / "transcripts").mkdir()
    (tmp_path / "transcripts" / "source.json").write_text(
        json.dumps({"segments": SEGMENTS}), encoding="utf-8")
    (tmp_path / "script" / "clips.yaml").write_text(yaml.safe_dump(plan), encoding="utf-8")
    return tmp_path


def _plan(**over) -> dict:
    doc = {"slug": "ep", "source": {"title": "Ep", "creator": "Show"}, "min_seconds": 1,
           "max_seconds": 90,
           "clips": [{"id": "c01", "title": "First", "start": 0.0, "end": 4.9, "why": "hook"},
                     {"id": "c02", "title": "Second", "start": "00:05.0", "end": "00:09.9"}]}
    doc.update(over)
    return doc


def _lint(doc: dict) -> list[cp.Issue]:
    doc = {**{"format": "vertical", "captions": "burned", "min_seconds": 1, "max_seconds": 90}, **doc}
    issues: list[cp.Issue] = []
    clips = cp.parse_clips(doc, issues)
    return issues + cp.validate(doc, clips, WORDS, 9.8)


def _msgs(issues, level) -> list[str]:
    return [i.message for i in issues if i.level == level]


def test_parse_time_forms():
    assert cp.parse_time(12) == 12.0
    assert cp.parse_time("01:02.5") == 62.5
    assert cp.parse_time("1:00:00") == 3600.0


def test_clean_plan_has_no_issues():
    assert _lint(_plan()) == []


def test_mid_word_and_mid_sentence_are_warned():
    doc = _plan(clips=[{"id": "c01", "title": "x", "start": 0.4, "end": 3.5}])
    warns = _msgs(_lint(doc), "warn")
    assert any("splits the word 'w0'" in m for m in warns)
    assert any("ends mid-sentence" in m for m in warns)


def test_past_source_end_and_bad_cut_are_errors():
    doc = _plan(clips=[{"id": "c01", "title": "x", "start": 0, "end": 20, "cuts": [[19, 25]]}])
    errs = _msgs(_lint(doc), "error")
    assert any("past the source" in m for m in errs)
    assert any("strictly inside" in m for m in errs)


def test_duplicate_ids_and_bad_reframe():
    doc = _plan(clips=[{"id": "a", "start": 0, "end": 4.9, "reframe": "up"},
                       {"id": "a", "start": 5, "end": 9.9}])
    errs = _msgs(_lint(doc), "error")
    assert any("duplicate" in m for m in errs)
    assert any("reframe" in m for m in errs)


def test_vertical_hard_ceiling():
    doc = _plan(clips=[{"id": "c01", "start": 0, "end": 200}])
    issues: list[cp.Issue] = []
    d = {"format": "vertical", "captions": "burned", "min_seconds": 1, "max_seconds": 90, **doc}
    clips = cp.parse_clips(d, issues)
    errs = _msgs(cp.validate(d, clips, WORDS, 300.0), "error")
    assert any("vertical-platform ceiling" in m for m in errs)


def test_cuts_shorten_duration_and_rebase_time():
    c = cp.parse_clips({"clips": [{"start": 0, "end": 10, "cuts": [[2, 4]]}]}, [])[0]
    assert c.kept == [(0, 2), (4, 10)]
    assert c.duration == 8
    assert c.to_clip_time(5.0) == 3.0


def test_approval_requires_written_words():
    clips = cp.parse_clips(_plan(), [])
    issues: list[cp.Issue] = []
    assert cp.approved_numbers({"approval": {"clips": [1]}}, clips, issues) == []
    assert any("written words" in i.message for i in issues)
    ok = {"approval": {"date": "2026-10-17", "words": "approve 2", "clips": [2]}}
    assert cp.approved_numbers(ok, clips, []) == [2]
    allv = {"approval": {"date": "2026-10-17", "words": "approved", "clips": "all"}}
    assert cp.approved_numbers(allv, clips, []) == [1, 2]
    bad: list[cp.Issue] = []
    cp.approved_numbers({"approval": {"date": "d", "words": "w", "clips": [7]}}, clips, bad)
    assert any("doesn't exist" in i.message for i in bad)


def test_review_doc_numbers_clips_and_ends_with_marked_transcript(tmp_path):
    proj = _project(tmp_path, _plan())
    sys.argv = ["clips_plan.py", "--project", str(proj)]
    assert cp.main() == 0
    md = (proj / "script" / "clips.md").read_text(encoding="utf-8")
    assert "## 01. First (~4.9s)" in md and "## 02. Second (~4.9s)" in md
    full = md.index("## Full source transcript")
    assert md.index("## 02.") < full
    tail = md[full:]
    assert tail.index("▶ Clip 01 starts") < tail.index("w0 w1") < tail.index("■ Clip 01 ends") \
        < tail.index("▶ Clip 02 starts") < tail.index("w5 w6") < tail.index("■ Clip 02 ends")


def test_build_plan_refuses_without_approval(tmp_path):
    proj = _project(tmp_path, _plan())
    sys.argv = ["clips_plan.py", "--project", str(proj), "--build-plan",
                "--fps", "30", "--source-size", "1920x1080"]
    assert cp.main() == 1
    assert not (proj / "script" / "clips.build.json").exists()


def test_build_plan_only_approved_clips(tmp_path):
    plan = _plan(approval={"date": "2026-10-17", "words": "approve 2", "clips": [2]})
    plan["clips"][1].update({"cuts": [[6.9, 7.9]],
                             "reframe": [{"at": 5.0, "x": "left"}, {"at": 8.95, "x": "right"}]})
    proj = _project(tmp_path, plan)
    sys.argv = ["clips_plan.py", "--project", str(proj), "--build-plan",
                "--fps", "30", "--source-size", "1920x1080"]
    assert cp.main() == 0
    built = json.loads((proj / "script" / "clips.build.json").read_text(encoding="utf-8"))
    assert [c["id"] for c in built["clips"]] == ["c02"]
    c = built["clips"][0]
    assert c["timeline"] == "ep-c02" and c["export"] == "exports/ep-c02.mp4"
    # kept 5.0-6.9 and 7.9-9.9, the second split at the 8.95 reframe switch
    assert [(p["src_start"], p["src_end"]) for p in c["pieces"]] == [(5.0, 6.9), (7.9, 8.95), (8.95, 9.9)]
    recs = [p["record_frame"] for p in c["pieces"]]
    assert recs[0] == 0 and recs == sorted(recs)
    assert c["pieces"][0]["pan"] > 0 > c["pieces"][2]["pan"]
    assert c["total_frames"] == round(9.9 * 30) - round(5.0 * 30) - (round(7.9 * 30) - round(6.9 * 30))
    srt = (proj / "captions" / "c02.srt").read_text(encoding="utf-8")
    assert "w6" in srt and "w7" not in srt and srt.startswith("1\n00:00:00,000 --> ")
    assert not (proj / "captions" / "c01.srt").exists()


def test_pan_is_clamped_and_centered():
    canvas, src = (1080, 1920), (1920, 1080)
    assert cp.pan_for(0.5, canvas, src) == 0
    limit = (1920 * (1920 / 1080) - 1080) / 2
    assert cp.pan_for(0.0, canvas, src) == pytest.approx(limit, abs=0.1)
    assert cp.pan_for(1.0, canvas, src) == pytest.approx(-limit, abs=0.1)
