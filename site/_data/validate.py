#!/usr/bin/env python3
"""Validate dontforget datasets before advancing the checkpoint.

Run: python3 site/_data/validate.py
Exit code 0 = clean; 1 = fix errors first.
"""

import datetime
import json
import re
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


def similar_enough(a: str, b: str, threshold: float) -> bool:
    """Cheap pre-filter before the expensive SequenceMatcher ratio.

    ratio = 2*M/(len(a)+len(b)) with M <= min(len(a), len(b)), so if the
    theoretical maximum is below the threshold the pair cannot match.
    """
    total = len(a) + len(b)
    if total == 0 or 2 * min(len(a), len(b)) / total < threshold:
        return False
    # autojunk=False keeps the ratio symmetric and order-independent.
    return SequenceMatcher(None, a, b, autojunk=False).ratio() > threshold


def token_jaccard(a: str, b: str) -> float:
    """Fraction of shared significant tokens (plural-normalized)."""
    def toks(s):
        out = set()
        for w in re.findall(r"[a-z0-9]+", s.lower()):
            if w.endswith("s") and len(w) > 4 and not w.endswith("ss"):
                w = w[:-1]
            out.add(w)
        return out
    sa, sb = toks(a), toks(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def event_duplicate(a: str, b: str) -> bool:
    """True for real near-duplicate event titles, not merely same-topic ones.

    High character similarity alone flags false positives that only share
    generic words ('bombings', 'earthquake', 'drone strike'), so also require
    a substantial overlap of distinctive tokens unless the titles are nearly
    identical.
    """
    ratio = SequenceMatcher(None, a, b, autojunk=False).ratio()
    if ratio > 0.8:
        return True
    return ratio > 0.6 and token_jaccard(a, b) >= 0.5


events = json.loads((BASE / "events.json").read_text())
promises = json.loads((BASE / "promises.json").read_text())
checkpoint = json.loads((BASE / "checkpoint.json").read_text())

all_events = [e for lst in events.values() for e in lst]

# Events: structure
check(isinstance(events, dict), "events.json must be an object keyed by MM-DD")

DOMAIN_RE = re.compile(r"[a-z0-9-]+(\.[a-z0-9-]+)+\.[a-z]{2,}")


def check_source(label, field, source):
    check(isinstance(source, str) and source.strip(), f"{label}: empty {field} entry")
    check("http" not in source.lower(), f"{label}: {field} contains a URL: {source[:60]}")
    check(not DOMAIN_RE.search(source.lower()), f"{label}: {field} contains a bare domain: {source[:60]}")
    check(len(source) <= 120, f"{label}: {field} entry too long ({len(source)} chars)")


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
        for s in e["sources"]:
            check_source(label, "event source", s)

# Events: duplicates
exact = [k for k, v in Counter((e["date"], e["title"].strip().lower()) for e in all_events).items() if v > 1]
for k in exact:
    errors.append(f"duplicate event: {k}")

by_key = {}
for dkey, lst in events.items():
    seen = by_key.setdefault(dkey, [])
    for e in lst:
        norm = e["title"].lower()
        for other in seen:
            if event_duplicate(norm, other):
                warn(f"possible duplicate on {dkey}: {norm!r} ~ {other!r}")
        seen.append(norm)

# Promises
check(isinstance(promises, list), "promises.json must be a list")
for p in promises:
    label = p.get("person", "?")
    for field in PROMISE_FIELDS:
        check(p.get(field) not in (None, ""), f"promise {label}: missing field {field}")
    check(p.get("date_promised", "") >= "2000-01-01", f"promise {label}: date before 2000")
    check(p.get("status") in ALLOWED_STATUSES, f"promise {label}: bad status {p.get('status')}")
    check(len(p.get("sources", [])) >= 1, f"promise {label}: no sources")
    for s in p["sources"]:
        check_source(label, "promise source", s)
    if "source_urls" in p:
        check(isinstance(p["source_urls"], list) and len(p["source_urls"]) == len(p["sources"]),
              f"promise {label}: source_urls must match sources length")
        for u in p["source_urls"]:
            check(u is None or u.startswith("http"), f"promise {label}: bad source_url entry {u}")

# Promises: overdue but still pending
for p in promises:
    if p.get("due_date", "") <= TODAY and p.get("status") == "pending":
        warn(f"overdue pending promise: {p['person']!r} due {p['due_date']}: {p['promise'][:70]}")

# Promises: duplicates
exact_p = [k for k, v in Counter(
    (p["person"].strip().lower(), p["promise"].strip().lower()) for p in promises
).items() if v > 1]
for k in exact_p:
    errors.append(f"duplicate promise: {k}")

seen_p = {}
for p in promises:
    person = p["person"].strip().lower()
    norm_p = f"{person} :: {p['promise'].strip().lower()}"
    for other in seen_p.get(person, ()):
        if similar_enough(norm_p, other, 0.82):
            warn(f"possible duplicate promise: {p['person']!r} ~ {other!r}")
    seen_p.setdefault(person, []).append(norm_p)

# Checkpoint consistency
ev_cp = checkpoint.get("events", {})
pr_cp = checkpoint.get("promises", {})
check(ev_cp.get("total") == len(all_events),
      f"checkpoint events.total {ev_cp.get('total')} != actual {len(all_events)}")
check(pr_cp.get("total") == len(promises),
      f"checkpoint promises.total {pr_cp.get('total')} != actual {len(promises)}")
check(ev_cp.get("last_date", "") <= TODAY, "checkpoint events.last_date is in the future")
check(pr_cp.get("last_date", "") <= TODAY, "checkpoint promises.last_date is in the future")

# Split files (generated by split_data.py)
events_index = BASE / "events" / "index.json"
if events_index.exists():
    idx = json.loads(events_index.read_text())
    total = sum(w.get("count", 0) for w in idx.get("windows", []))
    check(total == len(all_events), f"events split index count {total} != {len(all_events)}")
    for w in idx.get("windows", []):
        check((BASE / w["file"]).exists(), f"missing events split file {w['file']}")
        if w.get("days"):
            check(sum(w["days"].values()) == w.get("count"),
                  f"events split days mismatch in window {w['key']}")

promises_index = BASE / "promises" / "index.json"
if promises_index.exists():
    idx = json.loads(promises_index.read_text())
    check(idx.get("total") == len(promises), "promises split index total mismatch")
    due_now = sum(1 for p in promises if p.get("due_date", "") <= TODAY)
    check(idx.get("due_total") == due_now, f"promises split due_total {idx.get('due_total')} != {due_now}")
    for m in idx.get("months", []):
        check((BASE / m["file"]).exists(), f"missing promises month file {m['file']}")

print(f"events: {len(all_events)} entries across {len(events)} date keys")
print(f"promises: {len(promises)}")
for w in warnings:
    print(f"WARN: {w}")
if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)
print("OK")
