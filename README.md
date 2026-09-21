# dontforget

A belief that some things shouldn't be forgotten.

This is a quiet archive of lives taken by violence and disaster since 2000 — and of the promises the world made, kept, and broken along the way. Published events require at least two public source records. The numbers exist so the people behind them are not forgotten.

## What it shows

- **Today page** — events associated with this date across history and their reported death tolls
- **Promises page** — public commitments, grouped by due date, with outcomes (kept/broken/partial/pending)

## How it works

UTC for everything. Each event has ≥2 public source records, with links to the evidence. No commentary — what happened, how many, where to read more. Reports can share an underlying source; two links are not necessarily independent confirmation.

## Data

Current counts and research dates are in [checkpoint.json](site/_data/checkpoint.json).
The [September 21 audit](research/fact-checks/2026-09-21/README.md) covers the
original 709 events and 449 promises. Its ledgers distinguish supported
corrections from unresolved claims. Withheld originals remain in the research
archive, not in the public totals; withholding does not mean an event or promise
was disproven.

The update routine researches new events and promises from the checkpoint.
Publication is a separate, authorized step. These datasets are curated samples,
not an exhaustive census. Death tolls may be estimates or cumulative figures;
the record descriptions state their scope. Promise summaries need not be exact
quotes, and a passed deadline alone does not prove an unknown outcome was broken.

The pages stay light for slow connections: events are served in five-year windows (only the windows that actually contain the day's events are fetched) and promises load month by month. Content streams in as each chunk arrives — no buttons, no waiting on the full archive.

Promise totals use the visitor's current UTC date, not stale build-time counts.
Delayed fulfillment is included in the kept total and remains explicitly labeled.

## Checks

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/pages.test.cjs
python3 site/_data/split_data.py
python3 site/_data/validate.py
```

Pull requests run these checks without deployment. Main-branch Pages deployment
requires the validation job to pass. Generated chunks are checked against the
canonical data; obsolete generated chunks are removed when rebuilding.
