#!/usr/bin/env python3
"""Split the full datasets into small chunks for low-bandwidth pages.

Run after every data update, before validate.py:
    python3 site/_data/split_data.py

Outputs:
    site/_data/events/<YYYY-YYYY>.json — events grouped in 5-year windows
    site/_data/events/index.json       — window manifest
    site/_data/promises/index.json     — totals + due-month manifest
    site/_data/promises/<YYYY-MM>.json — one file per due month
"""

import datetime
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
EVENTS_DIR = BASE / "events"
PROMISES_DIR = BASE / "promises"
TODAY = datetime.date.today().isoformat()

EVENTS_DIR.mkdir(exist_ok=True)
PROMISES_DIR.mkdir(exist_ok=True)

events = json.loads((BASE / "events.json").read_text())
promises = json.loads((BASE / "promises.json").read_text())
all_events = [e for lst in events.values() for e in lst]

# Events: 5-year windows (2000-2004, 2005-2009, ...).
# Bucket every event in a single pass instead of rescanning all_events once per
# window (O(W x N) -> O(N)); each event's year is parsed exactly once.
year_of = {e["date"][:4] for e in all_events}
max_year = max(int(y) for y in year_of)
window_starts = list(range(2000, max_year + 1, 5))
buckets = {start: [] for start in window_starts}
for e in all_events:
    year = int(e["date"][:4])
    start = 2000 + ((year - 2000) // 5) * 5
    if start > window_starts[-1]:
        start = window_starts[-1]
    buckets[start].append(e)

windows = []
for start in window_starts:
    end = min(start + 4, max_year)
    items = buckets[start]
    days = {}
    for e in items:
        day = e["date"][5:]
        days[day] = days.get(day, 0) + 1
    key = f"{start}-{end}"
    (EVENTS_DIR / f"{key}.json").write_text(json.dumps(items, ensure_ascii=False, indent=1))
    windows.append({"key": key, "file": f"events/{key}.json", "count": len(items), "days": days})

windows.sort(key=lambda w: w["key"], reverse=True)
(EVENTS_DIR / "index.json").write_text(json.dumps({"windows": windows}, ensure_ascii=False, indent=2))

# Promises: manifest + one file per due month.
by_month = {}
unfiled = []
today_month = TODAY[:7]
for p in promises:
    month = p.get("due_date", "")[:7]
    if len(month) == 7 and month[4] == "-" and month[:4].isdigit() and month[5:].isdigit():
        by_month.setdefault(month, []).append(p)
    else:
        unfiled.append(p)

due_months = []
for month in sorted(by_month, reverse=True):
    items = by_month[month]
    (PROMISES_DIR / f"{month}.json").write_text(json.dumps(items, ensure_ascii=False, indent=1))
    due_months.append({
        "key": month,
        "file": f"promises/{month}.json",
        "count": len(items),
        "due": month <= today_month,
    })

due = [p for p in promises if p.get("due_date", "") <= TODAY]
manifest = {
    "total": len(promises),
    "due_total": len(due),
    "due_status": dict(Counter(p.get("status") for p in due)),
    "months": due_months,
    "unfiled": len(unfiled),
}
(PROMISES_DIR / "index.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

print(f"events: {len(all_events)} -> {len(windows)} five-year windows")
print(f"promises: {len(promises)} -> {len(due_months)} month files + index")
