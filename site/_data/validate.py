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
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parent
TODAY = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
ALLOWED_CATEGORIES = {
    "natural-disaster", "war", "gun-violence", "terrorism", "food-crisis", "industrial",
}
ALLOWED_STATUSES = {"kept", "broken", "partial", "pending", "kept (delayed)"}
EVENT_FIELDS = ("date", "title", "category", "location", "lives_lost", "description", "sources")
PROMISE_FIELDS = ("person", "role", "promise", "date_promised", "due_date", "status", "description", "evidence", "sources")

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
    if not isinstance(source, str):
        return
    check("http" not in source.lower(), f"{label}: {field} contains a URL: {source[:60]}")
    check(not DOMAIN_RE.search(source.lower()), f"{label}: {field} contains a bare domain: {source[:60]}")
    check(len(source) <= 120, f"{label}: {field} entry too long ({len(source)} chars)")


def check_date(value, label):
    try:
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError
        datetime.date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label}: invalid calendar date {value!r}")
        return False
    return True


def check_sources(record, label, minimum):
    sources = record.get("sources", [])
    check(isinstance(sources, list), f"{label}: sources must be a list")
    if not isinstance(sources, list):
        return
    check(len(sources) >= minimum, f"{label}: fewer than {minimum} sources")
    for source in sources:
        check_source(label, "source", source)
    if "source_urls" not in record:
        errors.append(f"{label}: missing evidence links (source_urls)")
        return
    urls = record["source_urls"]
    check(isinstance(urls, list) and len(urls) == len(sources),
          f"{label}: source_urls must match sources length")
    if not isinstance(urls, list):
        return
    for url in urls:
        if url is None:
            errors.append(f"{label}: missing evidence link")
            continue
        try:
            parsed = urlsplit(url) if isinstance(url, str) else None
            valid = parsed is not None and parsed.scheme in {"http", "https"} and parsed.hostname
        except ValueError:
            valid = False
        check(bool(valid), f"{label}: invalid source URL {url!r}")


for dkey, lst in events.items():
    check_date("2000-" + dkey, f"date key {dkey!r}")
    for e in lst:
        label = f"{e.get('date')} {e.get('title', '?')}"
        for field in EVENT_FIELDS:
            check(e.get(field) not in (None, ""), f"{label}: missing field {field}")
        if check_date(e.get("date"), label):
            check(e["date"] >= "2000-01-01", f"{label}: date before 2000")
            check(e["date"] <= TODAY, f"{label}: date in the future")
            check(e["date"][5:] == dkey, f"{label}: key {dkey} does not match date")
        check(e.get("category") in ALLOWED_CATEGORIES, f"{label}: bad category {e.get('category')}")
        check(type(e.get("lives_lost")) is int and e["lives_lost"] > 0,
              f"{label}: lives_lost must be a positive integer")
        check_sources(e, label, 2)

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
    promised_valid = check_date(p.get("date_promised"), f"promise {label} date_promised")
    due_valid = check_date(p.get("due_date"), f"promise {label} due_date")
    if promised_valid:
        check("2000-01-01" <= p["date_promised"] <= TODAY,
              f"promise {label}: date_promised before 2000 or in the future")
    if promised_valid and due_valid:
        check(p["due_date"] >= p["date_promised"],
              f"promise {label}: due_date precedes date_promised")
    check(p.get("status") in ALLOWED_STATUSES, f"promise {label}: bad status {p.get('status')}")
    evidence = p.get("evidence")
    check((isinstance(evidence, str) and bool(evidence.strip())) or
          (isinstance(evidence, list) and bool(evidence) and
           all(isinstance(item, str) and item.strip() for item in evidence)),
          f"promise {label}: evidence must contain a nonempty explanation")
    check_sources(p, f"promise {label}", 1)

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
check_date(ev_cp.get("last_date"), "checkpoint events.last_date")
check_date(pr_cp.get("last_date"), "checkpoint promises.last_date")


def read_chunk(filename, directory):
    relative = Path(filename)
    if relative.parent != Path(directory) or relative.suffix != ".json":
        errors.append(f"invalid split file path {filename!r}")
        return None
    path = BASE / relative
    if not path.is_file():
        errors.append(f"missing split file {filename}")
        return None
    try:
        content = json.loads(path.read_text())
    except (ValueError, OSError) as exc:
        errors.append(f"invalid split file {filename}: {exc}")
        return None
    check(isinstance(content, list), f"split file {filename} must contain a list")
    return content if isinstance(content, list) else None

# Split files (generated by split_data.py)
events_index = BASE / "events" / "index.json"
check(events_index.is_file(), "missing events split index")
if events_index.exists():
    idx = json.loads(events_index.read_text())
    total = sum(w.get("count", 0) for w in idx.get("windows", []))
    check(total == len(all_events), f"events split index count {total} != {len(all_events)}")
    split_events = []
    for w in idx.get("windows", []):
        items = read_chunk(w["file"], "events")
        if items is not None:
            split_events.extend(items)
            check(len(items) == w.get("count"), f"events chunk count mismatch in {w['key']}")
            check(dict(Counter(e.get("date", "")[5:] for e in items)) == w.get("days"),
                  f"events chunk days mismatch in {w['key']}")
        if w.get("days"):
            check(sum(w["days"].values()) == w.get("count"),
                  f"events split days mismatch in window {w['key']}")
    check(Counter(json.dumps(e, sort_keys=True) for e in split_events) ==
          Counter(json.dumps(e, sort_keys=True) for e in all_events),
          "events split contents differ from canonical events")

promises_index = BASE / "promises" / "index.json"
check(promises_index.is_file(), "missing promises split index")
if promises_index.exists():
    idx = json.loads(promises_index.read_text())
    check(idx.get("total") == len(promises), "promises split index total mismatch")
    as_of = idx.get("as_of")
    if check_date(as_of, "promises split as_of"):
        check(as_of <= TODAY, "promises split as_of is in the future")
        due = [p for p in promises if p.get("due_date", "") <= as_of]
        check(idx.get("due_total") == len(due), "promises split due_total mismatch at as_of")
        check(idx.get("due_status") == dict(Counter(p.get("status") for p in due)),
              "promises split due_status mismatch at as_of")
    split_promises = []
    for m in idx.get("months", []):
        items = read_chunk(m["file"], "promises")
        if items is not None:
            split_promises.extend(items)
            check(len(items) == m.get("count"), f"promises chunk count mismatch in {m['key']}")
            check(all(p.get("due_date", "")[:7] == m["key"] for p in items),
                  f"promises chunk month mismatch in {m['key']}")
    check(Counter(json.dumps(p, sort_keys=True) for p in split_promises) ==
          Counter(json.dumps(p, sort_keys=True) for p in promises),
          "promises split contents differ from canonical promises")

print(f"events: {len(all_events)} entries across {len(events)} date keys")
print(f"promises: {len(promises)}")
for w in warnings:
    print(f"WARN: {w}")
if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)
print("OK")
