"""Bounded local observation of the supervisor's own process group."""
import os
from pathlib import Path
import signal
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from supervisor.process_core import ProcessSupervisor, Limits


def _running(pid):
    try:
        # A reparented zombie consumes no CPU and cannot receive a signal.
        return Path(f'/proc/{pid}/stat').read_text().split(') ', 1)[1][0] != 'Z'
    except FileNotFoundError:
        return False


class GroupTerminationTests(unittest.TestCase):
    def test_timeout_stops_same_group_descendant(self):
        grandchild = (
            'import signal,time; '
            'signal.signal(signal.SIGTERM, signal.SIG_IGN); '
            'print("GRANDCHILD_READY", flush=True); time.sleep(5)'
        )
        parent = (
            'import subprocess,sys,signal,time; '
            'signal.signal(signal.SIGTERM, signal.SIG_IGN); '
            f'p=subprocess.Popen([sys.executable,"-B","-c",{grandchild!r}]); '
            'print("GRANDCHILD_PID",p.pid,flush=True); time.sleep(5)'
        )
        supervisor = ProcessSupervisor(
            (sys.executable, '-B', '-c', parent),
            Limits(wall_seconds=.8, grace_seconds=.1, cleanup_seconds=.5))
        pid = None
        try:
            result = supervisor.run()
            lines = result['stdout'].decode().splitlines()
            pid = int(next(line.split()[1] for line in lines if line.startswith('GRANDCHILD_PID ')))
            self.assertIn('GRANDCHILD_READY', lines)
            self.assertEqual(result['stop_reason'], 'WALL_DEADLINE')
            self.assertEqual(result['returncode'], -signal.SIGKILL)
            self.assertEqual(result['cleanup'], 'CONFIRMED')
            for _ in range(20):
                if not _running(pid):
                    break
                time.sleep(.01)
            self.assertFalse(_running(pid), 'same-group descendant survived cleanup')
        finally:
            if pid is not None and _running(pid):
                os.kill(pid, signal.SIGKILL)


if __name__ == '__main__':
    unittest.main()
