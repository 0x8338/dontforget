#!/usr/bin/env python3
"""Integrate this audit, preserving withheld originals. Dry-run by default."""

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


def reconcile(dataset, originals, entries):
    by_key = {identity(dataset, record): record for record in originals}
    if len(by_key) != len(originals):
        raise ValueError(f"{dataset}: duplicate original identities")
    observed = Counter(identity(dataset, row["key"]) for row in entries)
    if set(observed) != set(by_key) or any(count != 1 for count in observed.values()):
        raise ValueError(f"{dataset}: audit coverage must match every original exactly once "
                         f"({len(observed)} of {len(originals)} identities present)")
    published, withheld = [], []
    stats = Counter()
    for entry in entries:
        original = by_key[identity(dataset, entry["key"])]
        ready = entry.get("publication_ready")
        if type(ready) is not bool:
            raise ValueError(f"{dataset}: missing publication decision for {entry['key']}")
        result = entry["result"]
        if result not in {"verified", "correction", "unresolved"}:
            raise ValueError(f"{dataset}: invalid audit result {result}")
        if ready and result == "unresolved":
            raise ValueError(f"{dataset}: unresolved record marked publication-ready")
        changes = entry["changes"]
        if set(changes) - FIELDS[dataset]:
            raise ValueError(f"{dataset}: unknown correction fields {set(changes) - FIELDS[dataset]}")
        corrected = original | changes
        if not ({"sources", "source_urls"} & changes.keys()) and entry["sources"]:
            corrected["sources"] = [source["name"] for source in entry["sources"]]
            corrected["source_urls"] = [source["url"] for source in entry["sources"]]
        stats[result] += 1
        if ready:
            urls = corrected.get("source_urls", [])
            minimum = 2 if dataset == "events" else 1
            if len(urls) != len(corrected["sources"]) or len(urls) < minimum or not all(urls):
                raise ValueError(f"{dataset}: publication-ready record lacks evidence links: {entry['key']}")
            published.append(corrected)
            stats["published_changed" if corrected != original else "published_unchanged"] += 1
            if any(corrected.get(field) != original.get(field)
                   for field in FIELDS[dataset] - {"sources", "source_urls"}):
                stats["published_fact_corrections"] += 1
        else:
            withheld.append({"original": original, "proposed": corrected,
                             "note": entry["note"], "sources": entry["sources"],
                             "unresolved_fields": entry.get("unresolved_fields", [])})
    return published, withheld, dict(stats)


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
    quarantine = {"as_of": update["as_of"],
                  "policy": "Withheld from public datasets because material claims remain unresolved. "
                            "Originals and proposals below are not verified facts; withholding does not establish falsity."}
    for dataset in originals:
        entries = []
        for path in sorted(HERE.glob(f"{dataset}-*.json")):
            ledger = json.loads(path.read_text())
            if (ledger["dataset"] not in {dataset, FILES[dataset]} or
                    ledger["as_of"] != update["as_of"]):
                raise ValueError(f"Unexpected ledger metadata in {path.name}")
            entries.extend(ledger["records"])
        records, withheld, stats = reconcile(dataset, originals[dataset], entries)
        additions = ([item["record"] for item in update[dataset]] if dataset == "events"
                     else update[dataset])
        records.extend(additions)
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
        quarantine[dataset] = withheld
        counts[dataset] = {"original": len(originals[dataset]), "audited": len(entries),
                           "audit_results": stats, "withheld": len(withheld),
                           "added": len(additions), "published": len(records)}
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    checkpoint = baseline["checkpoint"]
    for dataset in originals:
        checkpoint[dataset].update(last_date=update["window"]["through"], total=counts[dataset]["published"])
    checkpoint["last_updated"] = now
    checkpoint["promises_expansion"]["last_focus"] = update["focus"]
    checkpoint["fact_check"] = {"as_of": update["as_of"], "report": "research/fact-checks/2026-09-21/README.md",
                                "withheld_events": len(quarantine["events"]),
                                "withheld_promises": len(quarantine["promises"])}
    output["checkpoint"] = checkpoint
    encoded = {name: (json.dumps(value, ensure_ascii=False, indent=1) + "\n").encode()
               for name, value in output.items()}
    summary = {"baseline_commit": BASELINE, "integrated_at": now, "counts": counts,
               "output_sha256": {name: digest(data) for name, data in encoded.items()}}
    if args.apply:
        for name, data in encoded.items():
            (ROOT / FILES[name]).write_bytes(data)
        (HERE / "quarantine.json").write_text(json.dumps(quarantine, ensure_ascii=False, indent=2) + "\n")
        (HERE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
