"""The agent-driven pipeline: prepare -> get_chunk -> submit_chunk -> finish. A sloppy agent gets errors, never a crash."""
import json
import re

import pytest

from test_engine import FakeMT, fixtures, tr  # noqa: F401  (fixtures: autouse glossary/books patches)
from urim_translate import config, scriptures, workflow

JOHN316 = ("For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him "
           "should not perish, but have everlasting life.")
DOC = f"""---
title: The Test Talk
language: eng
---

Brothers, the priesthood is the power of God. Jesus taught, “{JOHN316}”[^1] He asked us to be "faithful and true" in all things[^2] every single day of our lives.

## Gifts

The endowment is 1 gift among 3 others that we receive in the temple of the Lord today.

[^1]: John 3:16.
[^2]: Alma 32:21; John 3:16.
[^3]: A talk by an apostle, 2020.
"""
GOOD = [
    "A Prueba",
    "Irmãos, o sacerdócio é o poder de Deus. Jesus ensinou: “[[S1]]”[^1] Ele nos pediu que fôssemos fiéis em tudo[^2] todos os dias de nossas vidas.",
    "## Dons",
    "A investidura é 1 dom entre 3 outros que recebemos no templo do Senhor hoje.",
]


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "HOME", tmp_path / "home")
    scriptures._cache.clear()


@pytest.fixture
def doc(tmp_path):
    p = tmp_path / "talk.md"
    p.write_text(DOC, encoding="utf-8")
    return p


def prep(doc, **kw):
    return workflow.prepare(tr([]), doc, "pt", **kw)


def test_prepare_fills_church_text_and_footnotes(doc):
    r = prep(doc)
    assert r["ok"] and r["job_id"].startswith("j") and r["todo"] == [1, 2]
    assert r["already_done"]["scripture_quotes_filled_from_church_text"] == 1
    assert r["already_done"]["footnotes_that_are_only_scripture_citations"] == 2
    assert "instructions" in r and len(json.dumps(r)) < 1500
    c = workflow.get_chunk(r["job_id"], 1)
    assert "[[S1]]" in c["source"] and "everlasting" not in c["source"]
    assert c["scripture"][0]["ref"] == "João 3:16" and c["lines"] == 4        # title + 2 paragraphs + heading
    assert c["source"].startswith("The Test Talk") and "## Gifts" in c["source"]
    assert [t["use"] for t in c["terms"]] == ["sacerdócio", "investidura"]
    assert "url" not in c["terms"][0]
    fn = workflow.get_chunk(r["job_id"], 2)                                   # only the non-citation footnote remains
    assert fn["source"] == "[^3]: A talk by an apostle, 2020."


def test_unmatched_quote_is_not_given_a_false_reference(doc):
    c = workflow.get_chunk(prep(doc)["job_id"], 1)
    assert all("faithful" not in x["church_text"] for x in c.get("quotes", []))


def test_full_cycle_writes_the_file(doc, tmp_path):
    r = prep(doc, output_path=str(tmp_path / "out" / "t.pt.md"))
    jid = r["job_id"]
    ok = workflow.submit_chunk(tr([]), jid, 1, "\n\n".join(GOOD))
    assert ok["ok"] and ok["remaining"] == [2]
    ok = workflow.submit_chunk(tr([]), jid, 2, "[^3]: Uma palestra de um apóstolo, 2020.")
    assert ok["ok"] and ok["remaining"] == [] and ok["next"] is None
    f = workflow.finish(tr([]), jid)
    assert f["ok"] and f["lines_by_origin"]["citation"] == 2
    text = (tmp_path / "out" / "t.pt.md").read_text(encoding="utf-8")
    church = scriptures.passage("pt", "john", 3, 16, 16).rstrip(".,;:")
    assert text.startswith('---\ntitle: "A Prueba"') and "language: por" in text
    assert f"“{church}”" in text                                              # the Church's own pt text of John 3:16
    assert "[[" not in text and "everlasting" not in text
    assert "## Dons" in text and "[^1]: João 3:16." in text and "[^2]: Alma 32:21; João 3:16." in text
    assert f["scripture_quotes_from_church_text"] == 1


