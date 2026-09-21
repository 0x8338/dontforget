# Agent Execution Plan — dontforget

## Checkpoint

`site/_data/checkpoint.json`:
```json
{"events": {"last_date": "2026-07-31"}, "promises": {"last_date": "2026-07-31"}}
```

**Update = collect from last_date+1d to today UTC.** After successful research,
advance the checkpoint only through fully elapsed UTC days. Today's provisional
additions do not close today's coverage; revisit it next run and deduplicate.

## Preservation First

Follow [AGENTS.md](AGENTS.md#preserve-the-collected-archive). Existing records stay
visible when evidence is incomplete. Apply source-backed corrections in place;
flag unresolved fields instead of deleting, quarantining, hiding, or downgrading
an existing outcome solely because a new search was inconclusive. Whole-record
removal or merging requires explicit owner approval and record-specific evidence.

Capture IDs, total counts, due counts, and status counts before editing. Preserve
existing `archive_id` values; assign new IDs once and append additions to
`site/_data/retention.json`. Never shrink the inventory to pass validation.
Do not extend the fixed `legacy-review.json` exemptions to new records.

## Daily Update (only mode)

```
READ checkpoint → last_date
TARGET: last_date+1d through today UTC
Research events for each target date (≥2 sources, lives>0, date≥2000)
Append to events.json keyed by MM-DD
Set events.last_date = latest fully elapsed UTC day researched (at most yesterday)
```

**Promises — every run does ALL THREE:**

1. **Daily check:** new public commitments since `promises.last_date`; update statuses of due promises when new evidence exists.
2. **Overdue review (always):** find promises with `due_date <= today UTC` still marked `pending`, research evidence for each, and resolve the status only when supported. Document why a promise remains pending when evidence is insufficient; an elapsed deadline alone is not proof of failure.
3. **Expansion sweep:** research NEW untracked promises and add 3–10 verified entries per run. Rotate focus across the three tracks below so coverage grows evenly. A same-day re-run may skip this if the sweep already ran that day.

### Promise expansion tracks (rotate per run)

- **Track A — World leaders:** G20 gaps and newly elected heads of government (e.g. 2025–26 transitions: Germany/Merz, Japan/Ishiba, Canada/Carney, Ghana/Mahama, Sri Lanka/Dissanayake, Singapore/Wong).
- **Track B — CEOs & corporate:** AI labs, big tech, pharma, finance, energy, autos; commitments with explicit deadlines (safety, net-zero, hiring, investment, product rollouts).
- **Track C — International orgs & treaties:** UN agencies, NATO, IMF/World Bank, WHO, EU, G7/G20/COP decisions, treaty deadlines.

Quality gates for new entries: ≥1 verifiable source (prefer 2), explicit or calculable due date, faithful wording, status `kept | broken | partial | pending | kept (delayed)`, no duplicates vs `promises.json` (check person + promise prefix). `sources` are short names only — never URLs; put usable links in the aligned `source_urls` array. Do not invent exact quotes or deadlines. Legacy gaps follow the visible-review rules in AGENTS.md; these gates do not authorize removing collected records.

### Finish: validate, then publish when authorized

After the events + promises update:

1. Register new IDs in `retention.json`; compare before/after IDs and total/due/status counts using the same UTC date. Investigate unexpected reductions before publication.
2. Run the Python and page tests listed in AGENTS.md, then `python3 site/_data/split_data.py` to regenerate the lightweight pages data (events in 5-year windows, promises by due month + manifest).
3. Run `python3 site/_data/validate.py`; fix errors and document research warnings without removing records. Review the intended diff and complete the code/workflow review when applicable.
4. If publication is authorized and datasets or generated split files changed, stage explicit paths and commit with a UTC timestamp:
   `git commit -m "data: $(date -u +%Y-%m-%dT%H:%M:%SZ) — events +N, promises +M"`
5. When authorized, push to origin: `git push origin main` (repo: `0x8338/dontforget`). Verify the remote head and its Pages validation/deployment; report any remaining limits.
6. If a same-day re-run produced no changes, skip the commit.

Page loading: the homepage reads the events window manifest (`events/index.json`) and fetches only windows whose `days` map contains the displayed date; the promises page streams due-month files one by one. Both render incrementally and have no load-more buttons.

## Historical Backfill (one-time, already done)

The archive contains selected events from 2000 onward, not complete historical
coverage. See the September 2026 fact-check ledgers for corrections and unresolved
research. The initial withholding policy was reversed: all collected originals
are retained. Use checkpoint totals rather than the original backfill estimates.

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

Use the canonical JSON datasets and current checkpoint schema. Check for duplicate
new candidates before appending, but do not merge existing records automatically.
The old `merge_events.py` and historical population plan predate this workflow;
do not use them for daily updates. Run the current validation and retention checks
described above.
