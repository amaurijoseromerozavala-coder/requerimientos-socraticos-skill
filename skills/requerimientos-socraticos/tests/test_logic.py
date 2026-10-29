"""Behavioral tests for the bounded standalone boolean analyzer."""
import json
import os
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_logic.py'
V = lambda name: {'var': name}
OP = lambda op, *args: {'op': op, 'args': list(args)}

class LogicTests(unittest.TestCase):
    def run_cli(self, model, *args, python=None, extra=()):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'model.json'
            path.write_text(json.dumps(model), encoding='utf-8')
            run = subprocess.run([python or sys.executable, *extra, str(SCRIPT), str(path), *args], capture_output=True, text=True, timeout=40)
            return run.returncode, json.loads(run.stdout)

    def model(self):
        return {'inputs': ['x'], 'outputs': ['a', 'b'], 'domain': True, 'rules': [], 'properties': []}

    def test_triple_conflict_and_regional_counterexample(self):
        m = self.model()
        m['rules'] = [
            {'id': 'a', 'guard': V('x'), 'response': V('a')},
            {'id': 'b', 'guard': V('x'), 'response': V('b')},
            {'id': 'c', 'guard': V('x'), 'response': OP('not', OP('and', V('a'), V('b')))},
        ]
        code, out = self.run_cli(m, '--table')
        self.assertEqual(code, 0)
        self.assertEqual(out['queries']['no_output']['status'], 'SAT')
        self.assertEqual(out['queries']['no_output']['witness']['x'], True)
        self.assertEqual(out['queries']['gap']['status'], 'SAT')
        self.assertEqual(out['table']['feasible_inputs'], 2)
        self.assertEqual(out['table']['covered_inputs'], 1)
        self.assertEqual(out['table']['inputs_without_output'], 1)
        self.assertEqual(out['queries']['rule_consistency']['status'], 'SAT')
        self.assertEqual(out['table']['coverage']['metric'], 'GUARD_ACTIVATION_COVERAGE')
        self.assertEqual(out['table']['coverage']['numerator'], 1)
        self.assertEqual(out['provenance']['model_sha256'], hashlib.sha256(json.dumps(m).encode()).hexdigest())
        self.assertTrue(out['provenance']['z3_version'])
        self.assertGreaterEqual(out['provenance']['elapsed_seconds'], 0)
        for omitted in range(3):
            pair = dict(m, rules=[rule for i, rule in enumerate(m['rules']) if i != omitted])
            _, pair_result = self.run_cli(pair)
            self.assertEqual(pair_result['queries']['no_output']['status'], 'UNSAT')

    def test_empty_domain_and_property(self):
        m = self.model(); m['domain'] = False
        _, out = self.run_cli(m)
        self.assertEqual(out['domain_validity'], 'INVALID')
        m['domain'] = True
        m['rules'] = [{'id': 'r', 'guard': True, 'response': V('a')}]
        m['properties'] = [{'id': 'p', 'expression': V('a')}]
        _, out = self.run_cli(m)
        self.assertEqual(out['properties'][0]['counterexample']['status'], 'UNSAT')
        self.assertIn('model', out['properties'][0]['interpretation'])
        self.assertEqual(out['properties'][0]['consequence'], 'ENTAILED')
        m['rules'].append({'id': 'contradiction', 'guard': True, 'response': OP('not', V('a'))})
        _, out = self.run_cli(m)
        self.assertEqual(out['properties'][0]['consequence'], 'VACUOUS')

    def test_bounds_and_invalid_ast(self):
        m = self.model(); m['inputs'] = ['v%d' % i for i in range(32)]; m['outputs'] = []
        self.assertEqual(self.run_cli(m)[0], 0)
        m['inputs'].append('v32')
        self.assertNotEqual(self.run_cli(m)[0], 0)
        for bad in [1, {'var': 'missing'}, {'op': 'not', 'args': [True, False]}, {'op': 'xor', 'args': [True, False]}, {'var': 'a'}]:
            m = self.model(); m['domain'] = bad
            self.assertNotEqual(self.run_cli(m)[0], 0, bad)
        m = self.model(); m['rules'] = [{'id': 'r', 'guard': True, 'response': True}, {'id': 'r', 'guard': True, 'response': True}]
        self.assertNotEqual(self.run_cli(m)[0], 0)
        m = self.model(); m['extra'] = 1
        self.assertNotEqual(self.run_cli(m)[0], 0)

    def test_budget_and_table_limits(self):
        m = self.model()
        _, out = self.run_cli(m, '--timeout', '0.000001', '--table')
        self.assertEqual(out['status'], 'INCONCLUSIVE')
        self.assertEqual(out['error']['code'], 'WALL_CLOCK_LIMIT')
        self.assertNotIn('coverage', out)
        m['inputs'] = ['x%d' % i for i in range(13)]
        _, out = self.run_cli(m, '--table')
        self.assertEqual(out['table']['status'], 'NOT_RUN')
        self.assertNotEqual(self.run_cli(m, '--timeout', '31')[0], 0)

    def test_empty_variables_and_scope(self):
        m = {'inputs': [], 'outputs': [], 'domain': True, 'rules': [], 'properties': []}
        _, out = self.run_cli(m, '--table')
        self.assertEqual(out['queries']['domain']['status'], 'SAT')
        self.assertEqual(out['queries']['gap']['status'], 'SAT')
        self.assertEqual(out['queries']['no_output']['status'], 'UNSAT')
        self.assertEqual(out['table']['possible_rows'], 1)
        m['domain'] = False
        _, out = self.run_cli(m, '--table')
        self.assertEqual(out['domain_validity'], 'INVALID')
        self.assertNotIn('coverage', out['table'])
        m = self.model()
        m['rules'] = [{'id': 'r', 'guard': V('a'), 'response': True}]
        self.assertNotEqual(self.run_cli(m)[0], 0)
        m['rules'][0]['guard'] = True
        m['properties'] = [{'id': 'r', 'expression': True}]
        self.assertNotEqual(self.run_cli(m)[0], 0)

    def test_solver_failure_is_structured(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / 'z3.py').write_text("class Z3Exception(Exception): pass\ndef Bool(name): raise Z3Exception('fixture failure')\n")
            model = base / 'model.json'
            model.write_text(json.dumps(self.model()))
            env = dict(os.environ, PYTHONPATH=str(base))
            run = subprocess.run([sys.executable, str(SCRIPT), str(model)], env=env, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(json.loads(run.stdout)['error'], {'code': 'SOLVER_ERROR', 'message': 'fixture failure'})
            self.assertNotIn('Traceback', run.stderr)

    def test_missing_solver_is_structured(self):
        code, out = self.run_cli(self.model(), extra=('-S',))
        self.assertNotEqual(code, 0)
        self.assertEqual(out['error']['code'], 'SOLVER_UNAVAILABLE')

if __name__ == '__main__': unittest.main()
