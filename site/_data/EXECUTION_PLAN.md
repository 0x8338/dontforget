# Agent Execution Plan — Historical Data Population

## Overview

Populate `_memory/` and `_promises/` with historical data from **2000-01-01 to present**. Agents process in monthly batches with a checkpoint system so interrupted work can resume without restarting.

## Checkpoint File

`_data/checkpoint.json` is the single source of truth. Every agent reads it on start, writes to it on completion. If an agent dies, the next one picks up where it left off.

## Data Model

### Memory event (`_memory/YYYY/MM/DD/slug.md`)
```yaml
---
date: "2004-12-26"
title: "Indian Ocean Tsunami"
category: natural-disaster | war | gun-violence | terrorism | food-crisis | industrial
location: "Indian Ocean, 14 countries"
lives_lost: 227898
sources:
  - "BBC News"
  - "Reuters"
---
One-paragraph factual description. No commentary.
```

### Promise (`_promises/YYYY/person-slug.md`)
```yaml
---
person: "Barack Obama"
role: "President of the United States"
promise: "We will close Guantánamo Bay within one year"
date_promised: "2009-01-22"
due_date: "2010-01-22"
status: broken
sources:
  - "White House press briefing"
evidence:
  - "Guantánamo remains open as of 2026 - NYT"
---
Context and outcome.
```

## Phase 1: Memory Events (2000–2026)

### Strategy: Process by month
- Each agent claims one month from `checkpoint.json`
- Agent researches major events (catastrophes, mass shootings, conflicts) for that month
- Writes .md files to `_memory/YYYY/MM/DD/slug.md`
- Marks month as `completed` in checkpoint, increments `events_written`

### Agent Prompt Template
```
You are populating the dontforget historical archive.

CLAIM: Read _data/checkpoint.json. Find the first month in range [2000-01 to 2026-07]
not in the "completed" list and not "in_progress". Set it to "in_progress" with your
agent_id. Write the updated checkpoint.

RESEARCH: For every day in {MONTH}, search for significant events:
- Natural disasters (earthquakes, tsunamis, hurricanes, floods) with 100+ deaths
- Mass shootings (5+ fatalities)
- Terrorist attacks and armed conflicts with civilian casualties
- Industrial accidents with deaths
- Assassinations of public figures

For each event, find at least 2 reputable sources.

WRITE: Create _memory/YYYY/MM/DD/slug.md for each event following the data model above.
Use lowercase-kebab-case slugs.

COMPLETE: Update checkpoint.json — add {MONTH} to "completed", increment "events_written",
set "in_progress" to null. Write the updated checkpoint.
```

### Batch Size
- ~26 years × 12 months = 312 months
- Run 8-10 agents in parallel, each processing 1 month
- ~32 rounds of parallel agents
- Each agent produces ~3-15 events per month (not every day has major events)

### Quality Gates
- Agent writes events → maintainer spot-checks 10% of output
- Common failure mode: events on wrong date (timezone issues) — always use UTC
- Common failure mode: unverified death tolls — reject events without 2 sources

## Phase 2: Promises (2000–2026)

### Strategy: Process by year
- Promises are sparser than events — one agent per year
- Agent researches major public promises by world leaders, CEOs, institutions
- Writes .md files to `_promises/YYYY/person-slug.md`

### Agent Prompt Template
```
You are populating the dontforget promises archive.

CLAIM: Read _data/checkpoint.json. Find the first year in the promises range
not completed. Set it to "in_progress".

RESEARCH: For {YEAR}, find significant public promises:
- Political campaign promises with specific deadlines
- International agreements/treaties with target dates
- CEO/public figure commitments with explicit timelines
- Infrastructure/military/crisis-response pledges

Each promise must have: a verifiable public source, a specific person, an explicit
or calculable due date.

WRITE: Create _promises/YYYY/person-slug.md for each promise.

COMPLETE: Mark year as completed in checkpoint.
```

## Phase 3: Daily Update Task

### The daily agent runs once per day, processing yesterday's date

```
You are the daily updater for dontforget.

READ: _data/checkpoint.json → daily_task.last_date_processed

TARGET DATE: {last_date_processed + 1 day} or {yesterday UTC} if never run

RESEARCH: What catastrophic/gun-violence/conflict events happened on TARGET DATE?
Any promises due on TARGET DATE? Any promise statuses need updating?

WRITE: New event .md files. Update promise statuses if evidence available.

COMPLETE: Set last_date_processed = TARGET DATE in checkpoint.
```

## Resume / Recovery

### If an agent dies mid-month:
1. New agent reads `checkpoint.json`
2. Sees `in_progress: "2004-03"` with `agent_id: "dead-agent-xyz"`
3. Checks if any .md files exist under `_memory/2004/03/`
4. If partial work exists: inspects existing files, continues from where it stopped
5. If no files: restarts the month from scratch
6. Updates `agent_id` to itself and continues

### Checkpoint corruption recovery:
- `checkpoint.json` is committed to git after every completed month
- `git log -- _data/checkpoint.json` shows full history
- If corrupted, revert to last known-good commit

## Agent Concurrency Rules

1. **Only one agent per month** — enforced by checkpoint `in_progress` field
2. **Write checkpoint BEFORE starting work** (claim the month)
3. **Write checkpoint AFTER completing work** (release the month)
4. **Memory and Promises agents can run in parallel** — separate checkpoint sections
5. **File writes per agent are isolated** — each agent only writes to its own month's directory
6. **git commit each completed batch** — so partial progress is never lost

## Estimated Volume

| Category | Estimate |
|---|---|
| Memory events | ~2,000–5,000 (3-15 significant events per month × 312 months) |
| Promises | ~200–500 (10-20 major promises per year × 26 years) |
| Daily new events | ~1–3 per day |
| Daily promise updates | ~0–2 status changes per day |
