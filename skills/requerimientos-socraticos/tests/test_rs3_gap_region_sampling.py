"""Bounded, deterministic exploration of a small formal guard-gap region."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_logic.py'


def run_model(sample_limit):
    model = {'inputs': ['A', 'B'], 'outputs': ['P'],
             'domain': {'op': 'or', 'args': [{'var': 'A'}, {'var': 'B'}]},
             'rules': [{'id': 'inactive', 'guard': False, 'response': {'var': 'P'}}],
             'properties': []}
    with tempfile.TemporaryDirectory(prefix='gap-region-') as root:
        source = Path(root) / 'model.json'
        source.write_text(json.dumps(model), encoding='utf-8')
        result = subprocess.run([sys.executable, str(SCRIPT), str(source),
                                 '--gap-samples', str(sample_limit)],
                                capture_output=True, text=True, timeout=15)
    return result.returncode, json.loads(result.stdout)


class GapRegionSamplingTests(unittest.TestCase):
    def test_partial_region_is_ordered_and_not_claimed_complete(self):
        code, result = run_model(2)
        self.assertEqual(code, 0)
        region = result['gap_region']
        self.assertEqual(region['status'], 'PARTIAL_LIMIT')
        self.assertEqual([row['input_assignment'] for row in region['samples']],
                         [{'A': False, 'B': True}, {'A': True, 'B': False}])
        self.assertEqual(region['sample_limit'], 2)
        self.assertEqual(region['remaining'], 'EXISTS_IN_SUPPLIED_MODEL')
        self.assertEqual(result['queries']['no_output']['status'], 'UNSAT')
        for row in region['samples']:
            self.assertEqual(row['semantic_status'], 'UNINTERPRETED')
            self.assertEqual(row['authority'], 'PROPOSAL_ONLY')

    def test_exhaustion_is_only_within_supplied_model(self):
        code, result = run_model(4)
        self.assertEqual(code, 0)
        region = result['gap_region']
        self.assertEqual(region['status'], 'EXACT_WITHIN_SUPPLIED_MODEL')
        self.assertEqual(len(region['samples']), 3)
        self.assertEqual(region['remaining'], 'NONE_IN_SUPPLIED_MODEL')

    def test_zero_and_invalid_limits(self):
        code, result = run_model(0)
        self.assertEqual(code, 0)
        self.assertEqual(result['gap_region']['status'], 'NOT_RUN')
        for limit in (-1, 17):
            with self.subTest(limit=limit):
                code, result = run_model(limit)
                self.assertEqual(code, 2)
                self.assertEqual(result['error']['code'], 'INVALID_INPUT')

    def test_deadline_exhaustion_is_inconclusive(self):
        sys.path.insert(0, str(SCRIPT.parent))
        import z3
        from formal_queries import QueryContext
        from gap_region import sample_gap_region
        model = {'inputs': ['A'], 'outputs': [], 'domain': True,
                 'rules': [], 'properties': []}
        region = sample_gap_region(model, QueryContext(model, z3), z3, -1.0, 2)
        self.assertEqual(region['status'], 'INCONCLUSIVE')
        self.assertEqual(region['samples'], [])


if __name__ == '__main__':
    unittest.main()
