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

    def test_addition_keeps_its_assigned_id_when_corrected(self):
        original_id = audit.archive_id("events", self.record)
        corrected = self.record | {"archive_id": original_id, "title": "Corrected title",
                                   "date": "2020-01-02"}
        self.assertEqual(audit.archive_id("events", corrected), original_id)

    def test_retracted_fatality_is_corrected_without_dropping_the_record(self):
        self.entry["changes"] = {"lives_lost": 0, "title": "Fatality report corrected"}
        self.entry["note"] = "The source corrected its fatality report to an injury."
        public, _, _ = audit.reconcile("events", [self.record], [self.entry])
        self.assertEqual(len(public), 1)
        self.assertEqual(public[0]["lives_lost"], 0)
        self.assertEqual(public[0]["correction"]["original_values"]["lives_lost"], 2)

    def test_missing_duplicate_or_extra_coverage_fails(self):
        for entries in ([], [self.entry, self.entry], [self.entry | {"key": {"date": "2020-01-02", "title": "Other"}}]):
            with self.subTest(entries=entries), self.assertRaisesRegex(ValueError, "coverage"):
                audit.reconcile("events", [self.record], entries)

    def test_decision_must_be_explicit(self):
        self.entry.pop("publication_ready")
        with self.assertRaisesRegex(ValueError, "missing publication decision"):
            audit.reconcile("events", [self.record], [self.entry])

    def test_unresolved_cannot_be_marked_fully_checked(self):
        self.entry["result"] = "unresolved"
        with self.assertRaisesRegex(ValueError, "unresolved record"):
            audit.reconcile("events", [self.record], [self.entry])

    def test_research_gap_does_not_remove_record_or_discard_supported_correction(self):
        self.entry.update(publication_ready=False, unresolved_fields=["date"])
        public, backlog, _ = audit.reconcile("events", [self.record], [self.entry])
        self.assertEqual(len(public), 1)
        self.assertEqual(public[0]["lives_lost"], 3)
        self.assertEqual(public[0]["date"], self.record["date"])
        self.assertEqual(public[0]["review"]["fields"], ["date"])
        self.assertEqual(backlog[0]["original"], self.record)

    def test_unresolved_field_is_retained_not_replaced_with_a_guess(self):
        self.entry.update(publication_ready=False, unresolved_fields=["lives_lost"])
        public, _, _ = audit.reconcile("events", [self.record], [self.entry])
        self.assertEqual(public[0]["lives_lost"], 2)
        self.assertIn("lives_lost", public[0]["review"]["fields"])

    def test_unresolved_toll_does_not_block_a_supported_description_correction(self):
        self.record["description"] = "Incorrect attribution"
        self.entry.update(publication_ready=False, result="unresolved",
                          unresolved_fields=["lives_lost"],
                          changes={"description": "The source leaves responsibility unestablished."})
        public, _, _ = audit.reconcile("events", [self.record], [self.entry])
        self.assertEqual(public[0]["lives_lost"], 2)
        self.assertEqual(public[0]["description"], self.entry["changes"]["description"])

    def test_fully_unresolved_record_remains_in_archive(self):
        self.entry.update(publication_ready=False, result="unresolved",
                          unresolved_fields=["date", "lives_lost"])
        public, _, _ = audit.reconcile("events", [self.record], [self.entry])
        self.assertEqual(len(public), 1)
        self.assertEqual(public[0]["lives_lost"], self.record["lives_lost"])
        self.assertEqual(public[0]["archive_id"], audit.archive_id("events", self.record))

    def test_original_citations_are_not_replaced_by_partial_review_sources(self):
        self.entry.update(publication_ready=False, unresolved_fields=["date"],
                          sources=[{"name": "C", "url": "https://example.org/c"}])
        public, _, _ = audit.reconcile("events", [self.record], [self.entry])
        self.assertEqual(public[0]["sources"], self.record["sources"])
        self.assertEqual(public[0]["review"]["sources"], self.entry["sources"])

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
        self.assertNotIn("published_content_changes", stats)
