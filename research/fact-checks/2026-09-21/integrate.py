#!/usr/bin/env python3
"""Integrate evidence-backed corrections without dropping collected records."""

import argparse
from collections import Counter, defaultdict
import datetime
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE = "15704590b8c3bf33eabd6bed57a47ef01d54b20f"
FILES = {name: f"site/_data/{name}.json" for name in ("events", "promises", "checkpoint")}
FIELDS = {
    "events": {"date", "title", "category", "location", "lives_lost", "description", "sources", "source_urls"},
    "promises": {"person", "role", "promise", "date_promised", "due_date", "status", "description", "evidence", "sources", "source_urls"},
}


def identity(dataset, record):
    keys = ("date", "title") if dataset == "events" else ("person", "promise", "date_promised")
    return tuple(record[k] for k in keys)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def archive_id(dataset, record):
    if record.get("archive_id"):
        return record["archive_id"]
    key = json.dumps(identity(dataset, record), ensure_ascii=False).encode()
    return f"{dataset}-{digest(key)[:20]}"


def reconcile(dataset, originals, entries):
    by_key = {identity(dataset, record): record for record in originals}
    if len(by_key) != len(originals):
        raise ValueError(f"{dataset}: duplicate original identities")
    observed = Counter(identity(dataset, row["key"]) for row in entries)
    if set(observed) != set(by_key) or any(count != 1 for count in observed.values()):
        raise ValueError(f"{dataset}: audit coverage must match every original exactly once "
                         f"({len(observed)} of {len(originals)} identities present)")
    published, review_backlog = [], []
    stats = Counter()
    for entry in entries:
        original = by_key[identity(dataset, entry["key"])]
        ready = entry.get("publication_ready")
        if type(ready) is not bool:
            raise ValueError(f"{dataset}: missing publication decision for {entry['key']}")
        result = entry["result"]
        if result not in {"verified", "correction", "unresolved"}:
            raise ValueError(f"{dataset}: invalid audit result {result}")
        if ready and (result == "unresolved" or entry.get("unresolved_fields")):
            raise ValueError(f"{dataset}: unresolved record marked fully checked")
        changes = entry["changes"]
        if set(changes) - FIELDS[dataset]:
            raise ValueError(f"{dataset}: unknown correction fields {set(changes) - FIELDS[dataset]}")
        # An incomplete check does not invalidate the collection. Only apply
        # supported fields; retain the rest with the precise research gap.
        if not ready:
            blocked = set(entry["unresolved_fields"])
            if "identity" in blocked:
                blocked.update(changes)
            changes = {field: value for field, value in changes.items()
                       if field not in blocked | {"sources", "source_urls"}}
        corrected = original | changes
        corrected["archive_id"] = archive_id(dataset, original)
        if dataset == "events" and ready and changes.get("lives_lost") == 0:
            corrected["correction"] = {
                "as_of": "2026-09-21", "note": entry["note"],
                "original_values": {field: original[field] for field in changes},
            }
        if ready and not ({"sources", "source_urls"} & changes.keys()) and entry["sources"]:
            corrected["sources"] = [source["name"] for source in entry["sources"]]
            corrected["source_urls"] = [source["url"] for source in entry["sources"]]
        stats[result] += 1
        if ready:
            urls = corrected.get("source_urls", [])
            minimum = 2 if dataset == "events" else 1
            if len(urls) != len(corrected["sources"]) or len(urls) < minimum or not all(urls):
                raise ValueError(f"{dataset}: publication-ready record lacks evidence links: {entry['key']}")
        else:
            fields = list(entry["unresolved_fields"])
            urls = corrected.get("source_urls", [])
            if len(urls) != len(corrected["sources"]) or not all(urls):
                if "sources" not in fields:
                    fields.append("sources")
            corrected["review"] = {
                "as_of": "2026-09-21", "fields": fields,
                "note": entry["note"], "sources": entry["sources"],
            }
            if dataset == "promises":
                if not corrected.get("evidence"):
                    corrected["evidence"] = [
                        "Retained from the existing collection; outcome evidence remains to be documented."
                    ]
                    if "evidence" not in fields:
                        fields.append("evidence")
                if corrected["date_promised"] > corrected["due_date"]:
                    if "date_promised" not in fields:
                        raise ValueError("Reversed promise dates without an explicit research gap")
                    corrected["review"]["original_values"] = {"date_promised": corrected["date_promised"]}
                    corrected["date_promised"] = None
            review_backlog.append({"original": original, "retained": corrected,
                                   "applied_fields": sorted(changes)})
        published.append(corrected)
        stats["published_changed" if corrected != original else "published_unchanged"] += 1
        if any(corrected.get(field) != original.get(field)
               for field in FIELDS[dataset] - {"sources", "source_urls"}):
            stats["published_content_changes"] += 1
    return published, review_backlog, dict(stats)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write datasets and audit outputs")
    args = parser.parse_args()
    baseline_bytes = {name: subprocess.check_output(
        ["git", "show", f"{BASELINE}:{path}"], cwd=ROOT) for name, path in FILES.items()}
    baseline = {name: json.loads(data) for name, data in baseline_bytes.items()}
    previous = HERE / "summary.json"
    previous_hashes = json.loads(previous.read_text()).get("output_sha256", {}) if previous.exists() else {}
    for name, path in FILES.items():
        current_hash = digest((ROOT / path).read_bytes())
        if current_hash not in {digest(baseline_bytes[name]), previous_hashes.get(name)}:
            raise ValueError(f"Refusing to overwrite changes outside this integration: {path}")
    originals = {"events": [r for rows in baseline["events"].values() for r in rows],
                 "promises": baseline["promises"]}
    update = json.loads((HERE / "update.json").read_text())
    output, counts = {}, {}
    backlog = {"as_of": update["as_of"],
               "policy": "All collected records are retained. Unresolved details are research gaps, "
                         "not grounds for exclusion or a declaration that the record is false."}
    retention_path = ROOT / "site/_data/retention.json"
    retention = json.loads(retention_path.read_text()) if retention_path.exists() else {}
    for dataset in originals:
        entries = []
        for path in sorted(HERE.glob(f"{dataset}-*.json")):
            ledger = json.loads(path.read_text())
            if (ledger["dataset"] not in {dataset, FILES[dataset]} or
                    ledger["as_of"] != update["as_of"]):
                raise ValueError(f"Unexpected ledger metadata in {path.name}")
            entries.extend(ledger["records"])
        records, needs_review, stats = reconcile(dataset, originals[dataset], entries)
        additions = ([item["record"] for item in update[dataset]] if dataset == "events"
                     else update[dataset])
        records.extend(record | {"archive_id": archive_id(dataset, record)} for record in additions)
        ids = {record["archive_id"] for record in records}
        if not set(retention.get(dataset, [])).issubset(ids):
            raise ValueError(f"{dataset}: refusing to remove protected collected records")
        retention[dataset] = sorted(ids)
        identities = [identity(dataset, row) for row in records]
        if len(identities) != len(set(identities)):
            raise ValueError(f"{dataset}: duplicate corrected or new identities")
        if dataset == "events":
            buckets = defaultdict(list)
            for record in sorted(records, key=lambda r: (r["date"], r["title"])):
                buckets[record["date"][5:]].append(record)
            output[dataset] = dict(sorted(buckets.items()))
        else:
            output[dataset] = records
        backlog[dataset] = needs_review
        counts[dataset] = {"original": len(originals[dataset]), "audited": len(entries),
                           "audit_results": stats, "withheld": 0, "needs_review": len(needs_review),
                           "added": len(additions), "published": len(records)}
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    checkpoint = baseline["checkpoint"]
    for dataset in originals:
        checkpoint[dataset].update(last_date=update["window"]["through"], total=counts[dataset]["published"])
    checkpoint["last_updated"] = now
    checkpoint["promises_expansion"]["last_focus"] = update["focus"]
    checkpoint["fact_check"] = {"as_of": update["as_of"], "report": "research/fact-checks/2026-09-21/README.md",
                                "withheld_events": 0, "withheld_promises": 0,
                                "events_needing_review": len(backlog["events"]),
                                "promises_needing_review": len(backlog["promises"])}
    output["checkpoint"] = checkpoint
    encoded = {name: (json.dumps(value, ensure_ascii=False, indent=1) + "\n").encode()
               for name, value in output.items()}
    summary = {"baseline_commit": BASELINE, "integrated_at": now, "counts": counts,
               "output_sha256": {name: digest(data) for name, data in encoded.items()}}
    if args.apply:
        for name, data in encoded.items():
            (ROOT / FILES[name]).write_bytes(data)
        retention_path.write_text(json.dumps(retention, indent=2) + "\n")
        (HERE / "review-backlog.json").write_text(json.dumps(backlog, ensure_ascii=False, indent=2) + "\n")
        (HERE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
