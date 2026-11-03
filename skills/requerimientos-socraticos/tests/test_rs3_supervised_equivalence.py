"""Public bounded analyzer exposes scoped rule comparison without product claims."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_logic.py'
VAR = lambda name: {'var': name}
OP = lambda operation, *args: {'op': operation, 'args': list(args)}


def model(domain=True):
    return {'inputs': ['A', 'B'], 'outputs': [], 'domain': domain,
            'rules': [{'id': 'left', 'guard': True, 'response': VAR('A')},
                      {'id': 'right', 'guard': True, 'response': VAR('B')}],
            'properties': []}


def invoke(item, *options):
    with tempfile.TemporaryDirectory(prefix='rs3-equivalence-') as root:
        source = Path(root) / 'model.json'
        source.write_text(json.dumps(item), encoding='utf-8')
        run = subprocess.run([sys.executable, str(SCRIPT), str(source), *options],
                             capture_output=True, text=True, timeout=15)
    return run.returncode, json.loads(run.stdout), run.stderr


def flags(scope, left='left', right='right'):
    return ('--compare-left', left, '--compare-right', right,
            '--compare-scope', scope)


class SupervisedEquivalenceTests(unittest.TestCase):
    def test_absolute_difference_and_contextual_equivalence(self):
        item = model(OP('eq', VAR('A'), VAR('B')))
        absolute_code, absolute, stderr = invoke(item, *flags('absolute'))
        contextual_code, contextual, stderr2 = invoke(item, *flags('contextual'))
        self.assertEqual((absolute_code, contextual_code), (0, 0), stderr + stderr2)
        self.assertEqual(absolute['equivalence']['query']['status'], 'SAT')
        self.assertEqual(absolute['equivalence']['interpretation'],
                         'DIFFERENT_ABSOLUTELY')
        self.assertEqual(absolute['equivalence']['query']['witness_check'], 'VERIFIED')
        self.assertEqual(contextual['equivalence']['basis']['status'], 'SAT')
        self.assertEqual(contextual['equivalence']['query']['status'], 'UNSAT')
        self.assertEqual(contextual['equivalence']['interpretation'],
                         'EQUIVALENT_WITHIN_CONTEXT')
        self.assertEqual(contextual['equivalence']['scope'], 'contextual')
        self.assertEqual(absolute['queries']['gap'], contextual['queries']['gap'])

    def test_unsatisfiable_context_is_vacuous_not_equivalent(self):
        code, output, stderr = invoke(model(False), *flags('contextual'))
        self.assertEqual(code, 0, stderr)
        self.assertEqual(output['equivalence']['basis']['status'], 'UNSAT')
        self.assertEqual(output['equivalence']['interpretation'], 'VACUOUS_CONTEXT')

    def test_missing_or_invalid_comparison_is_rejected(self):
        for options in (('--compare-left', 'left'),
                        flags('invalid'),
                        flags('absolute', left='missing'),
                        flags('absolute', left='left', right='left')):
            with self.subTest(options=options):
                code, output, stderr = invoke(model(), *options)
                self.assertEqual(code, 2, stderr)
                self.assertEqual(output['error']['code'], 'INVALID_INPUT')
                self.assertNotIn('equivalence', output)

    def test_no_flags_keeps_legacy_output_shape(self):
        code, output, stderr = invoke(model())
        self.assertEqual(code, 0, stderr)
        self.assertNotIn('equivalence', output)
        self.assertEqual(set(output['queries']),
                         {'domain', 'gap', 'no_output', 'rule_consistency'})

    def test_exhausted_budget_does_not_claim_equivalence(self):
        code, output, stderr = invoke(model(), *flags('contextual'),
                                      '--timeout', '0.000001')
        self.assertEqual(code, 3, stderr)
        self.assertEqual(output['status'], 'INCONCLUSIVE')
        self.assertNotIn('equivalence', output)


if __name__ == '__main__':
    unittest.main()
