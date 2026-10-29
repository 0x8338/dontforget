# Dataset update: 2026-10-29 UTC

## Scope and preservation

This local-only update continues the unpublished October 28 work in
`dontforget-update-20261028`, based on `origin/main` at `aa42f12`. The older main
checkout was not moved. Prior additions and corrections remain intact.
Research covers October 28 and the beginning of October 29, plus a newly checked
October 26 event. Both checkpoints stop at October 28; October 29 remains open.
The checkpoint records an incremental research pass, not exhaustive worldwide
coverage or a new audit of the entire historical archive.

The pre-edit canonical JSON and retention inventory were copied to a local
temporary backup. All 779 baseline event IDs and 463 baseline promise IDs are
retained, along with all earlier remote IDs. No event facts were changed or
removed. Content warnings were prepended to the prior Binnari and Shirka
additions; only the two promise records below received factual corrections.
Seven IDs were appended to
`retention.json`; the fixed `legacy-review.json` inventory was not changed.

Both columns below use **2026-10-29 UTC**:

| Measure | Before this run | After this run |
| --- | ---: | ---: |
| Events | 779 | 783 |
| Promises | 463 | 466 |
| Due promises | 315 | 315 |
| Kept | 98 | 99 |
| Kept (delayed) | 20 | 20 |
| Broken | 121 | 122 |
| Partial | 44 | 44 |
| Pending | 180 | 181 |
| Overdue pending | 51 | 49 |
| Events with review metadata | 325 | 329 |
| Promises with review metadata | 337 | 336 |

Three additions have future deadlines. Two pending outcomes were resolved, so
pending increases by one while overdue pending falls by two. The one fewer
promise review object is Blackwell's resolved status flag, not a removed record.
Compared with remote `aa42f12`, the combined unpublished work adds nine events
and six promises: 774 to 783 events, and 460 to 466 promises.

## Four events

