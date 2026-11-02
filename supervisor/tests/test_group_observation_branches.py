"""Focused checks for the R3-001 process-group observation branches."""
from contextlib import nullcontext
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from supervisor.process_core import ProcessSupervisor, Limits


class GroupObservationBranches(unittest.TestCase):
    def test_group_observation_error_latches_infra_lock(self):
        supervisor = ProcessSupervisor(
            (sys.executable, '-B', '-c', 'print("done")'),
            Limits(wall_seconds=1, grace_seconds=.1, cleanup_seconds=.2))
        with patch.object(supervisor, '_group_still_exists',
                          side_effect=OSError('controlled group observation failure')) as probe:
            result = supervisor.run()
        self.assertTrue(probe.called)
        self.assertTrue(result['launched'])
        self.assertEqual(result['diagnostic'], 'OSError')
        self.assertEqual(result['cleanup'], 'UNCONFIRMED')
        self.assertEqual(result['status'], 'INFRA_LOCK')
        self.assertEqual(supervisor.run()['status'], 'INFRA_LOCK')

    def test_proc_read_error_is_uncertain_when_member_is_present(self):
        child = SimpleNamespace(pid=12345)
        entry = SimpleNamespace(name='54321', path='/proc/54321')
        supervisor = ProcessSupervisor((sys.executable, '-B', '-c', 'pass'))
        with (patch('supervisor.process_core.os.killpg', return_value=None),
              patch('supervisor.process_core.os.scandir',
                    return_value=nullcontext([entry])),
              patch('supervisor.process_core.Path.read_text',
                    side_effect=OSError('controlled proc read failure'))):
            self.assertTrue(supervisor._group_still_exists(child))

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
