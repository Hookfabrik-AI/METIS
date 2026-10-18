import importlib.util
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(filename):
    spec=importlib.util.spec_from_file_location(filename.stem,filename)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class IntegrityTest(unittest.TestCase):
    def test_artifact_hashes_and_manifest(self):
        self.assertTrue(load(ROOT/'scripts/verify_evidence.py').verify())
    def test_four_arm_reaggregation(self):
        self.assertTrue(load(ROOT/'scripts/summarize_qwen.py').summarize())
    def test_no_private_keys_copied(self):
        self.assertFalse(list(ROOT.rglob('id_ed25519')))
        self.assertFalse(list(ROOT.rglob('id_ed25519.pub')))
    def test_evidence_tracks_research_not_github_visibility(self):
        import json
        d=json.loads((ROOT/'evidence/index.json').read_text())
        self.assertEqual(d['status'],'ARCHIVED_RESEARCH_SNAPSHOT')
        self.assertNotIn('publication',d)
        self.assertEqual(d['research_scope']['p3'],'project_report_only_not_independently_reproduced')

if __name__=='__main__':unittest.main()
