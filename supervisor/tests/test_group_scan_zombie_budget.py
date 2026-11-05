"""Unrelated zombies must not make a completed group look live."""

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from supervisor.process_core import ProcessSupervisor


@contextmanager
def entries(total):
    yield (SimpleNamespace(name=str(number), path=f'/proc/{number}')
           for number in range(10000, 10000 + total))


class GroupScanZombieBudgetTests(unittest.TestCase):
    def check_group(self, total, live_last=False):
        child = SimpleNamespace(pid=5555)
        def stat_text(path):
            number = int(path.parent.name)
            state = 'S' if live_last and number == 10000 + total - 1 else 'Z'
            group = 5555 if state == 'S' else 1000
            return f'{number} (synthetic) {state} 1 {group} 1 0\n'
        with patch('supervisor.process_core.os.killpg'), patch(
                'supervisor.process_core.os.scandir', return_value=entries(total)), patch.object(
                Path, 'read_text', stat_text):
            return ProcessSupervisor._group_still_exists(object(), child)

    def test_unrelated_zombie_prefix_over_4096_is_not_a_live_group(self):
        self.assertFalse(self.check_group(4100))

    def test_live_member_after_zombie_prefix_is_still_detected(self):
        self.assertTrue(self.check_group(4100, live_last=True))

    def test_scan_beyond_bounded_total_remains_uncertain(self):
        self.assertTrue(self.check_group(32769))


if __name__ == '__main__':
    unittest.main()
