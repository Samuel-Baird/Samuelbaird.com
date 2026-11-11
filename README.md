# collector-items

A scheduled Claude routine searches online marketplaces, dealers, and auctions once a day for
religious-history collectibles and opens a GitHub issue when it finds something new.

- `RUNBOOK.md` — what each daily run does
- `scouts/` — the standing instructions for each scout (edit these to change what it hunts)
- `wants.md` — specific items to watch for
- `state/seen.json` — items already reported (dedupe)
- `reports/` — one report per run

To pause: disable the routine in Claude. To change interests: edit the files above; no other change is needed.
