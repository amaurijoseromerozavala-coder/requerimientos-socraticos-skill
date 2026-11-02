"""Bounded integration checks for durable reservation around a real child."""
import os
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from supervisor.journal import Journal, JournalBlocked
from supervisor.process_core import ProcessSupervisor, Limits

IDENTITY = {'run_id': 'journal-link-test', 'boot_id': 'test-boot',
            'pid_namespace_identity': 'test-namespace', 'owner_uid': os.getuid(),
            'checker_manifest_digest': 'a' * 64, 'policy_digest': 'b' * 64}


class JournalProcessLinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='journal-process-link-')
        self.root = Path(self.temp.name) / 'journal'
        Journal.initialize(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def supervisor(self, journal, script='print("ok")', **limits):
        values = {'wall_seconds': 1, 'grace_seconds': .1, 'cleanup_seconds': .2}
        values.update(limits)
        return ProcessSupervisor(
            (sys.executable, '-B', '-c', script),
            Limits(**values),
            journal=journal, journal_identity=IDENTITY)

    def test_reserve_precedes_launch_and_terminal_record_blocks_reentry(self):
        with Journal(self.root) as journal:
            supervisor = self.supervisor(journal)
            original = subprocess.Popen
            launches = []

            def launch(*args, **kwargs):
                self.assertEqual(journal.inspect()['state'], 'RESERVED')
                child = original(*args, **kwargs)
                launches.append(child.pid)
                return child

            with patch('supervisor.process_core.subprocess.Popen', side_effect=launch):
                result = supervisor.run()
                second = supervisor.run()
            state = journal.inspect()
            self.assertEqual(result['returncode'], 0)
            self.assertEqual(result['cleanup'], 'CONFIRMED')
            self.assertEqual(result['status'], 'JOURNAL_RECONCILIATION_REQUIRED')
            self.assertEqual(result['stdout'], b'ok\n')
            self.assertEqual(state['state'], 'CONFIRMED_TERMINATED')
            self.assertEqual(state['identity']['pid'], launches[0])
            self.assertTrue(state['identity']['process_start_identity'].isdigit())
            self.assertEqual(second['status'], 'INFRA_LOCK')
            self.assertEqual(len(launches), 1)

    def test_unavailable_journal_rejects_before_launch(self):
        closed = Journal(self.root)
        supervisor = self.supervisor(closed)
        with patch('supervisor.process_core.subprocess.Popen') as launch:
            result = supervisor.run()
        launch.assert_not_called()
        self.assertEqual(result['status'], 'INFRA_LOCK')
        with Journal(self.root) as journal:
            self.assertEqual(journal.inspect()['state'], 'IDLE')

    def test_half_configured_journal_is_rejected(self):
        command = (sys.executable, '-B', '-c', 'pass')
        with self.assertRaises(ValueError):
            ProcessSupervisor(command, journal=Journal(self.root))
        with self.assertRaises(ValueError):
            ProcessSupervisor(command, journal_identity=IDENTITY)

    def test_launch_failure_after_reservation_remains_blocked(self):
        with Journal(self.root) as journal:
            supervisor = self.supervisor(journal)
            with patch('supervisor.process_core.subprocess.Popen',
                       side_effect=OSError('controlled launch failure')) as launch:
                result = supervisor.run()
            self.assertEqual(launch.call_count, 1)
            self.assertEqual(result['status'], 'INFRA_LOCK')
            self.assertFalse(result['launched'])
            self.assertEqual(journal.inspect()['state'], 'RESERVED')

    def test_owner_exit_after_reserve_before_spawn_preserves_block(self):
        code = '''import json,os,sys
from unittest.mock import patch
from supervisor.journal import Journal
from supervisor.process_core import ProcessSupervisor,Limits
with Journal(sys.argv[1]) as journal:
    supervisor=ProcessSupervisor((sys.executable,'-B','-c','print("never")'),
        Limits(),journal=journal,journal_identity=json.loads(sys.argv[2]))
    with patch('supervisor.process_core.subprocess.Popen',side_effect=lambda *_a,**_kw:os._exit(27)):
        supervisor.run()
'''
        run = subprocess.run([sys.executable, '-B', '-c', code, str(self.root),
                              json.dumps(IDENTITY)], cwd=ROOT,
                             capture_output=True, timeout=5)
        self.assertEqual(run.returncode, 27, run.stderr)
        with Journal(self.root) as journal:
            self.assertEqual(journal.inspect()['state'], 'RESERVED')
            with self.assertRaises(JournalBlocked):
                journal.reserve(IDENTITY)

    def test_active_persistence_failure_cleans_child_and_keeps_reservation(self):
        with Journal(self.root) as journal:
            supervisor = self.supervisor(journal, script='import time; time.sleep(2)')
            with patch.object(journal, 'record_active',
                              side_effect=JournalBlocked('controlled write failure')):
                result = supervisor.run()
            self.assertEqual(result['status'], 'INFRA_LOCK')
            self.assertTrue(result['launched'])
            self.assertIsNotNone(result['returncode'])
            self.assertEqual(journal.inspect()['state'], 'RESERVED')

    def test_stop_persistence_failure_still_reaps_and_blocks(self):
        with Journal(self.root) as journal:
            supervisor = self.supervisor(journal, script='import time; time.sleep(2)',
                                         wall_seconds=.2)
            with patch.object(journal, 'record_stopping',
                              side_effect=JournalBlocked('controlled write failure')):
                result = supervisor.run()
            self.assertEqual(result['status'], 'INFRA_LOCK')
            self.assertIsNotNone(result['returncode'])
            self.assertEqual(journal.inspect()['state'], 'ACTIVE')

    def test_identity_failure_after_spawn_retains_reserved(self):
        with Journal(self.root) as journal:
            supervisor = self.supervisor(journal, script='import time; time.sleep(1)')
            with patch.object(supervisor, '_read_start_identity', side_effect=OSError('controlled proc failure')):
                result = supervisor.run()
            self.assertEqual(result['status'], 'INFRA_LOCK')
            self.assertEqual(journal.inspect()['state'], 'RESERVED')
            self.assertEqual(supervisor.run()['status'], 'INFRA_LOCK')
        with Journal(self.root) as journal:
            with self.assertRaises(JournalBlocked):
                journal.reserve(IDENTITY)

    def test_stop_recorded_before_signal_and_termination_confirmed(self):
        with Journal(self.root) as journal:
            supervisor = self.supervisor(journal, script='import time; time.sleep(2)',
                                         wall_seconds=.2)
            original = supervisor._signal_owned_group

            def signal_group(child, requested_signal):
                self.assertEqual(journal.inspect()['state'], 'STOPPING')
                return original(child, requested_signal)

            with patch.object(supervisor, '_signal_owned_group', side_effect=signal_group):
                result = supervisor.run()
            self.assertEqual(result['stop_reason'], 'WALL_DEADLINE')
            self.assertEqual(result['status'], 'JOURNAL_RECONCILIATION_REQUIRED')
            self.assertEqual(journal.inspect()['state'], 'CONFIRMED_TERMINATED')

    def test_terminal_transition_requires_matching_active_identity(self):
        with Journal(self.root) as journal:
            journal.reserve(IDENTITY)
            with self.assertRaises(JournalBlocked):
                journal.record_terminated(123, 'start-123')
            journal.record_active(123, 'start-123')
            with self.assertRaises(JournalBlocked):
                journal.record_terminated(124, 'start-123')
            with self.assertRaises(JournalBlocked):
                journal.record_terminated(123, 'different')
            journal.record_terminated(123, 'start-123')
            self.assertEqual(journal.inspect()['state'], 'CONFIRMED_TERMINATED')
            with self.assertRaises(JournalBlocked):
                journal.reserve(IDENTITY)
        with Journal(self.root) as journal:
            self.assertEqual(journal.inspect()['state'], 'CONFIRMED_TERMINATED')
            with self.assertRaises(JournalBlocked):
                journal.reserve(IDENTITY)

    def test_readme_keeps_link_and_reconciliation_boundary_explicit(self):
        text = (ROOT / 'README.md').read_text()
        self.assertIn('enlace optativo', text)
        self.assertIn('CONFIRMED_TERMINATED', text)
        self.assertIn('sin integración QA', text)


if __name__ == '__main__':
    unittest.main()
