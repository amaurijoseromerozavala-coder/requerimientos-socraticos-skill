import os
from pathlib import Path
import tempfile
import unittest
from supervisor.journal import Journal, JournalBlocked

IDENTITY={'run_id':'run-one','boot_id':'boot-one','pid_namespace_identity':'namespace-one',
          'owner_uid':os.getuid(),'checker_manifest_digest':'a'*64,'policy_digest':'b'*64}

class TransitionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'journal'
        Journal.initialize(self.root)
    def tearDown(self):self.temp.cleanup()
    def test_active_requires_reserved_and_complete_identity(self):
        with Journal(self.root) as j:
            with self.assertRaises(JournalBlocked): j.record_active(123,'start-123')
            j.reserve(IDENTITY)
            for pid,start in ((0,'start'),(-1,'start'),(123,''),(123,None)):
                with self.subTest(pid=pid,start=start),self.assertRaises(JournalBlocked):
                    j.record_active(pid,start)
            self.assertEqual(j.inspect()['state'],'RESERVED')
            j.record_active(123,'start-123')
            self.assertEqual(j.inspect()['state'],'ACTIVE')
            self.assertEqual(j.inspect()['identity']['pid'],123)
            self.assertEqual(j.inspect()['identity']['process_start_identity'],'start-123')
    def test_reopen_active_blocks_new_reservation(self):
        with Journal(self.root) as j:
            j.reserve(IDENTITY);j.record_active(123,'start-123')
        with Journal(self.root) as j:
            self.assertEqual(j.inspect()['state'],'ACTIVE')
            with self.assertRaises(JournalBlocked):j.reserve(IDENTITY)
    def test_stop_requires_active_and_retains_identity(self):
        with Journal(self.root) as j:
            j.reserve(IDENTITY)
            with self.assertRaises(JournalBlocked):j.record_stopping()
            j.record_active(123,'start-123');j.record_stopping()
            state=j.inspect()
            self.assertEqual(state['state'],'STOPPING')
            self.assertEqual(state['identity']['pid'],123)
            with self.assertRaises(JournalBlocked):j.record_stopping()
        with Journal(self.root) as j:
            self.assertEqual(j.inspect()['state'],'STOPPING')
            with self.assertRaises(JournalBlocked):j.reserve(IDENTITY)

if __name__=='__main__':unittest.main()
