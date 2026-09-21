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
            "date": "2020-01-01", "title": "Example event", "category": "industrial",
            "location": "Example location", "lives_lost": 2,
            "description": "Example evidence.", "sources": ["Source A", "Source B"],
            "source_urls": ["https://example.org/a", "https://example.org/b"],
        }]}
        self.promises = [{
            "person": "Example", "role": "Organization", "promise": "Example commitment",
            "date_promised": "2020-01-01", "due_date": "2020-12-31", "status": "kept",
            "description": "Example commitment.", "evidence": ["Example outcome evidence."],
            "sources": ["Source A"], "source_urls": ["https://example.org/pledge"],
        }]
        self.write_sources()
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
