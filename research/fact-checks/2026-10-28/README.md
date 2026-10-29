# Dataset update: 2026-10-28 UTC

## Scope

Local-only incremental refresh from `origin/main` at `aa42f12`. The original
checkout was not moved. Research covered October 25-27 and the beginning of
October 28, plus two newly reported incidents from October 23-24. The checkpoint
ends on October 27: October 28 is incomplete and must be revisited.

This is not a new exhaustive fact-check of the entire historical archive.
Every one of the 55 baseline pending promises due by October 28 was examined
for its existing claim, deadline, evidence and remaining verification needs.
Targeted searches supplied outcome evidence or follow-up leads where available.
Some scope/deadline decisions rely on the retained review rather than newly
verified outcomes. The per-record limits are explicit in
[overdue-review.json](overdue-review.json).

## Preservation and reconciliation

Both columns use **2026-10-28 UTC**, not different dates.

| Measure | Before | After |
| --- | ---: | ---: |
| Events | 774 | 779 |
| Promises | 460 | 463 |
| Due promises | 315 | 315 |
| Kept | 96 | 98 |
| Kept (delayed) | 20 | 20 |
| Broken | 119 | 121 |
| Partial | 44 | 44 |
| Pending | 181 | 180 |
| Overdue pending | 55 | 51 |
| Events with review metadata | 322 | 325 |
| Promises with review metadata | 341 | 337 |

All 774 original event IDs and all 460 original promise IDs must remain present.
No record is deleted, merged, hidden or quarantined. Eight new IDs are appended
to `retention.json`; `legacy-review.json` is unchanged. Existing dates and
deadlines are unchanged. All three new promises have future deadlines, explaining
why the due count stays at 315. Four pending outcomes are resolved and three
new pending records are added, explaining the net pending change of minus one.

The old checkpoint's promise-review counter of 300 was stale: the baseline
dataset actually had 341 review objects. The new value of 337 reflects removal
of four resolved status-only flags, not removal of promises. The original full
records, including those flags and their previous evidence, are preserved in
[corrections.json](corrections.json).

## Additions

Five events, with two linked publications each:

- `events-20261023-binnari-attack`
- `events-20261024-shirka-attacks`
- `events-20261026-gulmi-suv-crash`
- `events-20261026-kyiv-missile-attack`
- `events-20261026-daraa-airstrikes`

The Binnari, Shirka and Daraa counts are attributed preliminary reports, not
independently reconciled final totals. Their visible review notes retain the
counting differences. Do not sum successive bulletins or combine separate
attacks. Gulmi's two local reports establish October 26, not the October 27
date used by a later aggregator. The Kyiv entry does not add the following
morning's wider regional attack totals.

Three Track A government entries have explicit years or a fiscal-year endpoint:

- `promises-20261026-uk-evm-savings`: DWP's savings forecast, distinct from the
  wider anti-fraud programme. March 31, 2031 is the UK fiscal-year endpoint.
- `promises-20261026-uk-regenerative-evidence`: an evidence call in 2027, not
  adoption of a standard. December 31 is a stated year-end normalization.
- `promises-20261026-uk-carbon-recognition`: publication of recognition details
  later in 2026, not a guarantee about credit-market performance.

The next expansion focus is Track B. The expansion is UK-focused this time;
future Track A sweeps should diversify country coverage. Canada's October 26
Indigenous Workforce Readiness Fund announcement was considered but not added:
the four-year funding period did not identify an unambiguous starting fiscal
year, and an assumed anniversary would imply unsupported precision.

## Outcome corrections

- **GB300 shipments: pending to kept.** Supermicro's September 11, 2025 notice
  reports volume deliveries during the promised half-year. This resolves the
  prior distinction between a production ramp and actual deliveries.
  [Supermicro](https://ir.supermicro.com/news/news-details/2025/Supermicro-Begins-Volume-Shipments-of-NVIDIA-Blackwell-Ultra-Systems-and-Rack-Plug-and-Play-Data-Center-Scale-Solutions/default.aspx)
- **Meta AI users: pending to kept.** The October 2025 company publication
  explicitly exceeds the billion-user threshold. The metric remains
  company-reported, not independently audited.
  [Meta](https://about.fb.com/news/2025/10/improving-your-recommendations-apps-ai-meta)
- **India fiscal 2016-17 deficit: pending to broken.** CAG reports 3.54% of GDP,
  above the original 3.0% target. This does not judge the later relaxed target.
  The PDF's prose on printed page 35 establishes the result; screenshot retrieval
  failed, so no claim depends solely on visually reading the table.
  [CAG, chapter 1](https://cag.gov.in/webroot/uploads/download_audit_report/2017/Chapter_1_Overview_of_Union_Finances_2016-17_of_Report_No.44_of_2017_-_Financial_Audit_on_Accounts_of_the_Union_Government.pdf)
- **Basel III original schedule: pending to broken.** The oversight body moved
  the January 2022 start to January 2023. This grades the original schedule,
  not the reason for postponement or all jurisdictions' eventual implementation.
  [BIS, March 27, 2020](https://www.bis.org/press/p200327.htm)

## Research limits and next checks

The 51 still-pending records are retained and remain visible. Their uncertainty
is not evidence of failure. Several are forecasts, recommendations, appeals or
conditional commitments for which a simple kept/broken grade would misstate the
claim. No schema or classification-policy change is made in this data refresh.

Priority follow-ups from [the ledger](overdue-review.json): Oracle's fiscal 2026
actual capex; the World Bank's 2024 PPP ranking; a readable FIFA match record for
Ronaldo; the dated Rogue Squadron schedule removal; IDA20's retrospective; and
the exact date of Mexico's national school-phone proposal. Search excerpts are
leads, not substitutes for the outstanding scope and timing checks.

New-event candidates not added are separate from the retained archive:

- Gero, Nigeria: reports differ on October 26 evening versus October 27 early
  morning, and six versus seven deaths. Resolve the incident timestamp first.
  [Premium Times](https://www.premiumtimesng.com/regional/north-central/920799-six-killed-in-another-plateau-attack-as-governor-vows-to-track-down-killers.html),
  [Channels Television](https://www.channelstv.com/2026/10/27/mutfwang-vows-to-track-down-gero-killers-urges-communities-to-remain-vigilant/)
- Umm Zar, Syria: a report of three landmine deaths on October 27 needs a second
  corroborating publication.
  [Welat TV](https://www.welattv.net/en/node/32966)
- Haiti flooding: the October 27 report spans several preceding days; establish
  fatal-incident dates and corroboration before creating a dated record.
  [CANA](https://www.cananews.com/four-killed-as-heavy-rains-batter-haiti/)

These gaps do not justify dropping any existing record. The checkpoint denotes
an incremental research pass, not a claim that every worldwide event was found.

## Verification

Before completion, run the existing Python and JavaScript suites, regenerate
split datasets, validate the canonical and generated data, and compare stable
IDs/statuses against `aa42f12`. Also check that the overdue ledger covers exactly
the 55 baseline candidates and that each decision matches its resulting record.
Run `git diff --check` and `codex review --uncommitted`. This refresh was prepared
locally; on October 29 the owner authorised publication together with the next
day's update. See the October 29 report for the combined validation results.
