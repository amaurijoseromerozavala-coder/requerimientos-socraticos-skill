"""Durable output accounting and safe terminal reuse of the optional journal."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from supervisor.journal import Journal, JournalBlocked
from supervisor.process_core import Limits, ProcessSupervisor


def identity(run_id):
    return {'run_id': run_id, 'boot_id': 'bounded-test-boot',
            'pid_namespace_identity': 'bounded-test-namespace',
            'owner_uid': os.getuid(), 'checker_manifest_digest': 'a' * 64,
            'policy_digest': 'b' * 64}


class DurableReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='durable-reconciliation-')
        self.root = Path(self.temp.name) / 'journal'
        Journal.initialize(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_two_real_runs_reuse_only_after_durable_receipts(self):
        with Journal(self.root) as journal:
            for name in ('first', 'second'):
                runner = ProcessSupervisor(
                    (sys.executable, '-B', '-c', f'print({name!r})'),
                    Limits(wall_seconds=1, grace_seconds=.1, cleanup_seconds=.2),
                    journal=journal, journal_identity=identity(name))
                result = runner.run()
                self.assertEqual(result['status'], 'EXITED')
                self.assertEqual(result['cleanup'], 'CONFIRMED')
                self.assertEqual(journal.inspect()['state'], 'IDLE')
                record = journal.accounting()['runs'][-1]
                self.assertEqual(record['state'], 'STORED')
                slot = self.root / 'runs' / record['slot']
                self.assertEqual((slot / 'stdout.bin').read_bytes(), (name + '\n').encode())
                self.assertTrue((slot / 'receipt.json').is_file())
                self.assertEqual((slot / 'stdout.bin').stat().st_mode & 0o777, 0o600)
            self.assertEqual(len(journal.accounting()['runs']), 2)

    def test_reconciliation_rejects_mutated_capture_and_unresolved_reservation(self):
        with Journal(self.root) as journal:
            journal.reserve(identity('first'))
            with self.assertRaises(JournalBlocked):
                journal.reconcile_terminated()
            journal.record_active(123, 'start-123')
            journal.record_terminated(123, 'start-123')
            journal.store_capture(123, 'start-123', 0, b'ok\n', b'', True)
            record = journal.accounting()['runs'][0]
            (self.root / 'runs' / record['slot'] / 'stdout.bin').write_bytes(b'bad')
            with self.assertRaises(JournalBlocked):
                journal.reconcile_terminated()
            self.assertEqual(journal.inspect()['state'], 'CONFIRMED_TERMINATED')

    def test_duplicate_run_id_blocks(self):
        with Journal(self.root) as journal:
            journal.reserve(identity('one'))
            with self.assertRaises(JournalBlocked):
                journal.reserve(identity('one'))
            self.assertEqual(journal.inspect()['state'], 'RESERVED')

    def test_full_retention_budget_blocks_before_next_reservation(self):
        with Journal(self.root) as journal:
            for number in range(99):
                journal.reserve(identity(str(number)))
                journal.record_active(123, 'start-123')
                journal.record_terminated(123, 'start-123')
                journal.store_capture(123, 'start-123', 0, b'', b'', True)
                journal.reconcile_terminated()
            before = journal.accounting()
            with self.assertRaisesRegex(JournalBlocked, 'RETENTION_CAPACITY_EXCEEDED'):
                journal.reserve(identity('overflow'))
            self.assertEqual(journal.inspect()['state'], 'IDLE')
            self.assertEqual(journal.accounting(), before)

    def test_capture_write_failure_does_not_reconcile(self):
        with Journal(self.root) as journal:
            runner = ProcessSupervisor(
                (sys.executable, '-B', '-c', 'print("ok")'),
                Limits(wall_seconds=1, grace_seconds=.1, cleanup_seconds=.2),
                journal=journal, journal_identity=identity('write-failure'))
            with patch.object(journal, 'store_capture', side_effect=OSError('controlled write failure')):
                result = runner.run()
            self.assertEqual(result['status'], 'INFRA_LOCK')
            self.assertEqual(runner.state, 'INFRA_LOCK')
            self.assertEqual(journal.inspect()['state'], 'CONFIRMED_TERMINATED')
            self.assertEqual(journal.accounting()['runs'][0]['state'], 'RESERVED')

    def test_visible_storage_below_reservation_blocks_before_launch(self):
        with Journal(self.root) as journal:
            runner = ProcessSupervisor(
                (sys.executable, '-B', '-c', 'print("unreachable")'),
                Limits(wall_seconds=1, grace_seconds=.1, cleanup_seconds=.2),
                journal=journal, journal_identity=identity('no-space'))
            with patch('supervisor.journal.os.fstatvfs', return_value=SimpleNamespace(
                    f_bavail=1, f_frsize=4096)), patch(
                    'supervisor.process_core.subprocess.Popen') as launch:
                result = runner.run()
            launch.assert_not_called()
            self.assertEqual(result['status'], 'INFRA_LOCK')
            self.assertEqual(journal.inspect()['state'], 'IDLE')
            self.assertEqual(journal.accounting()['runs'], [])

    def test_reopen_reconciles_only_verified_terminal_capture(self):
        with Journal(self.root) as journal:
            journal.reserve(identity('interrupted-after-store'))
            journal.record_active(123, 'start-123')
            journal.record_terminated(123, 'start-123')
            journal.store_capture(123, 'start-123', 0, b'done\n', b'', True)
            self.assertEqual(journal.inspect()['state'], 'CONFIRMED_TERMINATED')
        with Journal(self.root) as journal:
            self.assertEqual(journal.inspect()['state'], 'IDLE')
            self.assertEqual(journal.accounting()['runs'][0]['state'], 'STORED')

    def test_unaccounted_root_staging_blocks_admission(self):
        (self.root / '.pending-unaccounted').write_bytes(b'partial')
        with self.assertRaises(JournalBlocked):
            with Journal(self.root) as journal:
                journal.reserve(identity('must-not-launch'))


if __name__ == '__main__':
    unittest.main()
