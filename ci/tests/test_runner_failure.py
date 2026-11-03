"""The CI runner must preserve a suite failure and stop the remaining suites."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / 'ci/run_quality.sh'
SYNTHETIC = 'SYNTHETIC_SECRET_DO_NOT_USE_001'


class RunnerFailureTests(unittest.TestCase):
    def test_suite_failure_is_bounded_and_nonzero(self):
        with tempfile.TemporaryDirectory(prefix='ci-runner-failure-') as directory:
            fake_python = Path(directory) / 'python3'
            fake_python.write_text(
                '#!/bin/sh\n'
                'case "$*" in\n'
                '  *check_rdd_record.py*) echo CONTROLLED_RECORD_OK; exit 0;;\n'
                '  *probe_environment*) echo CONTROLLED_OBSERVATION; exit 0;;\n'
                '  *safe_suite_capture.py*) exec "$CI_CAPTURE_REAL_PYTHON" "$@";;\n'
                '  *unittest*) echo CONTROLLED_SUITE_FAILURE --token=' + SYNTHETIC + ' >&2; exit 7;;\n'
                'esac\nexit 9\n', encoding='utf-8')
            fake_python.chmod(0o700)
            env = dict(os.environ, PATH=directory + os.pathsep + os.environ['PATH'],
                       CI_CAPTURE_REAL_PYTHON=sys.executable)
            path = Path(env.get('CI_RUNNER_PATH', str(RUNNER)))
            result = subprocess.run(['bash', str(path)], cwd=ROOT, env=env,
                                    capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 7)
        self.assertIn('ci: FAILED exit=7', result.stderr)
        self.assertIn('CONTROLLED_SUITE_FAILURE', result.stderr)
        self.assertNotIn(SYNTHETIC, result.stderr)
        self.assertNotIn('supervisor:', result.stdout)
        self.assertLessEqual(len(result.stdout) + len(result.stderr), 16384)


if __name__ == '__main__':
    unittest.main()