def test_sloppy_submissions_get_specific_errors(doc):
    jid = prep(doc)["job_id"]
    t = tr([])
    r = workflow.submit_chunk(t, jid, 1, "just one line")
    assert not r["ok"] and "expected exactly 4" in r["problems"][0]["problem"] and len(r["source_line_starts"]) == 4
    bad = list(GOOD)
    bad[1] = bad[1].replace("[[S1]]", "").replace("[^1]", "")
    r = workflow.submit_chunk(t, jid, 1, "\n".join(bad))
    assert not r["ok"]
    msgs = " ".join(p["problem"] for p in r["problems"])
    assert "[[S1]]" in msgs and "[^1]" in msgs
    untranslated = ["The Test Talk", DOC.split("\n\n")[1], "## Gifts", DOC.split("\n\n")[3]]
    r = workflow.submit_chunk(t, jid, 1, "\n".join(untranslated))
    assert not r["ok"]
    assert workflow.submit_chunk(t, jid, 1, "")["ok"] is False
    assert workflow.submit_chunk(t, jid, 1, 42)["ok"] is False           # wrong type: error dict, no exception
    assert workflow.submit_chunk(t, jid, 1, GOOD)["ok"]                  # a list of lines is accepted too


def test_soft_problems_block_twice_then_are_accepted_and_flagged(doc):
    jid = prep(doc)["job_id"]
    t = tr([])
    wrong = list(GOOD)
    wrong[3] = "A investidura é um dom entre três outros que recebemos no templo do Senhor hoje."   # numbers lost
    wrong[1] = wrong[1].replace("sacerdócio", "poder")                                           # glossary
    for attempt in (1, 2):
        r = workflow.submit_chunk(t, jid, 1, "\n".join(wrong))
        assert not r["ok"] and r["attempt"] == attempt
        msgs = " ".join(p["problem"] for p in r["problems"])
        assert "numbers differ" in msgs and 'must be rendered as "sacerdócio"' in msgs
    r = workflow.submit_chunk(t, jid, 1, "\n".join(wrong))
    assert r["ok"] and r["accepted_with_issues"]


def test_prefix_is_restored_and_blank_lines_ignored(doc):
    jid = prep(doc)["job_id"]
    sloppy = [GOOD[0], "", GOOD[1], "", "# Dons", GOOD[3]]               # wrong heading level, blank lines
    assert workflow.submit_chunk(tr([]), jid, 1, "\n".join(sloppy))["ok"]
    workflow.submit_chunk(tr([]), jid, 2, "[^3]: Uma palestra, 2020.")
    out = workflow.finish(tr([]), jid)["output_path"]
    assert "\n## Dons\n" in open(out, encoding="utf-8").read()


def test_bad_inputs_never_raise(doc, tmp_path):
    t = tr([])
    assert not workflow.prepare(t, tmp_path / "nope.md", "pt")["ok"]
    assert not workflow.prepare(t, doc, "fr")["ok"]
    (tmp_path / "empty.md").write_text("", encoding="utf-8")
    assert not workflow.prepare(t, tmp_path / "empty.md", "pt")["ok"]
    jid = prep(doc)["job_id"]
    for call in (lambda: workflow.get_chunk("zzz", 1), lambda: workflow.get_chunk(jid, 99), lambda: workflow.get_chunk(jid, "x"),
                 lambda: workflow.get_chunk("../..", 1), lambda: workflow.submit_chunk(t, jid, 0, "x"),
                 lambda: workflow.finish(t, "nojob"), lambda: workflow.job_status("")):
        r = call()
        assert r["ok"] is False and r["error"]
    assert workflow.get_chunk(f" {jid} ", "1")["ok"]                      # whitespace and "1" as text are tolerated


def test_finish_with_missing_chunks(doc):
    jid = prep(doc)["job_id"]
    r = workflow.finish(tr([]), jid)
    assert not r["ok"] and "[1, 2]" in r["error"] and "fill_missing_locally" in r["hint"]
    r = workflow.finish(tr([FakeMT()]), jid, fill_missing_locally=True)
    assert r["ok"] and r["lines_by_origin"]["local"] == 5


def test_resume_keeps_progress_and_chunks_respect_paragraphs(tmp_path):
    paras = [f"Paragraph {i}: " + "word " * 40 for i in range(10)]
    p = tmp_path / "long.md"
    p.write_text("\n\n".join(x.strip() for x in paras), encoding="utf-8")
    r = workflow.prepare(tr([]), p, "pt", max_words=100)
    assert len(r["chunks"]) >= 4 and sum(c["lines"] for c in r["chunks"]) == 10
    jid = r["job_id"]
    lines = workflow.get_chunk(jid, 1)["source"].split("\n\n")
    assert all(l.startswith("Paragraph") and l.endswith("word") for l in lines)
    out = [re.sub("^Paragraph", "Parágrafo", l).replace("word", "palavra") for l in lines]
    assert workflow.submit_chunk(tr([]), jid, 1, "\n\n".join(out))["ok"]
    again = workflow.prepare(tr([]), p, "pt", max_words=100)
    assert again["resumed"] and 1 not in again["todo"] and again["job_id"] == jid


