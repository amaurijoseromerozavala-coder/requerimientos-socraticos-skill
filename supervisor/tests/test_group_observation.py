"""Bounded observation when the direct child exits before its process group."""
import os
from pathlib import Path
import signal
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from supervisor.process_core import ProcessSupervisor, Limits


def _running(pid):
    try:
        return Path(f'/proc/{pid}/stat').read_text().split(') ', 1)[1][0] != 'Z'
    except FileNotFoundError:
        return False


class GroupObservationTests(unittest.TestCase):
    def test_escalation_waits_for_group_observation_before_reaping(self):
        supervisor = ProcessSupervisor(
            (sys.executable, '-B', '-c',
             'import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); '
             'print("ready",flush=True); time.sleep(4)'),
            Limits(wall_seconds=.15, grace_seconds=.05, cleanup_seconds=.3))
        original_signal = supervisor._signal_owned_group
        original_probe = supervisor._group_still_exists
        observed = {'kill_sent': False, 'delayed_once': False}

        def signal_group(child, requested_signal):
            original_signal(child, requested_signal)
            if requested_signal == signal.SIGKILL:
                observed['kill_sent'] = True

        def observe_group(child):
            active = original_probe(child)
            if observed['kill_sent'] and not observed['delayed_once']:
                observed['delayed_once'] = True
                return True  # A stale active observation directly after escalation.
            return active

        with (patch.object(supervisor, '_signal_owned_group', side_effect=signal_group),
              patch.object(supervisor, '_group_still_exists', side_effect=observe_group)):
            result = supervisor.run()
        self.assertTrue(observed['delayed_once'])
        self.assertEqual(result['signals_requested'], ['SIGTERM', 'SIGKILL'])
        self.assertEqual(result['cleanup'], 'CONFIRMED')

    def test_exited_leader_retains_group_identity_until_cleanup(self):
        with tempfile.TemporaryDirectory(prefix='supervisor-pre-reap-') as directory:
            marker = Path(directory) / 'descendant.pid'
            grandchild = ('import signal,time; '
                          'signal.signal(signal.SIGTERM,signal.SIG_IGN); '
                          'time.sleep(4)')
            parent = (
                'import subprocess,sys; '
                f'p=subprocess.Popen([sys.executable,"-B","-c",{grandchild!r}]); '
                f'open({str(marker)!r},"w").write(str(p.pid))'
            )
            pid = None
            try:
                supervisor = ProcessSupervisor(
                    (sys.executable, '-B', '-c', parent),
                    Limits(wall_seconds=.6, grace_seconds=.1, cleanup_seconds=.5))
                result = supervisor.run()
                pid = int(marker.read_text())
                self.assertEqual(result['returncode'], 0)
                self.assertEqual(result['signals_requested'], ['SIGTERM', 'SIGKILL'])
                self.assertEqual(result['cleanup'], 'CONFIRMED')
                self.assertEqual(result['status'], 'STOPPED')
                self.assertEqual(result['stop_reason'], 'WALL_DEADLINE')
                for _ in range(20):
                    if not _running(pid):
                        break
                    time.sleep(.01)
                self.assertFalse(_running(pid), 'same-group descendant remains active')
            finally:
                if pid is not None and _running(pid):
                    os.kill(pid, signal.SIGKILL)

    def test_exited_leader_with_detached_pipes_stops_owned_group(self):
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
                self.assertEqual(result['returncode'], 0)
                self.assertEqual(result['status'], 'STOPPED')
                self.assertEqual(result['stop_reason'], 'GROUP_CLEANUP')
                self.assertEqual(result['cleanup'], 'CONFIRMED')
                self.assertEqual(result['signals_requested'], ['SIGTERM'])
                self.assertFalse(_running(pid), 'owned-group member remains active')
            finally:
                if pid is not None and _running(pid):
                    os.kill(pid, signal.SIGKILL)

    def test_readme_states_current_partial_journal_boundary(self):
        readme = (ROOT / 'README.md').read_text()
        self.assertIn('RESERVED→ACTIVE→STOPPING', readme)
        self.assertIn('enlace optativo', readme)
        self.assertIn('sin integración QA', readme)
        self.assertIn('solicita terminación al grupo propio antes de recolectar', readme)


if __name__ == '__main__':
    unittest.main()
