"""Offline checks for the published, standalone MÉTIS research book."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "docs" / "index.html"

class ResearchBookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")

    def test_standalone_book_exists(self):
        self.assertIn("<!doctype html>", self.html.lower())
        self.assertIn("const BOOK =", self.html)
        self.assertIn('<html lang="en">', self.html)
        self.assertIn('"id":"preface"', self.html)
        self.assertIn('"id":"reproducibility"', self.html)
        self.assertNotIn("Bookmarks gespeichert", self.html)
        self.assertNotIn("NOUMORA", self.html)
        self.assertIn("P2 archived", self.html)
        self.assertIn("MÉTIS", self.html)
        self.assertNotIn("%%BOOK_JSON%%", self.html)

    def test_reading_controls_present(self):
        for control in ("font-increase", "focus-action", "theme-action", "bookmark"):
            with self.subTest(control=control):
                self.assertIn(control, self.html)

    def test_offline_references(self):
        for external in ("https://cdn.", "https://fonts.googleapis.com", "<script src="):
            self.assertNotIn(external, self.html)

    def test_repository_documents_avoid_internal_dependencies(self):
        for name in ("README.md", "SECURITY.md", "CHANGELOG.md"):
            with self.subTest(name=name):
                doc = (ROOT / name).read_text(encoding="utf-8")
                self.assertNotIn("reader/", doc)
                self.assertNotIn("build_reader.py", doc)

if __name__ == "__main__":
    unittest.main()
