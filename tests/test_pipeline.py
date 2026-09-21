import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "site" / "_data"


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        for name in ("split_data.py", "validate.py"):
            shutil.copyfile(SCRIPTS / name, self.base / name)
        self.events = {"01-01": [{
            "archive_id": "events-example",
            "date": "2020-01-01", "title": "Example event", "category": "industrial",
            "location": "Example location", "lives_lost": 2,
            "description": "Example evidence.", "sources": ["Source A", "Source B"],
            "source_urls": ["https://example.org/a", "https://example.org/b"],
        }]}
        self.promises = [{
            "archive_id": "promises-example",
            "person": "Example", "role": "Organization", "promise": "Example commitment",
            "date_promised": "2020-01-01", "due_date": "2020-12-31", "status": "kept",
            "description": "Example commitment.", "evidence": ["Example outcome evidence."],
            "sources": ["Source A"], "source_urls": ["https://example.org/pledge"],
        }]
        self.write_sources()
        self.write("retention.json", {"events": ["events-example"], "promises": ["promises-example"]})
        self.write("legacy-review.json", {"events": ["events-example"], "promises": ["promises-example"]})
        self.run_script("split_data.py")

    def write(self, name, value):
        (self.base / name).write_text(json.dumps(value))

    def read(self, name):
        return json.loads((self.base / name).read_text())

    def write_sources(self):
        self.write("events.json", self.events)
        self.write("promises.json", self.promises)
        self.write("checkpoint.json", {
            "events": {"last_date": "2020-01-01", "total": 1},
            "promises": {"last_date": "2020-01-01", "total": 1},
        })

    def run_script(self, script):
        return subprocess.run([sys.executable, str(self.base / script)],
                              text=True, capture_output=True, timeout=15)

    def invalid(self, message):
        result = self.run_script("validate.py")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(message, result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_clean_pipeline(self):
        result = self.run_script("validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stdout)

    def test_real_calendar_dates(self):
        self.promises[0]["due_date"] = "2020-02-30"
        self.write_sources()
        self.invalid("invalid calendar date")

    def test_reversed_promise_dates(self):
        self.promises[0]["date_promised"] = "2021-01-01"
        self.write_sources()
        self.invalid("due_date precedes date_promised")

    def test_future_announcement(self):
        tomorrow = datetime.datetime.now(datetime.timezone.utc).date() + datetime.timedelta(days=1)
        self.promises[0]["date_promised"] = tomorrow.isoformat()
        self.promises[0]["due_date"] = tomorrow.isoformat()
        self.write_sources()
        self.invalid("date_promised before 2000 or in the future")

    def test_boolean_is_not_a_death_toll(self):
        self.events["01-01"][0]["lives_lost"] = True
        self.write_sources()
        self.invalid("lives_lost must be a positive integer")

    def test_zero_toll_requires_a_documented_correction_and_original_value(self):
        event = self.events["01-01"][0]
        event["lives_lost"] = 0
        self.write_sources()
        self.run_script("split_data.py")
        self.invalid("documented zero-toll correction")
        event["correction"] = {
            "as_of": "2020-01-02", "note": "The source withdrew its fatality report.",
            "original_values": {"lives_lost": 2},
        }
        self.write_sources()
        self.run_script("split_data.py")
        result = self.run_script("validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        event["correction"]["original_values"] = {}
        self.write_sources()
        self.invalid("must preserve the original positive toll")

    def test_event_source_url_alignment(self):
        self.events["01-01"][0]["source_urls"] = ["https://example.org/a"]
        self.write_sources()
        self.invalid("source_urls must match sources length")

    def test_invalid_source_url(self):
        self.events["01-01"][0]["source_urls"][0] = "javascript:alert(1)"
        self.write_sources()
        self.invalid("invalid source URL")

    def test_missing_evidence_links(self):
        self.events["01-01"][0].pop("source_urls")
        self.write_sources()
        self.invalid("missing evidence links")

    def test_empty_promise_evidence(self):
        self.promises[0]["evidence"] = []
        self.write_sources()
        self.invalid("evidence must contain a nonempty explanation")

    def test_retained_citation_gap_requires_an_explicit_review_note(self):
        self.events["01-01"][0].pop("source_urls")
        self.events["01-01"][0]["review"] = {
            "as_of": "2020-01-02", "fields": ["sources"],
            "note": "Original citation links remain to be located.", "sources": [],
        }
        self.write_sources()
        self.run_script("split_data.py")
        result = self.run_script("validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_deletion_cannot_be_hidden_by_updating_totals(self):
        self.write("promises.json", [])
        checkpoint = self.read("checkpoint.json")
        checkpoint["promises"]["total"] = 0
        self.write("checkpoint.json", checkpoint)
        self.run_script("split_data.py")
        self.invalid("collected records removed from archive")

    def test_new_records_must_be_registered_and_cannot_then_be_dropped(self):
        self.promises.append(self.promises[0] | {
            "archive_id": "promises-new", "person": "Another organization",
            "promise": "A new commitment",
        })
        self.write_sources()
        checkpoint = self.read("checkpoint.json")
        checkpoint["promises"]["total"] = 2
        self.write("checkpoint.json", checkpoint)
        self.run_script("split_data.py")
        self.invalid("register new archive_ids in retention.json")
        retention = self.read("retention.json")
        retention["promises"].append("promises-new")
        self.write("retention.json", retention)
        result = self.run_script("validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.promises.pop()
        self.write_sources()
        self.run_script("split_data.py")
        self.invalid("collected records removed from archive")

    def test_retention_does_not_exempt_new_records_from_evidence_requirements(self):
        self.promises[0]["archive_id"] = "promises-new"
        self.promises[0].pop("source_urls")
        self.promises[0]["date_promised"] = None
        self.promises[0]["review"] = {
            "as_of": "2020-01-02", "fields": ["sources", "date_promised"],
            "note": "Evidence is still being researched.", "sources": [],
        }
        self.write_sources()
        self.write("retention.json", {"events": ["events-example"], "promises": ["promises-new"]})
        self.run_script("split_data.py")
        self.invalid("missing evidence links")
        self.invalid("missing field date_promised")

    def test_record_ids_remain_stable_across_factual_corrections(self):
        self.promises[0]["promise"] = "Corrected wording"
        self.write_sources()
        self.run_script("split_data.py")
        result = self.run_script("validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unknown_legacy_announcement_is_explicit_not_fabricated(self):
        self.promises[0]["date_promised"] = None
        self.promises[0]["review"] = {
            "as_of": "2020-01-02", "fields": ["date_promised"],
            "note": "The original date conflicts with the recorded deadline.", "sources": [],
            "original_values": {"date_promised": "2021-01-01"},
        }
        self.write_sources()
        self.run_script("split_data.py")
        result = self.run_script("validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stale_chunk_content(self):
        window = self.read("events/index.json")["windows"][0]["file"]
        chunk = self.read(window)
        chunk[0]["lives_lost"] = 99
        self.write(window, chunk)
        self.invalid("events split contents differ from canonical events")

    def test_missing_chunk(self):
        window = self.read("events/index.json")["windows"][0]["file"]
        (self.base / window).unlink()
        self.invalid("missing split file")

    def test_manifest_uses_its_build_date_not_validation_date(self):
        index = self.read("promises/index.json")
        index.update(as_of="2020-01-01", due_total=0, due_status={})
        self.write("promises/index.json", index)
        result = self.run_script("validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_wrong_status_counts(self):
        index = self.read("promises/index.json")
        index["due_status"] = {"broken": 1}
        self.write("promises/index.json", index)
        self.invalid("due_status mismatch")

    def test_obsolete_generated_chunks_are_removed(self):
        for name in ("events/w2020-2020.json", "events/2025-2029.json", "promises/2021-20.json"):
            self.write(name, [])
        self.write("events/notes.json", {"keep": True})
        result = self.run_script("split_data.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("events/w2020-2020.json", "events/2025-2029.json", "promises/2021-20.json"):
            self.assertFalse((self.base / name).exists())
        self.assertTrue((self.base / "events/notes.json").exists())


if __name__ == "__main__":
    unittest.main()
