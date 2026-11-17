from pipeline import proclamation_pages as pp


def entry(i):
    slug = f"lang{i}"
    docs = {d: {"title": f"Title {d} {i}", "subtitle": "", "source_url": f"https://example.org/{i}/{d}", "preview": f"{d}-{slug}-preview.jpg",
                "files": {k: {"file": f"{d}-{slug}-{k}.pdf", "kb": 40, "label": k, "w_in": 8.5, "h_in": 11}
                          for k in ("letter", "a4", "11x17", "18x24", "24x36", "27x40", "40x60", "a3", "a2", "a1", "a0")}}
            for d in ("family", "living-christ", "restoration", "articles-of-faith")}
    return {"slug": slug, "kind": "language", "code": f"l{i}", "native": f"Nativo {i}", "english": f"Language {i}", "docs": docs}


def test_index_stays_one_compact_list_at_150_languages():
    manifest = [entry(i) for i in range(150)]
    title, body, _ = pp.index_page(manifest)
    assert body.count('class="folder"') == 150
    assert body.count("/proclamations/lang149") == 1
    assert 'id="lang-filter"' in body and "/pfilter.js" in body
    assert "Languages <span" in body and "(150)" in body
    assert "<article" not in body            # documents live on each language's own page, not in the index


def test_alphabets_are_listed_separately():
    script = {**entry(1), "slug": "deseret", "kind": "script", "english": "Deseret Alphabet"}
    _, body, _ = pp.index_page([entry(0), script])
    assert "Alphabets" in body and body.index("Languages") < body.index("Alphabets")


def test_language_page_has_every_document_and_size():
    title, body, _ = pp.language_page(entry(7))
    assert title == "Proclamations in Language 7 | Urim"
    assert body.count("<article") == 4
    for size in ("Letter", "A4", "A0", "40×60"):
        assert body.count(f">{size}</a>") == 4
    assert "/posters/lang7/family-lang7-a4.pdf" in body and "&larr; All languages" in body
