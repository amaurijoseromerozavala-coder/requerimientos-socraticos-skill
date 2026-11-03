"""RS3 synthetic counterexamples compared with an independent finite oracle."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from rs3_query_oracle import classify_inputs, mutant_no_output


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_logic.py'
V = lambda variable: {'var': variable}
OP = lambda operation, *args: {'op': operation, 'args': list(args)}


def run_model(model):
    with tempfile.TemporaryDirectory(prefix='rs3-query-') as root:
        source = Path(root) / 'model.json'
        source.write_text(json.dumps(model, sort_keys=True), encoding='utf-8')
        result = subprocess.run([sys.executable, str(SCRIPT), str(source)],
                                capture_output=True, text=True, timeout=10)
    return result.returncode, json.loads(result.stdout), result.stderr


class RS3QueryOracleTests(unittest.TestCase):
    def test_no_output_counterexample_differs_from_mutant(self):
        model = {'inputs': ['A', 'B'], 'outputs': ['P'], 'domain': True,
                 'rules': [{'id': 'condition', 'guard': True,
                            'response': OP('implies', V('A'), V('B'))}],
                 'properties': []}
        expected = classify_inputs(model)
        self.assertEqual(expected['no_output'], [{'A': True, 'B': False}])
        self.assertEqual(mutant_no_output(model), [])
        exit_code, output, stderr = run_model(model)
        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(output['queries']['no_output']['status'], 'SAT')
        self.assertIn(output['queries']['no_output']['witness'], expected['no_output'])
        self.assertEqual(output['queries']['rule_consistency']['status'], 'SAT')

    def test_gap_does_not_imply_no_output(self):
        model = {'inputs': ['A'], 'outputs': ['P'], 'domain': True,
                 'rules': [{'id': 'inactive', 'guard': False, 'response': V('P')}],
                 'properties': []}
        expected = classify_inputs(model)
        self.assertEqual(len(expected['gap']), 2)
        self.assertEqual(expected['no_output'], [])
        exit_code, output, stderr = run_model(model)
        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(output['queries']['gap']['status'], 'SAT')
        self.assertEqual(output['queries']['no_output']['status'], 'UNSAT')

    def test_global_and_regional_conflict_have_distinct_consistency(self):
        for guard, consistency in ((True, 'UNSAT'), (V('A'), 'SAT')):
            with self.subTest(consistency=consistency):
                model = {'inputs': ['A'], 'outputs': ['P'], 'domain': True,
                         'rules': [{'id': 'positive', 'guard': guard, 'response': V('P')},
                                   {'id': 'negative', 'guard': guard,
                                    'response': OP('not', V('P'))}],
                         'properties': []}
                expected = classify_inputs(model)
                self.assertTrue(expected['no_output'])
                self.assertEqual(bool(expected['compatible_pairs']), consistency == 'SAT')
                exit_code, output, stderr = run_model(model)
                self.assertEqual(exit_code, 0, stderr)
                self.assertEqual(output['queries']['no_output']['status'], 'SAT')
                self.assertEqual(output['queries']['rule_consistency']['status'], consistency)

    def test_output_in_guard_is_invalid_input(self):
        model = {'inputs': ['A'], 'outputs': ['P'], 'domain': True,
                 'rules': [{'id': 'wrong_role', 'guard': V('P'), 'response': True}],
                 'properties': []}
        exit_code, output, stderr = run_model(model)
        self.assertEqual(exit_code, 2, stderr)
        self.assertEqual(output['error']['code'], 'INVALID_INPUT')
        self.assertNotIn('queries', output)


if __name__ == '__main__':
    unittest.main()
