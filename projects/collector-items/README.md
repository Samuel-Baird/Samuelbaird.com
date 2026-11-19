# collector-items

A daily Claude Code run on the homelab Mac Studio (launchd: `com.samuel.scout` at 7:00, then
`com.samuel.scout.check` at 8:00 for `LOCAL_CHECK.md`; wrapper `~/Scout/bin/scout-run.sh`, logs in
`~/Scout/logs/`) searches online marketplaces, dealers, and auctions once a day for
religious-history collectibles and opens a GitHub issue when it finds something new.

- `RUNBOOK.md` — what each daily run does
- `scouts/` — the standing instructions for each scout (edit these to change what it hunts)
- `wants.md` — specific items to watch for
- `state/seen.json` — items already reported (dedupe)
- `reports/` — one report per run

To pause: `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.samuel.scout.plist` (and `.check.plist`)
on the Mac Studio; `launchctl bootstrap` the same paths to resume. To change interests: edit the files above; no other change is needed.
