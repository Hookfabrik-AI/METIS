"""Smoke-test the P2 launcher without starting CPU-heavy training."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TrainingLayoutTests(unittest.TestCase):
    def test_shell_syntax(self):
        subprocess.run(["bash", "-n", str(ROOT / "scripts/train_p2.sh")], check=True)

    def test_project_root_is_parent_of_scripts(self):
        s = (ROOT / "scripts/train_p2.sh").read_text(encoding="utf-8")
        self.assertIn('$(dirname "${BASH_SOURCE[0]}")/.."', s)
        self.assertNotIn('$(dirname "${BASH_SOURCE[0]}")/../.."', s)
        self.assertTrue((ROOT / "research/p2/train.py").is_file())
        self.assertTrue((ROOT / "datasets/p2/train.jsonl").is_file())

    def test_launcher_invokes_all_stages_with_correct_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            output = folder / "calls.txt"
            stub = folder / "record-python"
            stub.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$METIS_TEST_LOG"\n', encoding="utf-8")
            stub.chmod(0o700)
            env = dict(os.environ, METIS_PYTHON=str(stub),
                       METIS_RUNS_DIR=str(folder / "runs"), METIS_TEST_LOG=str(output))
            subprocess.run(["bash", str(ROOT / "scripts/train_p2.sh")],
                           cwd=ROOT, env=env, check=True, capture_output=True, text=True)
            calls = output.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(calls), 7)
            self.assertTrue(all("train.py" in c for c in calls))
            self.assertTrue(all(str(ROOT / "datasets/p2") in c for c in calls))
            self.assertEqual(sum("/seed0/C " in c for c in calls), 1)
            self.assertIn("P2_TRAINING_CHAIN_DONE",
                          subprocess.run(["bash", str(ROOT / "scripts/train_p2.sh")],
                          cwd=ROOT, env=env, check=True, capture_output=True, text=True).stdout)

if __name__ == "__main__":
    unittest.main()
