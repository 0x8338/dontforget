#!/usr/bin/env python3
"""Merge agent-produced event JSON into events.json with dedup and validation."""
import json, sys, os
from datetime import datetime

EVENTS_FILE = os.path.join(os.path.dirname(__file__), 'events.json')
CHECKPOINT_FILE = os.path.join(os.path.dirname(__file__), 'checkpoint.json')

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved {path}")

def validate(event):
    errors = []
    try:
        datetime.strptime(event['date'], '%Y-%m-%d')
    except:
        errors.append(f"bad date: {event.get('date')}")
    if int(event['date'][:4]) < 2000:
        errors.append(f"pre-2000: {event['date']}")
    valid_cats = {'natural-disaster','war','gun-violence','terrorism','food-crisis','industrial'}
    if event.get('category') not in valid_cats:
        errors.append(f"bad category: {event.get('category')}")
    if len(event.get('sources', [])) < 2:
        errors.append(f"<2 sources: {event.get('sources')}")
    if not event.get('title'):
        errors.append("missing title")
    if not event.get('lives_lost') or event['lives_lost'] < 0:
        errors.append(f"bad lives_lost: {event.get('lives_lost')}")
    return errors

def get_mmdd(date_str):
    return date_str[5:10]  # MM-DD

def merge(new_events, year):
    """Merge new events into events.json, dedup by date+title, validate all."""
    data = load_json(EVENTS_FILE)

    accepted, rejected, dupes = 0, 0, 0
    existing_keys = set()
    for mmdd, events in data.items():
        for e in events:
            existing_keys.add((e['date'], e['title'].lower().strip()))

    for e in new_events:
        # Validate
        errs = validate(e)
        if errs:
            print(f"  REJECT {e.get('date','?')} — {e.get('title','?')[:60]}: {'; '.join(errs)}")
            rejected += 1
            continue

        # Dedup
        key = (e['date'], e['title'].lower().strip())
        if key in existing_keys:
            dupes += 1
            continue

        # Insert
        mmdd = get_mmdd(e['date'])
        if mmdd not in data:
            data[mmdd] = []
        data[mmdd].append(e)
        existing_keys.add(key)
        accepted += 1

    # Sort events within each date
    for mmdd in data:
        data[mmdd].sort(key=lambda e: e['date'], reverse=True)

    save_json(EVENTS_FILE, data)

    # Update checkpoint
    ck = load_json(CHECKPOINT_FILE)
    if str(year) not in ck['memory']['completed']:
        ck['memory']['completed'].append(str(year))
    ck['memory']['events_written'] = sum(len(v) for v in data.values())
    ck['memory']['last_updated'] = datetime.utcnow().isoformat()
    ck['memory']['in_progress'] = None
    save_json(CHECKPOINT_FILE, ck)

    return accepted, rejected, dupes

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 merge_events.py <year> < events.json")
        print("  Reads new events from stdin as JSON array")
        sys.exit(1)

    year = int(sys.argv[1])
    raw = sys.stdin.read().strip()

    # Extract JSON array from possibly messy output
    start = raw.find('[')
    end = raw.rfind(']')
    if start == -1 or end == -1:
        print("ERROR: No JSON array found in input")
        sys.exit(1)

    try:
        new_events = json.loads(raw[start:end+1])
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        sys.exit(1)

    print(f"Merging {len(new_events)} events for year {year}...")
    a, r, d = merge(new_events, year)

    # Summary
    data = load_json(EVENTS_FILE)
    total = sum(len(v) for v in data.values())
    dates = len([k for k,v in data.items() if v])
    lives = sum(e.get('lives_lost', 0) or 0 for v in data.values() for e in v)

    print(f"Accepted: {a}  Rejected: {r}  Duplicates: {d}")
    print(f"Dataset: {total} events across {dates} dates, ~{lives:,} lives")
