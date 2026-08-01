# CLAUDE.md — dontforget

## Project
Daily calendar of lives taken by violence and disaster since 2000, plus public promise tracking. UTC.

## Update workflow
- `_data/checkpoint.json` has `events.last_date` and `promises.last_date`
- **Events** = collect from last_date+1d to today UTC. Single agent. Advance checkpoint on success.
- Never batch-process already-covered dates. Checkpoint prevents gaps if a day is skipped.
- **Promises expansion runs on EVERY update.** Each run does both: (1) check for new commitments/status changes since `promises.last_date`; (2) research NEW untracked promises — add 3–10 verified entries per run, rotating focus across leaders / CEOs / international orgs (see EXECUTION_PLAN.md). This keeps the dataset growing even on quiet news days.
- Promise quality gates: ≥1 verifiable source (prefer 2), explicit or calculable due date, exact public quote preferred, no duplicates vs existing (person + promise prefix).
- Run `python3 site/_data/validate.py` after every update; fix errors before advancing the checkpoint.

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

## Key rules
- **All dates UTC.** No local timezone. Date range: 2000 to present.
- **≥2 public sources per event.** Double-source before writing. Never scrape.
- **Factual, no commentary.** What happened / what was promised / outcome.
- **Promises expansion is priority.** Always look for new targets: world leaders, CEOs, UN orgs, NATO, IMF, World Bank, more countries.
- **"Died by suicide"** — never "committed." No method details. Content warnings on high death tolls.