- **October 26, Nyala:** MSF reports 36 bodies received at its supported hospital
  after market and residential-area strikes. This is a hospital count, not an
  independently reconciled total or a civilian-only count. AP reports competing
  estimates, retained in the visible review note. This is distinct from the
  October 16 Nyala event already in the archive.
  [MSF](https://www.msf.org/people-killed-and-150-injured-sudanese-armed-forces-strike-nyala),
  [AP via KSAT](https://www.ksat.com/news/world/2026/10/28/strike-on-darfur-market-killed-civilians-selling-food-to-fighters-witnesses-say/).
- **October 28, Urda:** 68 deaths reported by regional authorities after a train
  collision. The toll is provisional; injury estimates and preliminary causal
  explanations are not treated as a final investigation. AFP and RTE establish
  Wednesday October 28, despite an SBS report saying October 27.
  [AFP](https://www.afp.com/en/spain-high-speed-train-crash-kills-68-injures-over-100),
  [RTE](https://www.rte.ie/news/world/2026/1028/1597051-spain-train-crash/).
- **October 28, Tharparkar:** Geo's updated report gives eight ambulance-fire
  deaths after one injured person died in transit. The Express Tribune's
  explicit Wednesday 22:40 local time places the event at 17:40 UTC, not on
  the October 29 publication date. Geo's inconsistent closing reference to
  Thursday is flagged, as are the initial seven-death count and uncertain cause.
  [The Express Tribune](https://tribune.com.pk/story/2637449/7-dead-five-injured-as-ambulance-catches-fire-in-sindhs-tharparkar?amp=1),
  [Geo News](https://www.geo.tv/latest/688756-seven-killed-as-ambulance-catches-fire-after-oxygen-cylinder-blast-in-tharparkar).
- **October 28, Rafah:** the initial three deaths are updated to four after a
  wounded person died, according to AFP's reporting of hospital/civil-defence
  accounts. The separate Khan Yunis death in AFP's five-death headline is not
  included in this event.
  [WAFA](https://english.wafa.ps/Pages/Details/176412),
  [AFP via Arab News](https://www.arabnews.com/middle-east/gaza-health-officials-say-israeli-strikes-kill-5-3008739).

## Three corporate commitments

- Amazon: more than EUR 16 billion of investment in Germany during 2027.
  The October 20 company account explicitly dates the announcement to the
  previous day's summit, so `date_promised` is October 19.
  [Amazon](https://www.aboutamazon.eu/news/company-news/amazons-commitment-to-germany).
- Generac: expected USD 2.4 billion of initial Amazon generator deliveries in
  2027-28. Use the September 16 filing date, not the October 28 reiteration;
  the warrant's USD 8 billion threshold is not the delivery target.
  [Form 8-K, page 2 prose](https://investors.generac.com/static-files/7fd7f15a-24c2-4822-b08b-9a2b3319dab6),
  [October 28 results](https://investors.generac.com/news-releases/news-release-details/generac-reports-third-quarter-2026-results).
- Charger Logistics: a non-binding intention to buy up to 500 Aurora-powered
  trucks, with deliveries in 2027-28 subject to a final agreement. Keep that
  condition explicit; do not represent the MOU as firm orders or fulfillment.
  [Aurora/Business Wire via Nasdaq](https://www.nasdaq.com/press-release/charger-logistics-and-aurora-begin-scaling-autonomous-fleet-500-trucks-2026-10-26).

Year-end deadlines are transparent normalizations of the stated calendar years,
not invented exact delivery dates. All three remain pending. Next rotation:
**Track C, international organisations and treaties**.

## Overdue review and corrections

All 51 pre-update overdue pending records were read with their existing claim,
deadline, evidence limits and October 28 review. The per-record decisions and
verification basis are in [overdue-review.json](overdue-review.json).

Fresh outcome searches focused on Blackwell availability, Rogue Squadron and
Boston NVAQC. For the other records, the prior dated research and specific
unresolved scope/timing reasons are carried forward explicitly; this is not a
claim of 51 fresh external verifications. The remaining 49 records remain
visible and pending. No outcome was downgraded because evidence was unavailable.

- Blackwell availability: pending to kept. Dell's December 9, 2024 announcement
  confirms shipments to CoreWeave within 2024. This resolves partner hardware
  availability, not the later start of general cloud service availability.
  [CoreWeave / Dell](https://investors.coreweave.com/news/news-details/2024/CoreWeave-and-Dell-Technologies-Extend-Relationship-to-Deliver-AI-at-Scale/default.aspx).
- Rogue Squadron: pending to broken for the original 2023 release schedule.
  Reuters reported calendar removal in 2022; Jenkins still owed a draft in
  March 2024. No claim of permanent cancellation is made. Exact December 22
  precision and broad original citation gaps remain flagged.
  [Reuters](https://yall1067.com/2022/09/15/disney-removes-star-wars-spinoff-rogue-squadron-from-calendar-variety/),
  [TheWrap](https://www.thewrap.com/patty-jenkins-star-wars-rogue-squadron-still-alive/).
- Boston NVAQC: unchanged pending. Retrieved material still describes an opening
  plan rather than establishing a dated operational opening. Headline wording
  alone does not demonstrate fulfillment; the Japanese quantum centre is a
  different facility.

The complete pre-edit values for both changed promises are preserved in
[corrections.json](corrections.json), including their original evidence/reviews.
The September withholding language on the touched Rogue Squadron note is
removed because it conflicts with the current preservation policy.

## Research limits and follow-ups

Some direct page requests failed despite readable indexed article text: the
Express Tribune, RTE, KSAT and Nasdaq pages. Their retrieved search text supplied
the cited passages, corroborated by accessible Geo, AFP, MSF or company material.
Do not describe those failures as successful live-page checks. The Dell earnings
transcript returned 404, so the outcome correction instead uses the readable
December 9 company release. No claim depends on an unread PDF table.

Haiti's four reported flood deaths remain a candidate because reporting covers
several days without assigning each death to a verified event date.
[CBC/CMC](https://www.cbc.bb/news/regional-news/four-killed-as-heavy-rains-batter-haiti/).
An aggregator's cyclone-fatality claim was not promoted without corroboration.
These unadded candidates are not deletions from the collected archive.
Continue the other October 28 ledger follow-ups; do not reset the archive or
bulk-reprocess previously covered days. Research before 02:00 UTC on October 29
cannot close that day's coverage.

## Verification

The existing Python suite passed all 34 tests and the JavaScript suite passed
all eight tests. Split files were regenerated and validation ended in `OK`.
Retention checks against both the pre-edit snapshot and `aa42f12` found no lost
IDs. The overdue ledger covers exactly all 51 baseline candidates, matches their
resulting statuses, and preserves full originals for the two corrections.

The 55 validator warnings consist of 49 documented overdue pending records and
six pre-existing fuzzy duplicate candidates. Five candidates are event title
pairs and one is the IMF promise pair. They are not evidence authorising a
merge or removal, and none involves this run's additions.

`codex review --uncommitted` identified missing content warnings in the prior
Binnari and Shirka additions. The warnings were added without changing factual
content or tolls, then generated data was refreshed. The reviewed diff also
includes the preserved October 28 work. The final review found no actionable
defects. The owner subsequently authorised committing and pushing the combined
October 28-29 updates to `origin/main` and verifying the Pages deployment.
