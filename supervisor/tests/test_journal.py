import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from supervisor.journal import Journal, JournalBlocked

IDENTITY={'run_id':'test-run','boot_id':'test-boot','pid_namespace_identity':'test-ns',
          'owner_uid':os.getuid(),'checker_manifest_digest':'a'*64,'policy_digest':'b'*64}

class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)/'journal'
        Journal.initialize(self.root)
    def tearDown(self): self.temp.cleanup()
    def test_initialization_never_overwrites(self):
        with self.assertRaises(FileExistsError): Journal.initialize(self.root)
    def test_reservation_persists_no_reentry(self):
        with Journal(self.root) as journal:
            self.assertEqual(journal.inspect()['state'],'IDLE')
            journal.reserve(IDENTITY)
            self.assertEqual(journal.inspect()['state'],'RESERVED')
            with self.assertRaises(JournalBlocked): journal.reserve(IDENTITY)
        with Journal(self.root) as journal:
            with self.assertRaises(JournalBlocked): journal.reserve(IDENTITY)
    def test_missing_and_corrupt_state_block(self):
        for value in (None,b'{bad',b'{}',b'x'*17000):
            with self.subTest(value_type=type(value).__name__):
                path=self.root/'state.json'
                if value is None: path.unlink()
                else: path.write_bytes(value)
                with self.assertRaises(JournalBlocked):
                    with Journal(self.root) as journal: journal.inspect()
    def test_cooperative_exclusion(self):
        with Journal(self.root):
            with self.assertRaises(JournalBlocked):
                with Journal(self.root): pass
    def test_symlink_state_rejected(self):
        (self.root/'state.json').unlink()
        (self.root/'state.json').symlink_to('/dev/null')
        with self.assertRaises(JournalBlocked):
            with Journal(self.root): pass
    def test_reservation_survives_abrupt_owner_exit(self):
        script='from supervisor.journal import Journal; import os,json,sys; j=Journal(sys.argv[1]); j.__enter__(); j.reserve(json.loads(sys.argv[2])); os._exit(0)'
        run=subprocess.run([sys.executable,'-B','-c',script,str(self.root),json.dumps(IDENTITY)],capture_output=True,timeout=5)
        self.assertEqual(run.returncode,0,run.stderr)
        with Journal(self.root) as journal:
            self.assertEqual(journal.inspect()['state'],'RESERVED')
            with self.assertRaises(JournalBlocked): journal.reserve(IDENTITY)
    def test_write_failure_latches_instance(self):
        with Journal(self.root) as journal:
            with patch('supervisor.journal.os.fsync',side_effect=OSError('controlled failure')):
                with self.assertRaises(JournalBlocked): journal.reserve(IDENTITY)
            with self.assertRaises(JournalBlocked): journal.reserve(IDENTITY)
    def test_directory_sync_failure_leaves_reservation_blocked(self):
        real_sync=os.fsync
        def sync(fd):
            import stat
            if stat.S_ISDIR(os.fstat(fd).st_mode): raise OSError('controlled directory sync failure')
            return real_sync(fd)
        with Journal(self.root) as journal:
            with patch('supervisor.journal.os.fsync',side_effect=sync):
                with self.assertRaises(JournalBlocked): journal.reserve(IDENTITY)
        with Journal(self.root) as journal:
            self.assertEqual(journal.inspect()['state'],'IDLE')
            self.assertEqual(journal.accounting()['runs'][0]['state'],'RESERVED')
            with self.assertRaises(JournalBlocked): journal.reserve(IDENTITY)
    def test_missing_lock_never_recreated(self):
        (self.root/'owner.lock').unlink()
        with self.assertRaises(JournalBlocked):
            with Journal(self.root): pass
        self.assertFalse((self.root/'owner.lock').exists())
    def test_invalid_identity_cannot_reserve(self):
        with Journal(self.root) as journal:
            with self.assertRaises(JournalBlocked): journal.reserve({})
    def test_busy_reservation_does_not_write(self):
        with Journal(self.root) as journal:
            with journal._operation:
                with self.assertRaises(JournalBlocked): journal.reserve(IDENTITY)
            self.assertEqual(journal.inspect()['state'],'IDLE')
    def test_persistence_and_cleanup_errors_preserve_primary_cause(self):
        primary=OSError(5, 'controlled persistence failure')
        secondary=OSError(30, 'controlled cleanup failure')
        with Journal(self.root) as journal:
            with patch('supervisor.journal.os.fsync',side_effect=primary), patch('supervisor.journal.os.unlink',side_effect=secondary):
                with self.assertRaises(JournalBlocked) as caught:
                    journal.reserve(IDENTITY)
            self.assertEqual(str(caught.exception),'RESERVATION_NOT_CONFIRMED')
            self.assertIs(caught.exception.__cause__,primary)
            self.assertTrue(any('CLEANUP_FAILED' in note for note in caught.exception.__notes__))
            with self.assertRaises(JournalBlocked): journal.reserve(IDENTITY)
    def test_invalid_records_rejected_without_rewrite(self):
        base={'schema_version':'reservation-journal/v1','state':'IDLE','identity':None}
        records=[
            b'{"schema_version":"reservation-journal/v1","state":"RESERVED","state":"IDLE","identity":null}',
            json.dumps(dict(base,schema_version='unknown/v99')).encode(),
            json.dumps(dict(base,state='RESERVED')).encode(),
            json.dumps(dict(base,identity=IDENTITY)).encode(),
            json.dumps(dict(base,state='UNKNOWN')).encode(),
        ]
        for raw in records:
            with self.subTest(raw=raw):
                path=self.root/'state.json';path.write_bytes(raw)
                with self.assertRaises(JournalBlocked, msg='INVALID_RECORD_MUST_BLOCK'):
                    with Journal(self.root): pass
                self.assertEqual(path.read_bytes(),raw)
    def test_no_implicit_initialize(self):
        with self.assertRaises(JournalBlocked):
            with Journal(self.root/'absent'): pass

if __name__=='__main__': unittest.main()
