# Archive Fact Check: 2026-09-21

Scope: all 709 existing events and 449 existing promises, followed by the
incremental update after the September 11 checkpoint.

## Preservation Correction

The initial integration incorrectly withheld 323 events and 300 promises when
details remained unresolved. The owner rejected that policy. All collected
records are now retained; a missing source, uncertain date, or unfinished check
does not establish falsity and must not remove an entry from the archive.

| Dataset | Original records retained | New records | Public dataset | Records with review notes |
| --- | ---: | ---: | ---: | ---: |
| Events | 709 | 13 | 722 | 322 |
| Promises | 449 | 5 | 454 | 300 |

As of September 21, the promises page includes 311 due records. Its stored
outcome counts are 109 kept (including 20 delayed), 109 broken, 40 partial and
53 pending. These are archive classifications, not a claim that every outcome
was independently re-established by this audit; record-level notes identify
the remaining questions.

## How Corrections Are Applied

- Fully supported corrections from the first integration are retained.
- For an incomplete check, only supported changes outside `unresolved_fields`
  are applied. An uncertain event identity preserves the original factual
  fields. A record-level unresolved result does not block supported corrections
  to other fields. No whole record is dropped.
- Original citations remain attached to restored records. Research sources are
  shown separately so a source supporting one detail is not presented as proof
  of every original claim.
- Empty legacy outcome evidence is explicitly marked as still to be documented.
  One impossible announcement/deadline ordering is represented with an unknown
  announcement date; the original value remains in `review.original_values`.
- The August 12 Beit Lahia entry remains visible with its headline and toll
  corrected: Anadolu explicitly withdrew the reported fatality. Zero here means
  no death confirmed by the corrected report, not a claim about the victim's
  eventual outcome. `correction.original_values` retains the earlier wording
  and toll; new positive-toll events still follow the normal evidence rules.
- The legacy `publication_ready` field records audit completeness only. It no
  longer controls whether an existing record appears on the site.
- Every record has a stable `archive_id`. `site/_data/retention.json` protects
  the collected identities; validation fails if a protected record disappears,
  even when totals and generated files have been rebuilt. New records must be
  registered there, and corrections must retain their assigned IDs.

`summary.json` records current totals and output hashes. Its content-change
counter includes field-level corrections and explicit missing-evidence notes;
it is not a count of independently verified outcomes.
`review-backlog.json` preserves the original and retained version of every
record needing follow-up. `quarantine.json` is a historical snapshot of the
initial, rejected exclusion policy, not a list of currently hidden records.

## Evidence And Coverage

Check attribution, wording, announcement date, deadline and outcome separately.
An announcement is not fulfillment, an unlocated source is not disproof, and a
passed deadline alone is not proof of failure. Distinguish event dates from
publication dates, local dates from UTC, and deaths from missing persons.

The six batch ledgers cover every original exactly once:

| File | Records checked | Records needing follow-up |
| --- | ---: | ---: |
| events-2000-2008.json | 171 | 76 |
| events-2009-2017.json | 180 | 92 |
| events-2018-2025.json | 160 | 69 |
| events-2026.json | 198 | 85 |
| promises-000-223.json | 224 | 168 |
| promises-224-448.json | 225 | 132 |

`update.json` records the new-event/promise research and candidates not yet added.
New candidates are different from collected records: an unverified new candidate
need not be added, but an incomplete recheck must not erase an existing entry.
The update researched September 12-21 UTC, closes the checkpoint through
September 20, and leaves September 21 provisional. The collection is not an
exhaustive census of events or promises worldwide.

## Validation

The restoration adds regression tests for retaining unresolved records,
preserving original citations, applying only supported field corrections,
displaying review notes without hiding promises, stable identities, and rejection
of record deletion even after checkpoint totals are updated. Structural checks,
source-link safety, UTC counts and generated/canonical consistency still apply.
Legacy citation gaps require membership in the fixed `legacy-review.json`
baseline inventory and an explicit review note. Retention protection does not
exempt new records from evidence links or known announcement dates.

Publication and the subsequent workflow-documentation update are separate steps.
No organization or repository settings are changed by this correction.
