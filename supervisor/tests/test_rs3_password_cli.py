import json
import os
from pathlib import Path
import pty
import tempfile
import termios
import threading
import unittest
from unittest import mock

from supervisor.rs3_password_auditor import PasswordAuditor
from supervisor.rs3_password_cli import ManualChannelBlocked, _read_secret, load_decision, run_check, run_enroll


class ManualPasswordChannelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'authority'
        self.password = 'synthetic-password-only-12345'
        PasswordAuditor.initialize(self.root, self.password, agent_uid=os.getuid() + 1)
        self.path = Path(self.tmp.name) / 'decision.json'
        self.doc = {'schema': 'rs3-manual-decision/v2', 'proposal_id': 'P-001',
                    'snapshot_sha256': 'a' * 64, 'decision_text': 'Acepto revisar P-001.',
                    'confirmation_kind': 'SEMANTIC_ACCEPTANCE'}
        self.path.write_text(json.dumps(self.doc), encoding='utf-8')

    def test_decision_file_rejects_ambiguous_or_nonregular_input(self):
        self.path.write_text('{"schema":"rs3-manual-decision/v2","schema":"x"}')
        with self.assertRaises(ManualChannelBlocked):
            load_decision(self.path)
        self.path.write_bytes(b'x' * 8193)
        with self.assertRaises(ManualChannelBlocked):
            load_decision(self.path)
        self.path.unlink()
        self.path.symlink_to(Path(self.tmp.name) / 'other')
        with self.assertRaises(ManualChannelBlocked):
            load_decision(self.path)

    def test_manual_file_requires_v2_confirmation_kind(self):
        self.path.write_text(json.dumps({**self.doc, 'schema': 'rs3-manual-decision/v1'}),
                             encoding='utf-8')
        with self.assertRaises(ManualChannelBlocked):
            load_decision(self.path)
        new_doc = {**self.doc, 'schema': 'rs3-manual-decision/v2',
                   'confirmation_kind': 'SEMANTIC_ACCEPTANCE'}
        self.path.write_text(json.dumps(new_doc), encoding='utf-8')
        self.assertEqual(load_decision(self.path)['confirmation_kind'],
                         'SEMANTIC_ACCEPTANCE')
        for invalid in ({key: value for key, value in new_doc.items()
                         if key != 'confirmation_kind'},
                        {**new_doc, 'confirmation_kind': 'UNKNOWN'}):
            with self.subTest(invalid=invalid):
                self.path.write_text(json.dumps(invalid), encoding='utf-8')
                with self.assertRaises(ManualChannelBlocked):
                    load_decision(self.path)

    def test_no_terminal_blocks_before_password_check(self):
        with mock.patch('supervisor.rs3_password_cli._open_tty',
                        side_effect=ManualChannelBlocked('TTY_REQUIRED')):
            with self.assertRaises(ManualChannelBlocked):
                run_check(self.root, self.path)
        self.assertEqual(PasswordAuditor(self.root).audit_events(), [])

    def test_displayed_snapshot_is_the_checked_snapshot(self):
        shown = []
        original_text = self.doc['decision_text']
        def change_file_after_display(fd):
            self.path.write_text(json.dumps({**self.doc, 'decision_text': 'Rechazo P-001.'}))
            return self.password
        with (mock.patch('supervisor.rs3_password_cli._open_tty', return_value=20),
              mock.patch('supervisor.rs3_password_cli._close_tty'),
              mock.patch('supervisor.rs3_password_cli._write_tty', side_effect=lambda fd, raw: shown.append(raw)),
              mock.patch('supervisor.rs3_password_cli._read_secret', side_effect=change_file_after_display)):
            result = run_check(self.root, self.path)
        self.assertIs(result['credential_match'], True)
        self.assertIs(result['execution_authorized'], False)
        self.assertIn(original_text.encode(), b''.join(shown))
        self.assertIn(self.doc['snapshot_sha256'].encode(), b''.join(shown))
        self.assertNotIn(self.password.encode(), b''.join(shown))
        self.assertEqual(len(PasswordAuditor(self.root).audit_events()), 1)

    def test_terminal_entry_disables_echo_and_restores_mode(self):
        master, slave = pty.openpty()
        self.addCleanup(os.close, master)
        self.addCleanup(os.close, slave)
        before = termios.tcgetattr(slave)
        result = []
        thread = threading.Thread(target=lambda: result.append(_read_secret(slave, b'Password: ')),
                                  daemon=True)
        thread.start()
        import select
        self.assertTrue(select.select([master], [], [], 2)[0])
        prompt = os.read(master, 1024)
        os.write(master, b'synthetic-secret\n')
        thread.join(2)
        self.assertFalse(thread.is_alive())
        self.assertEqual(result, ['synthetic-secret'])
        self.assertEqual(termios.tcgetattr(slave), before)
        remaining = os.read(master, 1024)
        self.assertNotIn(b'synthetic-secret', prompt + remaining)

    def test_unicode_password_enrollment_matches_and_mismatch_blocks(self):
        values = ['contraseña-sintética-larga', 'contraseña-sintética-larga']
        with (mock.patch('supervisor.rs3_password_cli._open_tty', return_value=20),
              mock.patch('supervisor.rs3_password_cli._close_tty'),
              mock.patch('supervisor.rs3_password_cli._read_secret', side_effect=values)):
            result = run_enroll(Path(self.tmp.name) / 'unicode-store', agent_uid=os.getuid() + 1)
        self.assertEqual(result['status'], 'ENROLLED')
        values = ['contraseña-sintética-larga', 'contraseña-distinta-larga']
        with (mock.patch('supervisor.rs3_password_cli._open_tty', return_value=20),
              mock.patch('supervisor.rs3_password_cli._close_tty'),
              mock.patch('supervisor.rs3_password_cli._read_secret', side_effect=values)):
            with self.assertRaises(ManualChannelBlocked):
                run_enroll(Path(self.tmp.name) / 'mismatch-store', agent_uid=os.getuid() + 1)


if __name__ == '__main__':
    unittest.main()
