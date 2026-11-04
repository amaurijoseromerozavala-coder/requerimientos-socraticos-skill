"""Falsifiers for a verified uncovered input becoming an unratified scenario."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_logic.py'
V = lambda variable: {'var': variable}


def run_model(model):
    raw = json.dumps(model, sort_keys=True).encode()
    with tempfile.TemporaryDirectory(prefix='gap-scenario-') as root:
        source = Path(root) / 'model.json'
        source.write_bytes(raw)
        completed = subprocess.run([sys.executable, str(SCRIPT), str(source)],
                                   capture_output=True, text=True, timeout=10)
    return completed.returncode, json.loads(completed.stdout), hashlib.sha256(raw).hexdigest()


def model(guard):
    return {'inputs': ['A', 'B'], 'outputs': ['P'],
            'domain': {'op': 'or', 'args': [V('A'), V('B')]},
            'rules': [{'id': 'only_A', 'guard': guard, 'response': V('P')}],
            'properties': []}


class GapScenarioInterrogationTests(unittest.TestCase):
    def test_sat_gap_exposes_verified_assignment_without_inventing_meaning(self):
        code, result, digest = run_model(model(V('A')))
        self.assertEqual(code, 0)
        self.assertEqual(result['queries']['gap']['status'], 'SAT')
        packet = result['gap_interpretation']
        self.assertEqual(packet['status'], 'NEEDS_HUMAN_INTERPRETATION')
        self.assertEqual(packet['input_assignment'], {'A': False, 'B': True})
        self.assertEqual(packet['inactive_rule_ids'], ['only_A'])
        self.assertEqual(packet['model_sha256'], digest)
        self.assertEqual(packet['scenario_scope'], 'SINGLE_WITNESS_NOT_ALL_COMBINATIONS')
        self.assertEqual(packet['remaining_gap_space'], 'NOT_ENUMERATED')
        self.assertEqual(packet['semantic_status'], 'UNINTERPRETED')
        self.assertEqual(packet['authority'], 'PROPOSAL_ONLY')
        self.assertNotIn('MISSING_REQUIREMENT_CONFIRMED', str(packet))
        self.assertEqual(result['queries']['no_output']['status'], 'UNSAT')

    def test_unsat_gap_has_no_interpretation_candidate(self):
        code, result, _ = run_model(model(True))
        self.assertEqual(code, 0)
        self.assertEqual(result['queries']['gap']['status'], 'UNSAT')
        self.assertEqual(result['gap_interpretation']['status'], 'NO_CANDIDATE')
        self.assertNotIn('input_assignment', result['gap_interpretation'])

    def test_unverified_or_mutated_witness_fails_closed(self):
        sys.path.insert(0, str(SCRIPT.parent))
        from gap_scenario import build_gap_interpretation
        candidate = model(V('A'))
        valid_query = {'status': 'SAT', 'witness_check': 'VERIFIED',
                       'witness': {'A': False, 'B': True}}
        for query in (
            {'status': 'UNKNOWN'},
            {'status': 'SAT', 'witness_check': 'UNKNOWN',
             'witness': {'A': False, 'B': True}},
            {**valid_query, 'witness': {'A': True, 'B': False}},
            {**valid_query, 'witness': {'A': False}},
        ):
            with self.subTest(query=query):
                packet = build_gap_interpretation(candidate, query, '0' * 64)
                self.assertNotEqual(packet['status'], 'NEEDS_HUMAN_INTERPRETATION')
                self.assertNotIn('input_assignment', packet)


if __name__ == '__main__':
    unittest.main()
