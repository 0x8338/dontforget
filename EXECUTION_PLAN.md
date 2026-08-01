# Agent Execution Plan — dontforget

## Checkpoint

`_data/checkpoint.json`:
```json
{"events": {"last_date": "2026-07-31"}, "promises": {"last_date": "2026-07-31"}}
```

**Update = collect from last_date+1d to today UTC.** Advance checkpoint after success. Skip = no gap.

## Daily Update (only mode)

```
READ checkpoint → last_date
TARGET: last_date+1d through today UTC
Research events for each target date (≥2 sources, lives>0, date≥2000)
Append to events.json keyed by MM-DD
Set events.last_date = today
```

**Promises — every run does ALL THREE:**

1. **Daily check:** new public commitments since `promises.last_date`; update statuses of due promises when new evidence exists.
2. **Overdue review (always):** find promises with `due_date <= today UTC` still marked `pending`, research evidence for each, and set the status to `kept`, `broken`, or `partial`. Do not leave an overdue promise `pending` without a documented reason.
3. **Expansion sweep:** research NEW untracked promises and add 3–10 verified entries per run. Rotate focus across the three tracks below so coverage grows evenly. A same-day re-run may skip this if the sweep already ran that day.

### Promise expansion tracks (rotate per run)

- **Track A — World leaders:** G20 gaps and newly elected heads of government (e.g. 2025–26 transitions: Germany/Merz, Japan/Ishiba, Canada/Carney, Ghana/Mahama, Sri Lanka/Dissanayake, Singapore/Wong).
- **Track B — CEOs & corporate:** AI labs, big tech, pharma, finance, energy, autos; commitments with explicit deadlines (safety, net-zero, hiring, investment, product rollouts).
- **Track C — International orgs & treaties:** UN agencies, NATO, IMF/World Bank, WHO, EU, G7/G20/COP decisions, treaty deadlines.

Quality gates for every entry: ≥1 verifiable source (prefer 2), explicit or calculable due date, exact public quote preferred, status `kept | broken | partial | pending | kept (delayed)`, no duplicates vs `promises.json` (check person + promise prefix). `sources` are short names only — never URLs; put full links in the optional `source_urls` array.

### Finish: validate, commit, push

After the events + promises update:

1. Run `python3 site/_data/split_data.py` to regenerate the lightweight pages data (events in 5-year windows, promises by due month + manifest).
2. Run `python3 site/_data/validate.py`; fix errors before continuing.
3. If `events.json`, `promises.json`, `checkpoint.json`, or generated split files changed, commit with a UTC timestamp:
   `git commit -m "data: $(date -u +%Y-%m-%dT%H:%M:%SZ) — events +N, promises +M"`
4. Push to origin: `git push origin main` (repo: `0x8338/dontforget`).
5. If a same-day re-run produced no changes, skip the commit.

## Historical Backfill (one-time, already done)

2000-2026 fully populated (536 events, 273 dates). No backfill needed.

## Promises Expansion (ongoing)

Priority — runs with every daily update, rotating focus. Target sources:
- World leaders (all G20 countries, not just US/UK/FR/DE/CN/IN/RU)
- CEOs (tech, pharma, finance, energy)
- International orgs (UN agencies, NATO, IMF, World Bank, WHO, EU)
- Commitments with specific deadlines that have passed (so status is known)

Agent prompt pattern:
```
Research NEW promises not already in promises.json.
Return JSON array. Mix kept/broken/partial. ≥1 source.
Focus on: [specific targets].
```

Track the last focus in `checkpoint.json` under `promises_expansion.last_focus` and pick the next track in rotation.

## Merge

Run `python3 site/_data/validate.py` (date≥2000, lives>0, ≥2 sources, duplicates, checkpoint totals). Merge script deduplicates by date+title; promises by person+promise prefix.
