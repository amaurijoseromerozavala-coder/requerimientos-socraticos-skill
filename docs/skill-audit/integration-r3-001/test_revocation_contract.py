"""CLI regression checks for documentary R3-001; no product processes started."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
MODEL = Path('docs/requirements/integracion-requisitos-qa-supervisor/candidato-v0.1')
CHECKER = Path('docs/skill-audit/integration-candidate-01/check-document-model.py')
EXPECTED_STATES = ('ISOLATED', 'VERIFYING', 'WAIT_AUTHORIZATION', 'READY',
                   'INCORPORATING', 'RECOVERING', 'INCORPORATED', 'BLOCKED',
                   'REBASE_REQUIRED')

class RevocationContractTests(unittest.TestCase):
    def run_candidate(self, fsm):
        with tempfile.TemporaryDirectory(prefix='document-r3-') as folder:
            target = Path(folder)
            for rel in [CHECKER, MODEL/'requirements.json', MODEL/'incorporation-gate.json',
                        MODEL.parent/'decisiones-confirmadas.json']:
                out = target/rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes((ROOT/rel).read_bytes())
            (target/MODEL/'fsm.json').write_text(json.dumps(fsm))
            return subprocess.run([sys.executable, '-B', str(target/CHECKER)],
                                  capture_output=True, text=True, timeout=5)

    def test_current_document(self):
        result = self.run_candidate(json.loads((ROOT/MODEL/'fsm.json').read_text()))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['result'], 'PASS_WITHIN_DOCUMENT_MODEL_SCOPE')

    def test_mutations_rejected_with_contract_diagnostic(self):
        original = json.loads((ROOT/MODEL/'fsm.json').read_text())
        mutations = []
        def add(name, mutate):
            doc = copy.deepcopy(original)
            mutate(doc)
            mutations.append((name, doc))
        add('missing_handler', lambda f: f.pop('global_handlers'))
        add('empty_handlers', lambda f: f.update(global_handlers=[]))
        add('duplicate_handler', lambda f: f['global_handlers'].append(copy.deepcopy(f['global_handlers'][0])))
        add('wrong_priority', lambda f: f['global_handlers'][0].update(priority='AFTER_LOCAL_TRANSITION'))
        add('wrong_event', lambda f: f['global_handlers'][0].update(event='unmapped_revocation'))
        add('duplicate_coverage', lambda f: f['global_handlers'][0]['applies_to'].append('READY'))
        add('unknown_coverage', lambda f: f['global_handlers'][0]['applies_to'].append('UNKNOWN_STATE'))
        add('changed_default', lambda f: f.update(default='ACCEPT'))
        for state in EXPECTED_STATES:
            add('missing_coverage_'+state, lambda f, s=state: f['global_handlers'][0]['applies_to'].remove(s))
        def shrink_both(f):
            f['states'].remove('BLOCKED')
            f['global_handlers'][0]['applies_to'].remove('BLOCKED')
        add('self_consistent_shrunken_scope', shrink_both)
        for name, doc in mutations:
            with self.subTest(mutation=name):
                result = self.run_candidate(doc)
                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn('GLOBAL_REVOCATION_CONTRACT', result.stderr, name)

    def test_import_has_no_output_or_write(self):
        source = (ROOT/CHECKER).read_text()
        with tempfile.TemporaryDirectory(prefix='document-r3-import-') as folder:
            script = Path(folder)/'checker.py'
            script.write_text(source)
            result = subprocess.run([sys.executable, '-B', '-c',
                'import runpy,sys; runpy.run_path(sys.argv[1], run_name="document_module")', str(script)],
                capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, '')
            self.assertEqual(result.stderr, '')
            self.assertEqual(sorted(x.name for x in Path(folder).iterdir()), ['checker.py'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
