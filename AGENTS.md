# AGENTS.md — dontforget

Handoff doc for agents maintaining this repository. Read in this order:

1. [CLAUDE.md](CLAUDE.md) — the canonical workflow and data rules.
2. [EXECUTION_PLAN.md](EXECUTION_PLAN.md) — checkpoint semantics, the promises routine, track rotation.
3. This file — runbook, performance rules, and repo hygiene.

## What this is

A daily UTC calendar of lives lost to violence and disaster since 2000, plus a
tracker of public promises (kept / broken / partial / pending). It is a static
site: visitors never download the full datasets, only small pre-split files.

## Take-over runbook

Always start from the checkpoint, never from "recent memory":

```bash
cat site/_data/checkpoint.json      # events.last_date, promises.last_date, totals, promises_expansion.last_focus
git status --short                  # CUSTOM_DOMAIN.md must stay dirty and untouched
git log --oneline -5                # last commit timestamp -> what has/hasn't run today
date -u +%Y-%m-%dT%H:%M:%SZ         # everything is UTC
```

The daily update is described fully in CLAUDE.md. Short version:

1. **Events** — research `events.last_date + 1` through today UTC, ≥2 sources each,
   append, then advance `events.last_date`. New facts for an already-covered date
   may be appended or used to revise a toll, but never batch-reprocess a whole day.
2. **Promises** — every run does all three: (a) new commitments/status changes since
   `promises.last_date`; (b) resolve every `pending` promise with `due_date <= today`;
   (c) add 3–10 NEW promises, rotating Track A (leaders) → B (CEOs) → C (orgs/treaties).
   A same-day re-run may skip (c). Record the focus in
   `checkpoint.json.promises_expansion.last_focus`.
3. **Build + validate + ship**:

```bash
python3 site/_data/split_data.py
python3 site/_data/validate.py          # must print OK; fix everything else first
git add site/_data                      # ONLY these; never `git add -A`
git commit -m "data: $(date -u +%Y-%m-%dT%H:%M:%SZ) — events +N, promises +M"
git push origin main                    # remote: 0x8338/dontforget
```

If a same-day re-run changed nothing, skip the commit. Keep the checkpoint totals
exactly in sync with actual counts — `validate.py` enforces this.

## Data rules that break the build

- Dates are UTC strings `YYYY-MM-DD`, ≥ 2000, never future-dated.
- Events: `lives_lost` positive int, category in
  `natural-disaster | war | gun-violence | terrorism | food-crisis | industrial`,
  ≥2 sources. Promises: ≥1 source (prefer 2), explicit/calculable `due_date`,
  status in `kept | broken | partial | pending | kept (delayed)`.
- `sources` are short publication names only — never URLs, never bare domains.
  URLs go in the optional `source_urls` array, same order, `null` for none.
- Factual, no commentary. Never scrape. No method details for deaths by suicide.
- Duplicates are checked by `date + title` (events) and `person + promise prefix`
  (promises) — check for near-duplicates before appending.

## Performance

The site already loads incrementally (per-5-year-window and per-month files, no
"load more" buttons). Preserve that: never add a build step that regenerates one
giant file visitors must download, and never fetch files a page does not need.

Pipeline scripts must stay O(N):

- `split_data.py` buckets events in a single pass and parses each year once.
- `validate.py` keeps the expensive duplicate checks inside per-date-key /
  per-person buckets, never a full N² sweep.
- After touching either script, run the stable microbenchmark before and after:
  `python3 site/_data/bench.py 5`. Reference ballpark on this machine: split
  ≈50 ms, validate ≈220 ms (process startup included). Fix regressions before
  committing.

Runtime economy also matters here — this harness runs on a token-metered DeepSeek
model, and the daily research is the dominant cost:

- Batch web searches; read only the pages needed to confirm a fact.
- Reuse already-collected coverage — the checkpoint exists precisely so days are
  not re-searched.
- Prefer `rg` and tiny targeted `python3 - <<'PY'` checks over dumping whole JSON
  files into context; both datasets are large text files.
- Prefer 2 solid sources per event and move on, rather than exhaustively re-verifying.

## Repo hygiene

- `CUSTOM_DOMAIN.md` is a user-owned work-in-progress. **Never edit it, never stage
  it.** Always stage explicit paths (`git add site/_data`), and check
  `git status --short` before and after.
- Generated files under `site/_data/events/` and `site/_data/promises/` are output
  of `split_data.py` — never hand-edit them.
- Commit messages use UTC timestamps (see format above); push after every data commit.

## Verification of a finished handoff

Before declaring a run complete, confirm:

- `python3 site/_data/validate.py` prints `OK`.
- Checkpoint `last_date`/`total` match the actual data.
- No overdue promises remain `pending` without a documented reason.
- The commit pushed to `origin main` contains only `site/_data` changes (plus any
  intentional doc edits), never `CUSTOM_DOMAIN.md`.
