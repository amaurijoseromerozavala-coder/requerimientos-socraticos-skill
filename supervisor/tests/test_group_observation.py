"""Bounded observation when the direct child exits before its process group."""
import os
from pathlib import Path
import signal
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from supervisor.process_core import ProcessSupervisor, Limits


def _running(pid):
    try:
        return Path(f'/proc/{pid}/stat').read_text().split(') ', 1)[1][0] != 'Z'
    except FileNotFoundError:
        return False


class GroupObservationTests(unittest.TestCase):
    def test_reaped_child_with_detached_pipes_blocks_admission(self):
        with tempfile.TemporaryDirectory(prefix='supervisor-group-observation-') as directory:
            marker = Path(directory) / 'descendant.pid'
            parent = (
                'import subprocess,sys; '
                'p=subprocess.Popen([sys.executable,"-B","-c","import time; time.sleep(5)"],'
                'stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); '
                f'open({str(marker)!r},"w").write(str(p.pid))'
            )
            pid = None
            try:
                supervisor = ProcessSupervisor(
                    (sys.executable, '-B', '-c', parent),
                    Limits(wall_seconds=1, grace_seconds=.1, cleanup_seconds=.2))
                result = supervisor.run()
                pid = int(marker.read_text())
                self.assertTrue(_running(pid), 'fixture descendant ended before observation')
                self.assertEqual(result['returncode'], 0)
                self.assertEqual(result['status'], 'INFRA_LOCK')
                self.assertEqual(result['cleanup'], 'UNCONFIRMED')
                self.assertEqual(supervisor.run()['status'], 'INFRA_LOCK')
            finally:
                if pid is not None and _running(pid):
                    os.kill(pid, signal.SIGKILL)

    def test_readme_states_current_partial_journal_boundary(self):
        readme = (ROOT / 'README.md').read_text()
        self.assertIn('RESERVED→ACTIVE→STOPPING', readme)
        self.assertIn('enlace optativo', readme)
        self.assertIn('sin integración QA', readme)


if __name__ == '__main__':
    unittest.main()
