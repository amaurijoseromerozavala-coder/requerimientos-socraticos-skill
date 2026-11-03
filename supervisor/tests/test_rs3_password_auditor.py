import os
from pathlib import Path
import tempfile
import unittest

from supervisor.rs3_password_auditor import PasswordAuditBlocked, PasswordAuditor


class PasswordAuditorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'authority'
        self.password = 'synthetic-password-only-12345'
        self.decision = dict(proposal_id='P-001', snapshot_sha256='a' * 64,
                             decision_text='Acepto revisar P-001.', nonce='1' * 32)

    def test_correct_and_wrong_password_are_logged_without_secret(self):
        PasswordAuditor.initialize(self.root, self.password, agent_uid=os.getuid() + 1)
        backend = PasswordAuditor(self.root)
        bad = backend.check(**self.decision, password='synthetic-wrong-value-123')
        good = backend.check(**{**self.decision, 'nonce': '2' * 32},
                             password=self.password)
        self.assertIs(bad['credential_match'], False)
        self.assertIs(good['credential_match'], True)
        self.assertEqual(good['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(good['execution_authorized'], False)
        self.assertEqual([row['event']['kind'] for row in backend.audit_events()],
                         ['PASSWORD_CHECK_REJECTED', 'PASSWORD_CHECK_ACCEPTED'])
        on_disk = (self.root / 'events.jsonl').read_text()
        self.assertNotIn(self.password, on_disk)
        self.assertNotIn(self.decision['decision_text'], on_disk)
        self.assertNotIn(self.password, (self.root / 'verifier.json').read_text())

    def test_reused_nonce_never_upgrades_failed_attempt(self):
        PasswordAuditor.initialize(self.root, self.password, agent_uid=os.getuid() + 1)
        backend = PasswordAuditor(self.root)
        backend.check(**self.decision, password='synthetic-wrong-value-123')
        with self.assertRaises(PasswordAuditBlocked):
            backend.check(**self.decision, password=self.password)
        self.assertEqual(len(backend.audit_events()), 1)

    def test_decision_digest_changes_with_text_or_snapshot(self):
        PasswordAuditor.initialize(self.root, self.password, agent_uid=os.getuid() + 1)
        backend = PasswordAuditor(self.root)
        first = backend.check(**self.decision, password=self.password)
        second = backend.check(**{**self.decision, 'nonce': '2' * 32,
                                  'decision_text': 'Rechazo P-001.'}, password=self.password)
        third = backend.check(**{**self.decision, 'nonce': '3' * 32,
                                 'snapshot_sha256': 'b' * 64}, password=self.password)
        self.assertNotEqual(first['subject_sha256'], second['subject_sha256'])
        self.assertNotEqual(first['subject_sha256'], third['subject_sha256'])

    def test_private_store_and_failed_log_write_block_check(self):
        PasswordAuditor.initialize(self.root, self.password, agent_uid=os.getuid() + 1)
        self.assertEqual((self.root / 'verifier.json').stat().st_mode & 0o777, 0o600)
        os.chmod(self.root / 'events.jsonl', 0o644)
        with self.assertRaises(PasswordAuditBlocked):
            PasswordAuditor(self.root).check(**self.decision, password=self.password)

    def test_invalid_enrollment_and_corrupt_verifier_fail_closed(self):
        with self.assertRaises(PasswordAuditBlocked):
            PasswordAuditor.initialize(self.root, 'short', agent_uid=os.getuid() + 1)
        PasswordAuditor.initialize(self.root, self.password, agent_uid=os.getuid() + 1)
        (self.root / 'verifier.json').write_text('{}')
        with self.assertRaises(PasswordAuditBlocked):
            PasswordAuditor(self.root).check(**self.decision, password=self.password)

    def test_verifier_symlink_and_duplicate_nonce_are_rejected(self):
        PasswordAuditor.initialize(self.root, self.password, agent_uid=os.getuid() + 1)
        backend = PasswordAuditor(self.root)
        backend.check(**self.decision, password=self.password)
        with self.assertRaises(PasswordAuditBlocked):
            backend.check(**self.decision, password=self.password)
        verifier = self.root / 'verifier.json'
        other = Path(self.tmp.name) / 'other.json'
        verifier.rename(other)
        verifier.symlink_to(other)
        with self.assertRaises(PasswordAuditBlocked):
            backend.check(**{**self.decision, 'nonce': '2' * 32}, password=self.password)

    def test_bounded_audit_failure_does_not_return_match(self):
        PasswordAuditor.initialize(self.root, self.password, agent_uid=os.getuid() + 1)
        (self.root / 'events.jsonl').write_bytes(b'x' * (1024 * 1024 + 1))
        with self.assertRaises(PasswordAuditBlocked):
            PasswordAuditor(self.root).check(**self.decision, password=self.password)


if __name__ == '__main__':
    unittest.main()
