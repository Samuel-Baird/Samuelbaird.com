#!/usr/bin/env python3
"""Lint a Saint Capybara project's beats.yaml for the referee's voice.

Companion to capy_check_sources.py (facts) and capy_check_brand.py
(anonymity). This one checks the *register* of the spoken beats against
docs/saint-capybara/apologetics-playbook.md's "Sharpness" section and
brand.md sec 2:

  - concession tells ("that's true", "he's right", "to be fair", "worth
    sitting with", "we're not saying", ...) are a warning on any spoken
    beat, and an ERROR when they appear in
      * the first sentence of the first response beat (the frame), or
      * anywhere in the closing beat (the punchline);
  - hedge tells ("maybe", "perhaps", "arguably", "I could be wrong", "more
    complicated than") are info on any spoken beat and a warning in the
    closing beat -- a fact-graded claim should sound like one;
  - polemic tells -- rage-bait vocabulary from brand.md's "Never" list
    ("destroyed", "owned", "cope", "rekt", "debunked") and the adjectives
    the jab rule forbids ("absurd", "laughable", "ridiculous", ...) -- are
    an error anywhere;
  - a bare "concede"/"admit" is only a warning: a *source* conceding a
    point is a legitimate rebuttal move, so the reviewer checks whose
    concession it is;
  - --strict upgrades every warning to an error.

This tool cannot tell whether a jab landed or whether there was more than
one; that stays with capy-critic-editor / capy-critic-opponent
(/capy-critique). It catches the mechanical tells that had been slipping
past the manual read-through.

Usage:
    python tools/capy_check_tone.py --project D:\\Videos\\<slug> [--strict]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capy import beats as beats_mod

Issue = beats_mod.Issue

SPOKEN_KINDS = {"narration", "card", "evidence", "chart"}

# (pattern, label). All matched case-insensitively against the beat text.
# CLAUSE anchors a tell to the start of a clause (start of text, or after
# sentence punctuation / a dash / a colon), so "how that's true" mid-sentence
# isn't a hit but "That's true, but..." and "-- that's true." are.
CLAUSE = r"(?:^|[.!?:;,]\s*|[-–—]+\s*)"
CONCESSION_TELLS: list[tuple[str, str]] = [
    (CLAUSE + r"that'?s true\b", "that's true"),
    (CLAUSE + r"that (part|much|bit)'?s? (is )?(true|real|right|fair)\b", "that part is true"),
    (CLAUSE + r"that (figure|number|quote|date)'?s? (is )?(real|right|accurate|correct)\b", "that figure is real"),
    (r"\b(he|she|they)'?s? (is |are )?right about\b", "he's right about"),
    (r"\b(he|she|they)'?s? (is |are )?(not wrong|partly right|half right)\b", "not wrong / partly right"),
    (r"\bthat'?s a fair\b", "that's a fair"),
    (r"\bfair (point|summary|question|concern|criticism)\b", "fair point"),
    (r"\bit'?s fair to\b", "it's fair to"),
    (r"\bto be fair\b", "to be fair"),
    (r"\bno argument there\b", "no argument there"),
    (r"\bworth sitting with\b", "worth sitting with"),
    (r"\bstart with what'?s true\b", "start with what's true"),
    (r"\bwe'?re not saying\b", "we're not saying"),
    (r"\bnot saying (that|this)\b", "not saying that"),
    (r"\bthe church (concedes|admits|acknowledges)\b", "the Church concedes"),
    (r"\b(doesn'?t|does not) make (it|this) comfortable\b", "doesn't make it comfortable"),
    (r"\b(half|some|part) of (that|this) is (exactly )?right\b", "half of that is right"),
    (CLAUSE + r"(that'?s |he'?s |she'?s )?exactly right\b", "exactly right"),
    (r"\bhowever (it|this) lands\b", "however it lands"),
    (CLAUSE + r"(both|two claims,? both) (are )?true\b", "both true"),
    (r"\bboth sides have a point\b", "both sides have a point"),
]

SOFT_CONCESSION_TELLS: list[tuple[str, str]] = [
    (r"\bconced(e|es|ed|ing)\b", "concede (check whose concession this is -- a source conceding is fine)"),
    (r"\badmit(s|ted|ting)?\b", "admit (check whose admission this is)"),
]

HEDGE_TELLS: list[tuple[str, str]] = [
    (r"\bmaybe\b", "maybe"),
    (r"\bperhaps\b", "perhaps"),
    (r"\barguably\b", "arguably"),
    (r"\bi could be wrong\b", "I could be wrong"),
    (r"\bin some ways\b", "in some ways"),
    (r"\bmore complicated than\b", "more complicated than"),
    (r"\bit'?s complicated\b", "it's complicated"),
    (r"\bsettles? (absolutely )?everything\b", "settles everything"),
]

POLEMIC_TELLS: list[tuple[str, str]] = [
    (r"\bdestroy(ed|s)?\b", "destroyed (rage-bait)"),
    (r"\bowned\b", "owned (rage-bait)"),
    (r"\bcope\b", "cope (rage-bait)"),
    (r"\brekt\b", "rekt (rage-bait)"),
    (r"\bdebunk(ed|s|ing)?\b", "debunked (rage-bait)"),
    (r"\babsurd\b", "absurd (jab adjective)"),
    (r"\blaughable\b", "laughable (jab adjective)"),
    (r"\bridiculous\b", "ridiculous (jab adjective)"),
    (r"\bembarrassing\b", "embarrassing (jab adjective)"),
    (r"\bdesperate\b", "desperate (jab adjective)"),
    (r"\bpathetic\b", "pathetic (jab adjective)"),
    (r"\bstupid\b", "stupid (ad hominem)"),
    (r"\bidiot(s|ic)?\b", "idiot (ad hominem)"),
    (r"\bliar(s)?\b", "liar (ad hominem -- brand.md: never call people dishonest without evidence)"),
    (r"\bclown(s)?\b", "clown (ad hominem)"),
]

WARN_POLEMIC_TELLS: list[tuple[str, str]] = [
    (r"\bdishonest(ly)?\b", "dishonest (allowed only with evidence on screen -- brand.md sec 2)"),
    (r"\bboy,? does\b", "'boy, does...' (personal register -- playbook jab rule 2)"),
]


def _first_sentence(text: str) -> str:
    text = text.strip()
    m = re.search(r"[.!?](\s|$)", text)
    return text[: m.end()] if m else text


def _hits(text: str, tells: list[tuple[str, str]]) -> list[str]:
    out = []
    for pat, label in tells:
        if re.search(pat, text, flags=re.IGNORECASE):
            out.append(label)
    return out


def check(doc: dict, strict: bool = False) -> list[Issue]:
    issues: list[Issue] = []
    beats = doc.get("beats", []) or []
    spoken = [b for b in beats if b.get("kind") in SPOKEN_KINDS and (b.get("text") or "").strip()]
    if not spoken:
        return [Issue("warning", None, "no spoken beats found (narration/card/evidence/chart)")]

    first = spoken[0]
    closing = beats[-1] if beats else None
    closing_id = closing.get("id") if closing else None

    warn = "error" if strict else "warning"

    for b in spoken:
        bid = b.get("id")
        text = b.get("text") or ""
        is_first = b is first
        is_closing = closing is not None and bid == closing_id

        # Concession tells
        for label in _hits(text, CONCESSION_TELLS):
            if is_closing:
                issues.append(Issue("error", bid, f"closing beat contains concession tell '{label}' -- the close is the punchline, not the disclaimer (playbook: Sharpness)"))
            elif is_first and label in _hits(_first_sentence(text), CONCESSION_TELLS):
                issues.append(Issue("error", bid, f"first response sentence opens on concession tell '{label}' -- the frame is Saint Capybara's position, never agreement (playbook: Sharpness)"))
            else:
                issues.append(Issue(warn, bid, f"concession tell '{label}' -- fold the granted fact into the rebuttal sentence, or cut it (playbook: concession budget)"))

        for label in _hits(text, SOFT_CONCESSION_TELLS):
            level = "error" if is_closing else warn
            issues.append(Issue(level, bid, f"{label}"))

        # Hedge tells
        for label in _hits(text, HEDGE_TELLS):
            if is_closing:
                issues.append(Issue(warn, bid, f"closing beat hedges with '{label}' -- a fact-graded claim should sound like one (brand.md sec 2)"))
            else:
                issues.append(Issue("info", bid, f"hedge '{label}' -- fine only if the claim is graded disputed/speculation"))

        # Polemic tells
        for label in _hits(text, POLEMIC_TELLS):
            issues.append(Issue("error", bid, f"polemic tell '{label}' -- brand.md sec 2 'Never' list / playbook jab rule 3"))
        for label in _hits(text, WARN_POLEMIC_TELLS):
            issues.append(Issue(warn, bid, f"{label}"))

    # Closing beat that is a clip/excerpt is someone else's problem (beats.validate)
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--strict", action="store_true", help="upgrade warnings to errors")
    args = ap.parse_args()

    beats_path = args.project / "script" / "beats.yaml"
    if not beats_path.exists():
        print(f"error: {beats_path} not found")
        return 2

    doc = beats_mod.load_beats(beats_path)
    issues = check(doc, strict=args.strict)

    order = {"error": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda i: (order.get(i.level, 3), str(i.beat_id)))
    for iss in issues:
        where = f"[{iss.beat_id}]" if iss.beat_id else "[--]"
        print(f"{iss.level.upper():7} {where:8} {iss.message}")

    n_err = sum(1 for i in issues if i.level == "error")
    n_warn = sum(1 for i in issues if i.level == "warning")
    n_info = sum(1 for i in issues if i.level == "info")
    if not issues:
        print("capy_check_tone: clean -- no concession, hedge, or polemic tells in spoken beats.")
    else:
        print(f"\ncapy_check_tone: {n_err} error(s), {n_warn} warning(s), {n_info} info.")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
