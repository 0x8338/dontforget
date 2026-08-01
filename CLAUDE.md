# CLAUDE.md — dontforget

## Project
Daily calendar of lives taken by violence and disaster since 2000, plus public promise tracking. UTC.

## Update workflow
- `_data/checkpoint.json` has `events.last_date` and `promises.last_date`
1. **Events:** collect from last_date+1d to today UTC, append verified events, advance `events.last_date`. Never batch-process already-covered dates; checkpoint prevents gaps if a day is skipped.
2. **Promises:** expansion runs on EVERY update — check for new commitments/status changes since `promises.last_date`, plus research 3–10 NEW untracked promises, rotating focus across leaders / CEOs / international orgs (see EXECUTION_PLAN.md). Advance `promises.last_date`. Quality gates: ≥1 verifiable source (prefer 2), explicit or calculable due date, exact public quote preferred, no duplicates vs existing (person + promise prefix).
3. **Validate:** run `python3 site/_data/validate.py`; fix errors before proceeding.
4. **Commit & push if changed:** if `events.json`, `promises.json`, or `checkpoint.json` changed, commit with a UTC timestamp in the message (e.g. `data: 2026-08-01T01:10:00Z — events +4, promises +4`) and push to origin (`0x8338/dontforget`, branch `main`). If a same-day re-run changes nothing, skip the commit.

## Data models

### Event (`_data/events.json`, keyed by MM-DD)
```yaml
date: "YYYY-MM-DD"  # UTC, ≥2000
title: "..."
category: natural-disaster | war | gun-violence | terrorism | food-crisis | industrial
location: "City, Country"
lives_lost: N
description: "One paragraph. Factual. No commentary."
sources: ["Org 1", "Org 2"]  # ≥2
```

### Promise (`_data/promises.json`)
```yaml
person: "Name"
role: "Title"
promise: "Exact quote"
date_promised/due_date: "YYYY-MM-DD"
status: kept | broken | partial | pending | kept (delayed)
description/evidence/sources
```

`sources` are short publication names only — never URLs. Full links go in the optional `source_urls` array (same order, `null` where no URL exists).

## Key rules
- **All dates UTC.** No local timezone. Date range: 2000 to present.
- **≥2 public sources per event.** Double-source before writing. Never scrape.
- **Sources are short names only** (e.g. "BBC News"), never URLs; keep links in `source_urls` when available.
- **Factual, no commentary.** What happened / what was promised / outcome.
- **Promises expansion is priority.** Always look for new targets: world leaders, CEOs, UN orgs, NATO, IMF, World Bank, more countries.
- **"Died by suicide"** — never "committed." No method details. Content warnings on high death tolls.
