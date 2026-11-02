# Urim — Mormon Translation Atlas

A searchable multilingual dictionary of Latter-day Saint theological vocabulary:
how the Church's own published translations render distinctive Restoration terms
in English, Portuguese (pt-BR) and Spanish. Live at <https://urim.samuelbaird.com>.

Independent project; not affiliated with The Church of Jesus Christ of Latter-day Saints.

## Sourcing rule

Only Church-translated material is used as evidence. Every rendering shown in
the atlas is one of:

| Status | Meaning |
|---|---|
| `approved_term` | On the Church's "Approved Terms for Interpretation" list |
| `attested` | Found in aligned official Church text (General Conference translations, scriptures) with counts and source links |
| `inferred` | Mined from aligned Church text, not yet reviewed |

AI-generated translations (including those held in pulpit-vault) are never used
as evidence. A term with no Church source stays blank.

## Layout

- `concepts/` curated concept files (source of truth)
- `pipeline/` Python build: seed, attest, mine variants, build
- `data/` generated attestations, glossaries, provenance
- `site/` static site (Vercel root)
- `mcp/` local, free translation MCP server (glossary-enforcing, cached)
- `api/mcp.js` hosted read-only atlas MCP at `/api/mcp` (see the site's Connect page)

## Rebuild

Needs a local checkout of [pulpit-vault](https://github.com/Noah-Airmet/pulpit-vault)
with its parallel corpus built (`URIM_PULPIT`, default `../pulpit-vault`).

```bash
python -m pipeline.attest
python -m pipeline.build
```
