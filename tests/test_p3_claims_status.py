import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class P3ReportStatusTest(unittest.TestCase):
    def test_report_not_confused_with_verified_evidence(self):
        data=json.loads((ROOT/'reports/p3/reported-progress-2026-10-18.json').read_text(encoding='utf-8'))
        self.assertEqual(data['status'],'USER_REPORTED_NOT_INDEPENDENTLY_VERIFIED')
        self.assertEqual(data['validation']['independent_review'],'pending')
        self.assertNotIn('publication_approved',data['validation'])
        self.assertFalse(data['limitations']['p3_raw_artifacts_in_repo'])
        self.assertFalse((ROOT/'models/p3').exists())
        self.assertFalse((ROOT/'evidence/p3').exists())
        index=json.loads((ROOT/'evidence/index.json').read_text(encoding='utf-8'))
        self.assertNotIn('publication',index)
        self.assertEqual(index['research_scope']['p3'],'project_report_only_not_independently_reproduced')
        self.assertEqual(index['qwen_four_arm']['arms']['B'],'MÉTIS P2 greedy candidate')

if __name__=='__main__': unittest.main()