def test_church_tm_hit_is_used(tmp_path):
    t = tr([])
    t.store.tm_put("pt", "Brothers, the priesthood is the power of God.", "Irmãos, o sacerdócio é o poder de Deus.", "church")
    t.store.tm_put("pt", "The endowment is 1 gift.", "agent text is never reused", "ollama")
    p = tmp_path / "a.md"
    p.write_text("Brothers, the priesthood is the power of God.\n\nThe endowment is 1 gift.\n", encoding="utf-8")
    r = workflow.prepare(t, p, "pt")
    assert r["already_done"]["lines_from_church_translation_memory"] == 1 and r["chunks"][0]["lines"] == 1


def test_links_become_short_ids_and_come_back(tmp_path):
    url = "https://www.churchofjesuschrist.org/study/scriptures/bofm/alma/5?lang=eng&id=p12#p12"
    p = tmp_path / "l.md"
    p.write_text(f"Alma asked about a change of heart ([Alma 5:12]({url})), see also {url} today.\n", encoding="utf-8")
    t = tr([])
    jid = workflow.prepare(t, p, "pt")["job_id"]
    c = workflow.get_chunk(jid, 1)
    assert "https://" not in c["source"] and "[[L1]]" in c["source"] and "[[L2]]" in c["source"] and "placeholders_note" in c
    dup = workflow.submit_chunk(t, jid, 1, "Alma ([Alma 5:12]([[L1]])) [[L1]] [[L2]] hoje, veja também muita coisa aqui hoje.")
    assert not dup["ok"] and "[[L1]]" in json.dumps(dup)
    ok = workflow.submit_chunk(t, jid, 1, "Alma perguntou sobre uma mudança de coração ([Alma 5:12]([[L1]])), veja também [[L2]] hoje.")
    assert ok["ok"], ok
    out = open(workflow.finish(t, jid, str(tmp_path / "o.md"))["output_path"], encoding="utf-8").read()
    assert f"([Alma 5:12]({url}))" in out and f"também {url} hoje" in out


def test_server_exposes_the_pipeline_and_the_recipe():
    import asyncio
    from urim_translate import server
    tools = {t.name: t for t in asyncio.run(server.mcp.list_tools())}
    for name in ("prepare_translation", "get_chunk", "submit_chunk", "finish_translation", "job_status",
                 "translate_file", "translate_text", "match_glossary", "check_translation", "backends_status"):
        assert name in tools, name
    ins = server.mcp.instructions
    assert all(w in ins for w in ("prepare_translation", "get_chunk", "submit_chunk", "finish_translation", "parallel"))
    assert "LOCAL" in tools["translate_file"].description        # a model must not mistake the slow route for the main one
    assert "edits" in ins


class FakeDraft(FakeMT):
    """A machine translator that gets one Church term wrong ('poder' for priesthood) and keeps masked tokens."""
    CANNED = {
        "The Test Tal": "A Prueba",
        "Brothers, th": "Irmãos, o poder é o poder de Deus. Jesus ensinou: “⟦1⟧”⟦2⟧ Ele nos pediu que fôssemos fiéis em tudo⟦3⟧ todos os dias de nossas vidas.",
        "Gifts": "Dons",
        "The endowmen": "A investidura é 1 dom entre 3 outros que recebemos no templo do Senhor hoje.",
        "A talk by an": "Uma palestra de um apóstolo, 2020.",
    }

    def translate(self, texts, lang):
        return [self.CANNED[t[:12]] for t in texts]


def test_draft_mode_only_corrections_are_sent(doc):
    t = tr([FakeDraft()])
    r = workflow.prepare(t, doc, "pt", draft=True)
    assert r["ok"] and "edits" in r["instructions"]
    jid = r["job_id"]
    c = workflow.get_chunk(jid, 1)
    assert set(c["draft"]) == {"1", "2", "3", "4"} and "poder" in c["draft"]["2"]
    assert "sacerdócio" in " ".join(c["draft_issues"]["2"]) and "1" not in c["draft_issues"]
    bad = workflow.submit_chunk(t, jid, 1, edits={})
    assert not bad["ok"] and bad["problems"][0]["line"] == 2 and "edits" in bad["hint"]
    assert workflow.submit_chunk(t, jid, 1, edits={"9": "x"})["ok"] is False
    assert workflow.submit_chunk(t, jid, 1, edits="nonsense")["ok"] is False
    good = workflow.submit_chunk(t, jid, 1, edits={"2": GOOD[1]})
    assert good["ok"], good
    assert workflow.submit_chunk(t, jid, 2, edits={})["ok"]              # the footnote draft was fine as it was
    f = workflow.finish(t, jid)
    assert f["ok"] and f["lines_by_origin"]["draft"] == 4 and f["lines_by_origin"]["agent"] == 1
    out = open(f["output_path"], encoding="utf-8").read()
    assert "\n## Dons\n" in out and "Irmãos, o sacerdócio" in out and "[[" not in out


