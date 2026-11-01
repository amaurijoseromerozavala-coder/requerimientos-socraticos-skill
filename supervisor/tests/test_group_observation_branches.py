"""Focused checks for the R3-001 process-group observation branches."""
from contextlib import nullcontext
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
from types import SimpleNamespace
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


class GroupObservationBranches(unittest.TestCase):
    def test_proc_read_error_latches_infra_lock(self):
        with tempfile.TemporaryDirectory(prefix='group-observation-error-') as directory:
            marker = Path(directory) / 'descendant.pid'
            parent = (
                'import subprocess,sys; '
                'p=subprocess.Popen([sys.executable,"-B","-c","import time; time.sleep(3)"],'
                'stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); '
                f'open({str(marker)!r},"w").write(str(p.pid))'
            )
            supervisor = ProcessSupervisor(
                (sys.executable, '-B', '-c', parent),
                Limits(wall_seconds=1, grace_seconds=.1, cleanup_seconds=.2))
            pid = None
            try:
                with patch('supervisor.process_core.Path.read_text',
                           side_effect=OSError('controlled proc observation failure')):
                    result = supervisor.run()
                pid = int(marker.read_text())
                self.assertTrue(_running(pid), 'fixture ended before observation')
                self.assertEqual(result['returncode'], 0)
                self.assertEqual(result['cleanup'], 'UNCONFIRMED')
                self.assertEqual(result['status'], 'INFRA_LOCK')
                self.assertEqual(supervisor.run()['status'], 'INFRA_LOCK')
            finally:
                if pid is not None and _running(pid):
                    os.kill(pid, signal.SIGKILL)

    def test_zombie_only_observation_preserves_normal_exit(self):
        child = []
        original = subprocess.Popen

        def launch(*args, **kwargs):
            process = original(*args, **kwargs)
            child.append(process)
            return process

        fake_entry = SimpleNamespace(name='999', path='/proc/999')
        def zombie_stat(*_args, **_kwargs):
            return f'999 (zombie) Z 1 {child[0].pid} 0 0'

        supervisor = ProcessSupervisor(
            (sys.executable, '-B', '-c', 'print("done")'),
            Limits(wall_seconds=1, grace_seconds=.1, cleanup_seconds=.2))
        with (patch('supervisor.process_core.subprocess.Popen', side_effect=launch),
              patch('supervisor.process_core.os.killpg', return_value=None) as group_probe,
              patch('supervisor.process_core.os.scandir',
                    return_value=nullcontext([fake_entry])) as scan,
              patch('supervisor.process_core.Path.read_text', side_effect=zombie_stat)):
            result = supervisor.run()
        self.assertTrue(group_probe.called)
        self.assertTrue(scan.called)
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['status'], 'EXITED')
        self.assertEqual(result['cleanup'], 'CONFIRMED')


if __name__ == '__main__':
    unittest.main()
