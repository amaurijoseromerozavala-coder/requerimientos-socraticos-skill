"""Bounded real descendant fixture, plus an explicit false-completeness mutation."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCENARIO = Path('supervisor/tests/retained_pipe_scenario.py')


class RetainedPipeTests(unittest.TestCase):
    def test_reaped_child_with_open_descendant_pipes(self):
        run = subprocess.run([sys.executable, '-B', str(ROOT/SCENARIO)],
                             capture_output=True, text=True, timeout=8)
        self.assertEqual(run.returncode, 0, run.stderr)
        observed = json.loads(run.stdout)
        self.assertIn(observed['auxiliary_pid'], observed['fixture_reaped_pids'])
        self.assertFalse(observed['fixture_children_remaining'])
        print(run.stdout, end='')

    def test_false_complete_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='retained-pipe-mutant-') as directory:
            root = Path(directory)
            for rel in (SCENARIO, Path('supervisor/process_core.py'),
                        Path('supervisor/journal.py'), Path('supervisor/safe_capture.py'),
                        Path('supervisor/_child_entry.py')):
                target = root/rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/rel, target)
            core = root/'supervisor/process_core.py'
            source = core.read_text()
            before = "'capture_complete': all(eof.values())"
            self.assertEqual(source.count(before), 1)
            core.write_text(source.replace(before, "'capture_complete': True"))
            run = subprocess.run([sys.executable, '-B', str(root/SCENARIO)],
                                 capture_output=True, text=True, timeout=8)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('CAPTURE_MUST_BE_INCOMPLETE', run.stderr)
            self.assertNotIn('FIXTURE_REAP_DEADLINE', run.stderr)
            print(json.dumps({'negative_control':'false_capture_complete',
                              'exit':run.returncode,'expected_assertion_observed':True}))


if __name__ == '__main__':
    unittest.main(verbosity=2)
