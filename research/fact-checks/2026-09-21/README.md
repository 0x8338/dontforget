# Archive Fact Check: 2026-09-21

Scope: all 709 existing events and 449 existing promises, followed by the
incremental update after the 2026-09-11 checkpoint. The audit pass is complete;
this is not a certification that every original claim was verified. Unsupported
records remain preserved for follow-up, outside the public datasets.

## Integrated Result

| Dataset | Originals checked | Factual corrections retained | Source-only updates | Withheld originals | New records | Public dataset |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Events | 709 | 348 | 38 | 323 | 13 | 399 |
| Promises | 449 | 148 | 1 | 300 | 5 | 154 |

Every original identity has exactly one ledger entry. `summary.json` records
counts, the original commit, and output hashes; `quarantine.json` preserves all
623 withheld originals, proposed corrections, sources, and remaining blockers.
Some corrections are supported but do not resolve every material claim, so the
number of correction findings is larger than the corrections retained above.

The update researched September 12-21 UTC, closes the checkpoint through
September 20, and leaves September 21 provisional. It added 13 events and five
promises, recording Track A as the expansion focus. The resulting archive is a
curated sample, not complete coverage of all countries or all events.

Corrections include UTC-day shifts, revised tolls, attribution, announcement
dates, actual deadline scope, and outcome evidence. Follow-up outcome research
resolved 13 initially pending assessments, including the 737 MAX's delayed
return to service and Lordstown's delayed initial production and deliveries.
Promise wording distinguishes forecasts, collective targets, and conditional
commitments from unconditional personal guarantees.

As of September 21, 87 retained promises are due: 32 kept (including six
delayed), 11 broken, two partial, and 42 pending. The pending entries have dated
reasons explaining the remaining outcome question. A missed date alone was not
used to manufacture a failure judgment.

## Evidence Rules

- Check event identity, date, location, death toll and material description claims.
- Check each promise's attribution, wording, announcement date, deadline and
  outcome separately. A commitment announcement is not evidence of fulfillment.
- Prefer primary records and reputable reporting. Distinguish event dates from
  publication dates, local dates from UTC, and initial tolls from later revisions.
- Record disagreement and access limitations. A failed search does not establish
  that a claim is false. Do not invent exact quotations or deadlines.
- `verified` means the checked sources support all material fields; `correction`
  means evidence supports a specific proposed change; `unresolved` means some
  material claims could not be established. Unresolved claims are not verified.
- Sources in the canonical datasets remain short names. Evidence URLs belong in
  aligned `source_urls` arrays. Research ledgers stay outside the published site.

## Ledger Format

Each batch records `dataset`, `scope`, `as_of` and `records`. Every record has:

- `key`: original `date` and `title` for an event, or `person`, `promise` and
  `date_promised` for a promise;
- `result`: `verified`, `correction` or `unresolved`;
- `checked_fields`: fields actually checked against evidence;
- `sources`: objects with a publication `name` and an exact `url`;
- `note`: concise findings, remaining uncertainty and search/access limitations;
- `changes`: proposed canonical field replacements, or an empty object.
- `publication_ready`: true only if the corrected record's material claims are
  supported; a supported correction can still leave another claim unresolved.

The research batches do not edit the canonical datasets. The maintainer reviews
and integrates supported corrections after checking coverage and collisions.
Unresolved entries are withheld from the public datasets, not declared false.
Originals and proposed corrections are preserved in `quarantine.json`.
`update.json` records the subsequent research window, new records and withheld
candidates. It is not evidence that every event worldwide was found.

## Batches

| File | Scope | Status |
| --- | --- | --- |
| events-2000-2008.json | Events dated 2000-2008 | Complete: 171 checked, 95 ready, 76 withheld |
| events-2009-2017.json | Events dated 2009-2017 | Complete: 180 checked, 88 ready, 92 withheld |
| events-2018-2025.json | Events dated 2018-2025 | Complete: 160 checked, 91 ready, 69 withheld |
| events-2026.json | Existing events dated 2026 | Complete: 198 checked, 112 ready, 86 withheld |
| promises-000-223.json | Existing promises at indexes 0 through 223 | Complete: 224 checked, 56 ready, 168 withheld |
| promises-224-448.json | Existing promises at indexes 224 through 448 | Complete: 225 checked, 93 ready, 132 withheld |

Checkpoint dates must advance only for dates actually researched. A structural
validation pass or regenerated manifest is not a completed fact check.
The update closes coverage through September 20 UTC and records provisional
September 21 research separately, because that UTC day is still in progress.

## Software And Validation

- Source links are visible and escaped; promise outcome evidence is displayed.
- Promise totals and filters use the current UTC date, including delayed
  fulfillment in the kept count. Chunk failures no longer stop later loads.
- Validation rejects invalid calendar dates, unsupported status values, missing
  links, non-positive/non-integer tolls, and generated/canonical data mismatches.
- Rebuilding removes obsolete generated chunks so withheld data cannot remain in
  stale public chunk files. Pull requests validate without deploying; main Pages
  deployment depends on successful validation.
- Passed 21 Python tests, six Node page tests, generation, structural validation,
  and `git diff --check`.
- Browser checks passed at widths 1440, 390 and 320: complete final-data loading,
  UTC totals, all promise filters, an event filter, evidence links, no JavaScript
  errors, and no horizontal overflow. Screenshots were inspected. External font
  requests were blocked during this check, exercising the fallback fonts.
- Validator duplicate warnings were reviewed: the two September 19 strikes are
  in different locations; the November 27 mine disasters occurred in different
  years and provinces. Overdue-pending warnings remain intentionally visible.

Same-data five-run benchmark (399 events, 154 promises; milliseconds, including
process startup):

| Script | Baseline mean / median | Updated mean / median |
| --- | ---: | ---: |
| split_data.py | 306.8 / 219.5 | 99.6 / 112.6 |
| validate.py | 146.0 / 55.0 | 95.8 / 65.9 |

The validator's median increased with the additional integrity checks. Large
startup outliers make these local measurements unsuitable for a general speedup
claim. The baseline scripts ran against the same final canonical data in a
temporary directory, not against the larger original archive.

All changes are local. No commit, push, Pages deployment, or GitHub setting
change was performed by this update.
