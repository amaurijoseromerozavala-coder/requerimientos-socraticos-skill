"""Persistence, replay, and uncertainty falsifiers for a code-free ledger."""

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from supervisor.rs3_coordinate_ledger import CoordinateLedger, LedgerBlocked


class CoordinateLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'ledger'
        CoordinateLedger.initialize(self.root, card_id='CARD-1',
                                    coordinates=['A1', 'A2'])
        self.digest = 'a' * 64

    def test_restart_preserves_pending_and_spent_without_reuse(self):
        first = CoordinateLedger(self.root).reserve('A1', self.digest)
        self.assertEqual(first['state'], 'PENDING')
        self.assertEqual(first['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(first['execution_authorized'], False)
        restarted = CoordinateLedger(self.root)
        with self.assertRaises(LedgerBlocked):
            restarted.reserve('A1', self.digest)
        with self.assertRaises(LedgerBlocked):
            restarted.spend_pending('A1', 'b' * 64)
        spent = restarted.spend_pending('A1', self.digest)
        self.assertEqual(spent['state'], 'SPENT')
        with self.assertRaises(LedgerBlocked):
            CoordinateLedger(self.root).reserve('A1', 'b' * 64)
        self.assertEqual(CoordinateLedger(self.root).reserve('A2', 'b' * 64)['state'],
                         'PENDING')

    def test_concurrent_reservation_allows_at_most_one(self):
        def attempt(_):
            try:
                CoordinateLedger(self.root).reserve('A1', self.digest)
                return 'PENDING'
            except LedgerBlocked:
                return 'BLOCKED'
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, range(2)))
        self.assertEqual(sorted(outcomes), ['BLOCKED', 'PENDING'])
        self.assertEqual(CoordinateLedger(self.root).snapshot()['coordinates']['A1']['state'],
                         'PENDING')

    def test_distinct_processes_cannot_both_reserve_same_coordinate(self):
        program = ('import sys\n'
                   'from supervisor.rs3_coordinate_ledger import CoordinateLedger, LedgerBlocked\n'
                   'try:\n'
                   '    CoordinateLedger(sys.argv[1]).reserve("A1", "a" * 64)\n'
                   'except LedgerBlocked:\n'
                   '    raise SystemExit(2)\n')
        command = [sys.executable, '-B', '-c', program, str(self.root)]
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: subprocess.run(
                command, capture_output=True, timeout=5), range(2)))
        self.assertEqual(sorted(result.returncode for result in results), [0, 2],
                         [result.stderr.decode() for result in results])

    def test_staged_crash_blocks_until_explicit_reconciliation(self):
        CoordinateLedger(self.root).reserve('A1', self.digest)
        stage = self.root / 'state.stage'
        stage.write_bytes(b'incomplete-stage')
        os.chmod(stage, 0o600)
        with self.assertRaises(LedgerBlocked):
            CoordinateLedger(self.root).spend_pending('A1', self.digest)
        self.assertEqual(CoordinateLedger(self.root).reconcile_stage()['status'],
                         'STAGE_DISCARDED')
        self.assertEqual(CoordinateLedger(self.root).snapshot()['coordinates']['A1']['state'],
                         'PENDING')
        CoordinateLedger(self.root).spend_pending('A1', self.digest)

    def test_fsync_failure_never_returns_success(self):
        with mock.patch('supervisor.rs3_coordinate_ledger.os.fsync',
                        side_effect=OSError('synthetic')):
            with self.assertRaises(LedgerBlocked):
                CoordinateLedger(self.root).reserve('A1', self.digest)
        with self.assertRaises(LedgerBlocked):
            CoordinateLedger(self.root).reserve('A1', self.digest)
        CoordinateLedger(self.root).reconcile_stage()
        self.assertEqual(CoordinateLedger(self.root).snapshot()['coordinates']['A1']['state'],
                         'AVAILABLE')

    def test_directory_fsync_failure_after_replace_cannot_reuse(self):
        real_fsync = os.fsync
        def fail_directory(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                raise OSError('synthetic directory sync failure')
            return real_fsync(fd)
        with mock.patch('supervisor.rs3_coordinate_ledger.os.fsync', side_effect=fail_directory):
            with self.assertRaises(LedgerBlocked):
                CoordinateLedger(self.root).reserve('A1', self.digest)
        self.assertEqual(CoordinateLedger(self.root).snapshot()['coordinates']['A1']['state'],
                         'PENDING')
        with self.assertRaises(LedgerBlocked):
            CoordinateLedger(self.root).reserve('A1', self.digest)

    def test_private_bounds_and_corruption_fail_closed(self):
        self.assertEqual((self.root.stat().st_mode & 0o777), 0o700)
        self.assertEqual(((self.root / 'state.json').stat().st_mode & 0o777), 0o600)
        self.assertNotIn('secret', (self.root / 'state.json').read_text())
        os.chmod(self.root / 'state.json', 0o644)
        with self.assertRaises(LedgerBlocked):
            CoordinateLedger(self.root).snapshot()
        os.chmod(self.root / 'state.json', 0o600)
        (self.root / 'state.json').write_text('{"schema":"unknown"}\n')
        with self.assertRaises(LedgerBlocked):
            CoordinateLedger(self.root).snapshot()


if __name__ == '__main__':
    unittest.main()
