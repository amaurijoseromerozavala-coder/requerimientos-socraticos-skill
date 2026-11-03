"""Fail closed on missing IDs or false completion in the proposed RS3 inventory."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / 'docs/design/rs3/reconciliation-2026-11-03.json'


class RS3ReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(MATRIX.read_text(encoding='utf-8'))

    def test_fixed_denominators_and_unique_ids(self):
        doc = self.doc
        self.assertEqual(doc['source']['zip_sha256'],
                         '83a83c77921f7737e89328b8dae365e7d0e7047f0c3fc7acbf7af2fd8f6c2d7e')
        for key, prefix, total in (('requirements', 'RS3-REQ-', 107),
                                    ('tasks', 'T', 50), ('cases', 'RS3-AT-', 52)):
            ids = [row['id'] for row in doc[key]]
            width = 3
            self.assertEqual(ids, [f'{prefix}{number:0{width}d}'
                                   for number in range(1, total + 1)])
            self.assertEqual(len(ids), len(set(ids)))

    def test_proposals_are_not_promoted_by_code_presence(self):
        for row in self.doc['requirements']:
            self.assertEqual(row['package_status'], 'PROPOSED')
            self.assertEqual(row['acceptance_status'], 'NOT_VERIFIED_PER_REQUIREMENT')
            self.assertIn(row['implementation_status'],
                          ('CODE_OBSERVED_PARTIAL', 'DOCUMENTED_ONLY', 'NOT_ASSESSED'))
            self.assertEqual(row['package_mapping'], 'GROUP_ONLY_PROPOSED_NOT_FINE_GRAINED')
            for path in row['code_paths'] + row['test_paths']:
                self.assertTrue((ROOT / path).is_file(), (row['id'], path))
        for row in self.doc['cases']:
            self.assertEqual(row['execution'], 'NOT_RUN_AS_PACKAGE_CASE')

    def test_authority_and_formal_boundaries(self):
        self.assertEqual(self.doc['decisions']['production_ready'],
                         'DOCUMENTARY_REVIEW_ELIGIBILITY')
        self.assertEqual(self.doc['decisions']['d05_gate'], 'SECURITY_BOUNDARY_UNMET')
        self.assertEqual(self.doc['formal']['no_output'], 'SAT(D ∧ ¬∃O:C)')
        self.assertEqual(self.doc['plan_status'], 'TOPOLOGY_ONLY')

    def test_task_dependencies_are_closed_and_acyclic(self):
        rows = {row['id']: row for row in self.doc['tasks']}
        seen = set()
        for row in self.doc['tasks']:
            self.assertIn(row['state'], ('READ_ONLY_COMPLETED', 'OBSERVED_PARTIAL',
                                          'PENDING', 'BLOCKED'))
            for predecessor in row['depends_on']:
                self.assertIn(predecessor, seen, (row['id'], predecessor))
            seen.add(row['id'])


if __name__ == '__main__':
    unittest.main()
