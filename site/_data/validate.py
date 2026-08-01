#!/usr/bin/env python3
"""Validate dontforget datasets before advancing the checkpoint.

Run: python3 site/_data/validate.py
Exit code 0 = clean; 1 = fix errors first.
"""

import datetime
import json
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

BASE = Path(__file__).resolve().parent
TODAY = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
ALLOWED_CATEGORIES = {
    "natural-disaster", "war", "gun-violence", "terrorism", "food-crisis", "industrial",
}
ALLOWED_STATUSES = {"kept", "broken", "partial", "pending", "kept (delayed)"}
EVENT_FIELDS = ("date", "title", "category", "location", "lives_lost", "description", "sources")
PROMISE_FIELDS = ("person", "role", "promise", "date_promised", "due_date", "status", "sources")

errors = []
warnings = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


events = json.loads((BASE / "events.json").read_text())
promises = json.loads((BASE / "promises.json").read_text())
checkpoint = json.loads((BASE / "checkpoint.json").read_text())

all_events = [e for lst in events.values() for e in lst]

# Events: structure
check(isinstance(events, dict), "events.json must be an object keyed by MM-DD")
for dkey, lst in events.items():
    check(len(dkey) == 5 and dkey[2] == "-", f"bad date key {dkey!r}")
    for e in lst:
        label = f"{e.get('date')} {e.get('title', '?')}"
        for field in EVENT_FIELDS:
            check(e.get(field) not in (None, ""), f"{label}: missing field {field}")
        check(e.get("date", "") >= "2000-01-01", f"{label}: date before 2000")
        check(e.get("date", "") <= TODAY, f"{label}: date in the future")
        check(e.get("date", "")[5:] == dkey, f"{label}: key {dkey} does not match date")
        check(e.get("category") in ALLOWED_CATEGORIES, f"{label}: bad category {e.get('category')}")
        check(isinstance(e.get("lives_lost"), int) and e["lives_lost"] > 0,
              f"{label}: lives_lost must be a positive integer")
        check(len(e.get("sources", [])) >= 2, f"{label}: fewer than 2 sources")

# Events: duplicates
exact = [k for k, v in Counter((e["date"], e["title"].strip().lower()) for e in all_events).items() if v > 1]
for k in exact:
    errors.append(f"duplicate event: {k}")

by_key = {}
for dkey, lst in events.items():
    for e in lst:
        norm = e["title"].lower()
        for other in by_key.get(dkey, []):
            if SequenceMatcher(None, norm, other).ratio() > 0.6:
                warn(f"possible duplicate on {dkey}: {norm!r} ~ {other!r}")
        by_key.setdefault(dkey, []).append(norm)

# Promises
check(isinstance(promises, list), "promises.json must be a list")
for p in promises:
    label = p.get("person", "?")
    for field in PROMISE_FIELDS:
        check(p.get(field) not in (None, ""), f"promise {label}: missing field {field}")
    check(p.get("date_promised", "") >= "2000-01-01", f"promise {label}: date before 2000")
    check(p.get("status") in ALLOWED_STATUSES, f"promise {label}: bad status {p.get('status')}")

# Promises: duplicates
exact_p = [k for k, v in Counter(
    (p["person"].strip().lower(), p["promise"].strip().lower()) for p in promises
).items() if v > 1]
for k in exact_p:
    errors.append(f"duplicate promise: {k}")

seen_p = []
for p in promises:
    norm_p = f"{p['person'].strip().lower()} :: {p['promise'].strip().lower()}"
    for other in seen_p:
        if SequenceMatcher(None, norm_p, other).ratio() > 0.82:
            warn(f"possible duplicate promise: {p['person']!r} ~ {other!r}")
    seen_p.append(norm_p)

# Checkpoint consistency
ev_cp = checkpoint.get("events", {})
pr_cp = checkpoint.get("promises", {})
check(ev_cp.get("total") == len(all_events),
      f"checkpoint events.total {ev_cp.get('total')} != actual {len(all_events)}")
check(pr_cp.get("total") == len(promises),
      f"checkpoint promises.total {pr_cp.get('total')} != actual {len(promises)}")
check(ev_cp.get("last_date", "") <= TODAY, "checkpoint events.last_date is in the future")
check(pr_cp.get("last_date", "") <= TODAY, "checkpoint promises.last_date is in the future")

print(f"events: {len(all_events)} entries across {len(events)} date keys")
print(f"promises: {len(promises)}")
for w in warnings:
    print(f"WARN: {w}")
if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)
print("OK")
