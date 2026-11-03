import os
from pathlib import Path
import tempfile
import unittest

from supervisor.rs3_audit_log import AuditBlocked, AuditLog


class AuditLogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'audit'
        self.event = {'kind': 'PROPOSAL_RECORDED', 'ref': 'RS3-001',
                      'subject_sha256': 'a' * 64}

    def test_persists_documentary_event_without_authority_claim(self):
        AuditLog.initialize(self.root)
        log = AuditLog(self.root, max_bytes=4096)
        record = log.append(self.event)
        self.assertEqual(record['sequence'], 1)
        self.assertEqual(record['authority_verification'], 'NOT_PERFORMED')
        self.assertIs(record['execution_authorized'], False)
        self.assertEqual(AuditLog(self.root, max_bytes=4096).read_all(), [record])

    def test_authority_event_and_extra_fields_are_rejected(self):
        AuditLog.initialize(self.root)
        log = AuditLog(self.root)
        for event in ({**self.event, 'kind': 'HUMAN_CONFIRMED'},
                      {**self.event, 'secret': 'synthetic-only'},
                      {**self.event, 'kind': []}):
            with self.assertRaises(AuditBlocked):
                log.append(event)
        self.assertEqual(log.read_all(), [])

    def test_corruption_blocks_append_and_read(self):
        AuditLog.initialize(self.root)
        log = AuditLog(self.root)
        log.append(self.event)
        data = (self.root / 'events.jsonl').read_bytes()
        (self.root / 'events.jsonl').write_bytes(data[:-2])
        with self.assertRaises(AuditBlocked):
            log.read_all()
        with self.assertRaises(AuditBlocked):
            log.append(self.event)

    def test_capacity_and_private_path(self):
        AuditLog.initialize(self.root)
        log = AuditLog(self.root, max_bytes=1)
        with self.assertRaises(AuditBlocked):
            log.append(self.event)
        os.chmod(self.root, 0o755)
        with self.assertRaises(AuditBlocked):
            log.read_all()

    def test_digest_mismatch_blocks_further_use(self):
        AuditLog.initialize(self.root)
        log = AuditLog(self.root)
        log.append(self.event)
        path = self.root / 'events.jsonl'
        raw = path.read_bytes().replace(b'RS3-001', b'RS3-002')
        path.write_bytes(raw)
        with self.assertRaises(AuditBlocked):
            log.read_all()
        with self.assertRaises(AuditBlocked):
            log.append(self.event)

    def test_symlink_file_is_rejected(self):
        AuditLog.initialize(self.root)
        path = self.root / 'events.jsonl'
        path.unlink()
        path.symlink_to(Path(self.tmp.name) / 'other')
        with self.assertRaises(AuditBlocked):
            AuditLog(self.root).append(self.event)

    def test_complete_tail_removal_is_unobservable_without_checkpoint(self):
        AuditLog.initialize(self.root)
        log = AuditLog(self.root)
        first = log.append(self.event)
        log.append({**self.event, 'ref': 'RS3-002'})
        (self.root / 'events.jsonl').write_bytes(
            (self.root / 'events.jsonl').read_bytes().splitlines(keepends=True)[0])
        self.assertEqual(log.read_all(), [first])
        self.assertEqual(log.read_all()[0]['authority_verification'], 'NOT_PERFORMED')


if __name__ == '__main__':
    unittest.main()
