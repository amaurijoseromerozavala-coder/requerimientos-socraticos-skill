"""RS3 witness claims are checked against the frozen Boolean query formula."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import z3

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from formal_queries import QueryContext, QueryKind
from witness_validation import verify_assignment


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_logic.py'


def example():
    return {'inputs': ['A', 'B'], 'outputs': ['P'], 'domain': True,
            'rules': [{'id': 'r', 'guard': True,
                       'response': {'op': 'implies',
                                    'args': [{'var': 'A'}, {'var': 'B'}]}}],
            'properties': []}


class WitnessRecheckTests(unittest.TestCase):
    def test_valid_and_altered_witness(self):
        context = QueryContext(example(), z3)
        query = context.formula(QueryKind.NO_OUTPUT)
        deadline = time.monotonic() + 5
        self.assertEqual(verify_assignment(query, {'A': True, 'B': False},
                                           ['A', 'B'], context.variables, z3, deadline), 'VERIFIED')
        self.assertEqual(verify_assignment(query, {'A': False, 'B': False},
                                           ['A', 'B'], context.variables, z3, deadline), 'REFUTED')

    def test_incomplete_extra_and_nonboolean_values(self):
        context = QueryContext(example(), z3)
        query = context.formula(QueryKind.NO_OUTPUT)
        deadline = time.monotonic() + 5
        for witness in ({'A': True}, {'A': True, 'B': False, 'P': False},
                        {'A': 1, 'B': False}):
            with self.subTest(witness=witness):
                self.assertEqual(verify_assignment(query, witness, ['A', 'B'],
                                                   context.variables, z3, deadline), 'INVALID')

    def test_expired_budget_does_not_claim_verification(self):
        context = QueryContext(example(), z3)
        self.assertEqual(verify_assignment(context.formula(QueryKind.NO_OUTPUT),
                                           {'A': True, 'B': False}, ['A', 'B'],
                                           context.variables, z3, time.monotonic() - 1), 'UNKNOWN')

    def test_deadline_crossed_during_recheck_is_unknown(self):
        context = QueryContext(example(), z3)
        with patch('witness_validation.time.monotonic', side_effect=(10.0, 12.0)):
            result = verify_assignment(context.formula(QueryKind.NO_OUTPUT),
                                       {'A': True, 'B': False}, ['A', 'B'],
                                       context.variables, z3, 11.0)
        self.assertEqual(result, 'UNKNOWN')

    def test_cli_labels_completion_and_recheck(self):
        with tempfile.TemporaryDirectory(prefix='rs3-witness-') as root:
            source = Path(root) / 'model.json'
            source.write_text(json.dumps(example()), encoding='utf-8')
            run = subprocess.run([sys.executable, str(SCRIPT), str(source)],
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)['queries']['no_output']
        self.assertEqual(result['status'], 'SAT')
        self.assertEqual(result['witness_check'], 'VERIFIED')
        self.assertEqual(result['witness_origin'], 'MODEL_COMPLETION_APPLIED')


if __name__ == '__main__':
    unittest.main()