def test_draft_mode_without_a_translator_falls_back_to_plain_pipeline(doc):
    t = tr([])
    jid = workflow.prepare(t, doc, "pt", draft=True)["job_id"]
    c = workflow.get_chunk(jid, 1)
    assert "draft" not in c
    ok = workflow.submit_chunk(t, jid, 1, "\n".join(GOOD))
    assert ok["ok"]
    assert not workflow.submit_chunk(t, jid, 2, edits={})["ok"]          # no draft: asks for the translation instead


def test_ordinary_space_in_a_citation_is_accepted():
    """Church citations use a non-breaking space ("2 Nefi"); an agent typing a plain space must not be rejected."""
    ln = {"keep": ["2 Nefi 33:6", "[[L1]]"], "shown": "[2 Nefi 33:6]([[L1]]).", "quotes": []}
    typed = "[2 Nefi 33:6]([[L1]])."
    assert any("exactly as written" in h for h in workflow._check(ln, typed, tr([]), "es", tr([]).glossary("es"))[0])
    fixed = workflow._restore_spaces(ln, typed)
    assert fixed == "[2 Nefi 33:6]([[L1]])."
    assert not any("exactly as written" in h for h in workflow._check(ln, fixed, tr([]), "es", tr([]).glossary("es"))[0])


def test_submit_returns_the_next_chunk_unless_asked_not_to(doc):
    t = tr([])
    jid = prep(doc)["job_id"]
    ok = workflow.submit_chunk(t, jid, 1, "\n".join(GOOD))
    assert ok["ok"] and ok["next"] == 2 and ok["next_chunk"]["chunk"] == 2 and "[^3]" in ok["next_chunk"]["source"]
    last = workflow.submit_chunk(t, jid, 2, "[^3]: Uma palestra de um apóstolo, 2020.")
    assert last["ok"] and "next_chunk" not in last
    jid2 = workflow.prepare(t, doc, "pt", output_path="x.md")["job_id"]
    assert "next_chunk" not in workflow.submit_chunk(t, jid2, 1, "\n".join(GOOD), include_next=False)


def test_default_chunk_size_is_about_nine_hundred_words(tmp_path):
    p = tmp_path / "long.md"
    p.write_text("\n\n".join("Paragraph %d: %s" % (i, "word " * 99) for i in range(18)), encoding="utf-8")
    assert len(workflow.prepare(tr([]), p, "pt")["chunks"]) <= 3 < len(workflow.prepare(tr([]), p, "pt", max_words=450)["chunks"])


def test_reference_footnotes_may_stay_close_to_the_english(tmp_path):
    p = tmp_path / "f.md"
    p.write_text("A paragraph that has a reference.[^1]\n\n[^1]: Dallin H. Oaks, “The Family-Centered Gospel of Jesus Christ,” Liahona, May 2026.\n", encoding="utf-8")
    t = tr([])
    jid = workflow.prepare(t, p, "pt")["job_id"]
    assert workflow.submit_chunk(t, jid, 1, "Um parágrafo que tem uma referência.[^1]")["ok"]
    r = workflow.submit_chunk(t, jid, 2, "Dallin H. Oaks, “The Family-Centered Gospel of Jesus Christ,” Liahona, May 2026.")
    assert r["ok"], r


def test_bad_tool_arguments_return_a_readable_error():
    from urim_translate import server
    r = server.lookup_term("covenant path", "en")
    assert r["ok"] is False and "es" in r["error"] and "pt" in r["error"]


def test_link_style_citation_after_a_quote_fills_the_church_text(tmp_path):
    url = "https://www.churchofjesuschrist.org/study/scriptures/nt/john/3?lang=eng&id=p16#p16"
    p = tmp_path / "c.md"
    p.write_text(f"Jesus taught, “{JOHN316}” ([John 3:16]({url}); emphasis added). Believe it today and always.\n", encoding="utf-8")
    r = workflow.prepare(tr([]), p, "pt")
    assert r["already_done"]["scripture_quotes_filled_from_church_text"] == 1
    c = workflow.get_chunk(r["job_id"], 1)
    assert "[[S1]]" in c["source"] and "everlasting" not in c["source"]
