"""Validate reproducibility entry points without launching CPU-intensive training."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TrainingLayoutTests(unittest.TestCase):
    def test_shell_syntax(self):
        subprocess.run(["bash", "-n", str(ROOT / "scripts/train_p2.sh")], check=True)
    def test_project_root_is_parent_of_scripts(self):
        text = (ROOT / "scripts/train_p2.sh").read_text(encoding="utf-8")
        self.assertIn('$(dirname "${BASH_SOURCE[0]}")/.."', text)
        self.assertNotIn('$(dirname "${BASH_SOURCE[0]}")/../.."', text)
        self.assertTrue((ROOT / "research/p2/train.py").is_file())
        self.assertTrue((ROOT / "datasets/p2/train.jsonl").is_file())

if __name__ == "__main__":
    unittest.main()
