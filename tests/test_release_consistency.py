"""Portable shell launcher and research release regression checks."""
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ReleaseConsistencyTests(unittest.TestCase):
    def test_training_script_syntax(self):
        subprocess.run(["bash", "-n", str(ROOT / "scripts/train_p2.sh")], check=True)

    def test_training_root_is_repository(self):
        text = (ROOT / "scripts/train_p2.sh").read_text(encoding="utf-8")
        expected = 'ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"'
        self.assertIn(expected, text)
        self.assertNotIn('/../.."', text)

    def test_license_and_scope_present(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Apache License", license_text)
        self.assertIn("Version 2.0", license_text)
        self.assertTrue((ROOT / "LICENSING.md").is_file())

    def test_no_internal_toolkit(self):
        self.assertFalse((ROOT / "reader").exists())
        for p in ("README.md", "SECURITY.md", "CHANGELOG.md"):
            self.assertNotIn("reader/build_reader.py", (ROOT / p).read_text(encoding="utf-8"))

    def test_no_private_project_paths_in_text(self):
        for folder in ("docs", "research", "evidence"):
            for p in (ROOT / folder).rglob("*"):
                if not p.is_file() or p.suffix not in {".py", ".json", ".md", ".txt"}:
                    continue
                s = p.read_text(encoding="utf-8")
                self.assertNotRegex(s, r"\b[A-Z][A-Z0-9]+_(?:THINKING|COGNITION)_|\b[A-Z][A-Z0-9]+-INSTANCE")
                self.assertNotRegex(s, r"(?m)^-----BEGIN (?:OPENSSH|RSA|EC) PRIVATE KEY-----")

if __name__ == "__main__":
    unittest.main()
