import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import contextlib
import io

from supervisor.rs3_password_auditor import PasswordAuditBlocked, PasswordAuditor
from supervisor.rs3_password_cli import main, run_enroll


class AuthorityUidGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'authority'
        self.password = 'synthetic-password-only-12345'

    def test_same_uid_enrollment_is_rejected_without_store(self):
        with self.assertRaises(PasswordAuditBlocked):
            PasswordAuditor.initialize(self.root, self.password, agent_uid=os.getuid())
        self.assertFalse(self.root.exists())

    def test_verifier_binds_distinct_agent_and_authority_uid(self):
        PasswordAuditor.initialize(self.root, self.password, agent_uid=os.getuid() + 1)
        doc = json.loads((self.root / 'verifier.json').read_text())
        self.assertEqual(doc['authority_uid'], os.getuid())
        self.assertEqual(doc['agent_uid'], os.getuid() + 1)
        with mock.patch('supervisor.rs3_password_auditor.os.getuid', return_value=os.getuid() + 2):
            with self.assertRaises(PasswordAuditBlocked):
                PasswordAuditor(self.root).check(
                    proposal_id='P-001', snapshot_sha256='a' * 64,
                    decision_text='Acepto revisar P-001.', nonce='1' * 32,
                    confirmation_kind='SEMANTIC_ACCEPTANCE',
                    password=self.password)

    def test_manual_enroll_requires_distinct_agent_uid(self):
        with (mock.patch('supervisor.rs3_password_cli._open_tty', return_value=20),
              mock.patch('supervisor.rs3_password_cli._close_tty'),
              mock.patch('supervisor.rs3_password_cli._read_secret',
                         side_effect=[self.password, self.password])):
            with self.assertRaises(PasswordAuditBlocked):
                run_enroll(self.root, agent_uid=os.getuid())
        self.assertFalse(self.root.exists())

    def test_effective_uid_mismatch_and_missing_cli_uid_block(self):
        with mock.patch('supervisor.rs3_password_auditor.os.geteuid', return_value=os.getuid() + 2):
            with self.assertRaises(PasswordAuditBlocked):
                PasswordAuditor.initialize(self.root, self.password,
                                           agent_uid=os.getuid() + 1)
        self.assertFalse(self.root.exists())
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                main(['enroll', '--root', str(self.root)])
        self.assertEqual(result.exception.code, 2)
        self.assertFalse(self.root.exists())


if __name__ == '__main__':
    unittest.main()
