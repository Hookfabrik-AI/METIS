"""Repository release safety regressions; not a substitute for a security audit."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / "README.md", ROOT / "CHANGELOG.md", ROOT / "CONTRIBUTING.md",
        ROOT / "SECURITY.md", ROOT / "REPRODUCIBILITY.md",
        *(ROOT / "docs").glob("*.md"), *(ROOT / "research/p2").glob("*.py")]

class PublicationLayoutTests(unittest.TestCase):
    def test_license_and_scope_are_explicit(self):
        self.assertTrue((ROOT / "LICENSE").is_file())
        self.assertIn("Apache License", (ROOT / "LICENSE").read_text(encoding="utf-8"))
        scope = (ROOT / "LICENSE_SCOPE.md").read_text(encoding="utf-8")
        self.assertIn("model weights", scope.lower())
        self.assertIn("separate", scope.lower())

    def test_no_unrelated_project_identifiers_in_published_docs_or_p2_code(self):
        identifiers = ("NOU" + "MORA", "MOI" + "RAI", "AR" + "KEIN")
        for path in DOCS:
            s = path.read_text(encoding="utf-8")
            with self.subTest(file=str(path.relative_to(ROOT))):
                for word in identifiers:
                    self.assertNotIn(word, s)
                self.assertNotRegex(s, r"/home/[A-Za-z0-9_-]+/")

    def test_no_internal_reader_directory_or_parallel_english_readme(self):
        self.assertFalse((ROOT / "reader").exists())
        self.assertFalse((ROOT / "README.en.md").exists())
        self.assertIn('lang="en"', (ROOT / "docs/index.html").read_text(encoding="utf-8"))

    def test_relative_markdown_links_exist(self):
        for doc in DOCS + [ROOT / "P3_INGESTION.md", ROOT / "LICENSE_SCOPE.md"]:
            for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
                target = link.split("#")[0]
                if not target or target.startswith(("http:", "https:", "#", "mailto:")):
                    continue
                with self.subTest(document=str(doc.relative_to(ROOT)), target=target):
                    self.assertTrue((doc.parent / target).exists())

if __name__ == "__main__":
    unittest.main()
