"""RS3 distinguishes an unknown name from a declared variable in the wrong role."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from logic_engine import InputError, validate


def model():
    return {'inputs': ['A'], 'outputs': ['production_ready'], 'domain': True,
            'rules': [{'id': 'rule', 'guard': {'var': 'A'},
                       'response': {'var': 'production_ready'}}],
            'properties': [{'id': 'property',
                            'expression': {'var': 'production_ready'}}]}


class VariableRoleTests(unittest.TestCase):
    def test_output_in_domain_or_guard_has_typed_role_diagnostic(self):
        for location in ('domain', 'guard'):
            with self.subTest(location=location):
                item = model()
                if location == 'domain':
                    item['domain'] = {'var': 'production_ready'}
                else:
                    item['rules'][0]['guard'] = {'var': 'production_ready'}
                with self.assertRaisesRegex(InputError, '^WRONG_VARIABLE_ROLE$'):
                    validate(item)

    def test_unknown_name_is_not_misclassified_as_wrong_role(self):
        for location in ('guard', 'response'):
            with self.subTest(location=location):
                item = model()
                item['rules'][0][location] = {'var': 'UNDECLARED'}
                with self.assertRaisesRegex(InputError, '^UNKNOWN_VARIABLE$'):
                    validate(item)

    def test_declared_output_is_valid_in_response_and_property(self):
        self.assertGreater(validate(model()), 0)

    def test_cli_preserves_invalid_input_exit_and_reports_role(self):
        item = model()
        item['rules'][0]['guard'] = {'var': 'production_ready'}
        with tempfile.TemporaryDirectory(prefix='rs3-role-') as root:
            source = Path(root) / 'model.json'
            source.write_text(json.dumps(item), encoding='utf-8')
            run = subprocess.run([sys.executable, str(SCRIPTS.parent / 'scripts' /
                                                  'analyze_logic.py'), str(source)],
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 2, run.stderr)
        output = json.loads(run.stdout)
        self.assertEqual(output['error']['code'], 'INVALID_INPUT')
        self.assertEqual(output['error']['message'], 'WRONG_VARIABLE_ROLE')
        self.assertNotIn('queries', output)


if __name__ == '__main__':
    unittest.main()
