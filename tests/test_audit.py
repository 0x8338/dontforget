import importlib.util
from pathlib import Path
import unittest


PATH = Path(__file__).resolve().parents[1] / "research/fact-checks/2026-09-21/integrate.py"
spec = importlib.util.spec_from_file_location("audit", PATH)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.record = {"date": "2020-01-01", "title": "Example", "sources": ["A", "B"],
                       "lives_lost": 2, "source_urls": ["https://example.org/a", "https://example.org/b"]}
        self.entry = {"key": {"date": "2020-01-01", "title": "Example"},
                      "publication_ready": True, "result": "correction",
                      "changes": {"lives_lost": 3}, "sources": [], "note": "Updated toll."}

    def test_supported_correction(self):
        public, withheld, stats = audit.reconcile("events", [self.record], [self.entry])
        self.assertEqual(public[0]["lives_lost"], 3)
        self.assertEqual(withheld, [])
        self.assertEqual(stats["published_changed"], 1)
        self.assertEqual(self.record["lives_lost"], 2)

    def test_missing_duplicate_or_extra_coverage_fails(self):
        for entries in ([], [self.entry, self.entry], [self.entry | {"key": {"date": "2020-01-02", "title": "Other"}}]):
            with self.subTest(entries=entries), self.assertRaisesRegex(ValueError, "coverage"):
                audit.reconcile("events", [self.record], entries)

    def test_decision_must_be_explicit(self):
        self.entry.pop("publication_ready")
        with self.assertRaisesRegex(ValueError, "missing publication decision"):
            audit.reconcile("events", [self.record], [self.entry])

    def test_unresolved_cannot_be_published(self):
        self.entry["result"] = "unresolved"
        with self.assertRaisesRegex(ValueError, "unresolved record"):
            audit.reconcile("events", [self.record], [self.entry])

    def test_withheld_original_and_proposal_are_preserved(self):
        self.entry.update(publication_ready=False, unresolved_fields=["date"])
        public, withheld, _ = audit.reconcile("events", [self.record], [self.entry])
        self.assertEqual(public, [])
        self.assertEqual(withheld[0]["original"], self.record)
        self.assertEqual(withheld[0]["proposed"]["lives_lost"], 3)
        self.assertEqual(withheld[0]["unresolved_fields"], ["date"])

    def test_links_required_for_published_records(self):
        self.entry["changes"]["source_urls"] = [None, None]
        with self.assertRaisesRegex(ValueError, "lacks evidence links"):
            audit.reconcile("events", [self.record], [self.entry])

    def test_verified_record_receives_ledger_links(self):
        self.entry.update(result="verified", changes={}, sources=[
            {"name": "C", "url": "https://example.org/c"},
            {"name": "D", "url": "https://example.org/d"},
        ])
        public, _, stats = audit.reconcile("events", [self.record], [self.entry])
        self.assertEqual(public[0]["sources"], ["C", "D"])
        self.assertEqual(public[0]["source_urls"], ["https://example.org/c", "https://example.org/d"])
        self.assertNotIn("published_fact_corrections", stats)
