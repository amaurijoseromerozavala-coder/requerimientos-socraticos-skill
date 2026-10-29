"""Bounded private scratch lifecycle tests; kill only test-created processes."""
from contextlib import ExitStack
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from scratch_pool import workspace,ScratchError,SLOTS

class ScratchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.root=self.base/'pool'
    def tearDown(self):self.tmp.cleanup()
    def test_normal_exit_cleans_bundle(self):
        with workspace(root=self.root) as (bundle,fd):(bundle/'file').write_text('test')
        self.assertFalse(bundle.exists());self.assertTrue((bundle.parent/'.lease').is_file())
    def test_exception_cleans_bundle(self):
        with self.assertRaisesRegex(ValueError,'fixture'):
            with workspace(root=self.root) as (bundle,fd):
                (bundle/'file').write_text('test');raise ValueError('fixture')
        self.assertFalse(bundle.exists())
    def test_live_slot_never_deleted(self):
        with workspace(root=self.root,slots=1) as (bundle,fd):
            (bundle/'keep').write_text('active')
            with self.assertRaisesRegex(ScratchError,'SCRATCH_BUSY'):
                with workspace(root=self.root,slots=1,timeout=.03):self.fail('active slot reused')
            self.assertEqual((bundle/'keep').read_text(),'active')
    def test_pool_capacity_is_fixed(self):
        with ExitStack() as stack:
            bundles=[stack.enter_context(workspace(root=self.root))[0] for _ in range(SLOTS)]
            self.assertEqual(len(set(bundles)),SLOTS)
            with self.assertRaisesRegex(ScratchError,'SCRATCH_BUSY'):
                with workspace(root=self.root,timeout=.03):self.fail('unbounded extra slot')
            self.assertEqual(len(list(self.root.glob('slot-*'))),SLOTS)
    def test_foreign_namespace_not_touched(self):
        unrelated=self.base/'requirements-git-unrelated';unrelated.mkdir();(unrelated/'keep').write_text('keep')
        with workspace(root=self.root):pass
        self.assertEqual((unrelated/'keep').read_text(),'keep')
    def test_symlink_namespace_rejected(self):
        real=self.base/'real';real.mkdir();self.root.symlink_to(real)
        with self.assertRaisesRegex(ScratchError,'UNSAFE_SCRATCH_DIRECTORY'):
            with workspace(root=self.root):pass
        self.assertFalse(list(real.iterdir()))
    def test_open_namespace_rejected(self):
        self.root.mkdir(mode=0o700);self.root.chmod(0o777)
        with self.assertRaisesRegex(ScratchError,'UNSAFE_SCRATCH_DIRECTORY'):
            with workspace(root=self.root):pass
    def test_symlink_bundle_not_followed(self):
        with workspace(root=self.root) as (bundle,fd):pass
        outside=self.base/'outside';outside.mkdir();(outside/'keep').write_text('keep')
        bundle.symlink_to(outside,target_is_directory=True)
        with self.assertRaisesRegex(ScratchError,'UNSAFE_SCRATCH_BUNDLE'):
            with workspace(root=self.root):pass
        self.assertEqual((outside/'keep').read_text(),'keep')
    def test_hardlinked_lease_rejected(self):
        with workspace(root=self.root) as (bundle,fd):pass
        os.link(bundle.parent/'.lease',self.base/'alias')
        with self.assertRaisesRegex(ScratchError,'UNSAFE_SCRATCH_LEASE'):
            with workspace(root=self.root):pass
    def wait_marker(self,marker,process):
        deadline=time.monotonic()+5
        while not marker.exists():
            if process.poll() is not None or time.monotonic()>deadline:self.fail('test child did not reach checkpoint')
            time.sleep(.01)
    def worker(self,code,*args):
        return subprocess.Popen([sys.executable,'-B','-c',code,str(ROOT/'scripts'),str(self.root),*map(str,args)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    def test_sigkill_orphan_reclaimed_on_exclusive_reuse(self):
        marker=self.base/'ready'
        code="import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from scratch_pool import workspace;\nwith workspace(root=Path(sys.argv[2]),slots=1) as (p,fd):\n (p/'orphan').write_text('owned fixture');Path(sys.argv[3]).write_text(str(p));sys.stdin.read(1)"
        child=self.worker(code,marker)
        try:
            self.wait_marker(marker,child);bundle=Path(marker.read_text());child.kill();child.wait(timeout=3)
            self.assertTrue((bundle/'orphan').is_file())
            with workspace(root=self.root,slots=1) as (reused,fd):
                self.assertEqual(reused,bundle);self.assertFalse((reused/'orphan').exists())
            self.assertFalse(bundle.exists())
        finally:
            if child.poll() is None:child.kill();child.wait(timeout=3)
            child.stdin.close()
    def test_inherited_lease_protects_consumer_after_parent_sigkill(self):
        ready=self.base/'consumer-ready';stop=self.base/'stop'
        consumer="import sys,time;from pathlib import Path;Path(sys.argv[1]).write_text('ready');deadline=time.monotonic()+5;\nwhile not Path(sys.argv[2]).exists() and time.monotonic()<deadline:time.sleep(.01)"
        parent_code="import sys,subprocess;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from scratch_pool import workspace;\nwith workspace(root=Path(sys.argv[2]),slots=1) as (p,fd):\n (p/'keep').write_text('consumer data');subprocess.Popen([sys.executable,'-B','-c',sys.argv[5],sys.argv[3],sys.argv[4]],pass_fds=(fd,),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);sys.stdin.read(1)"
        parent=self.worker(parent_code,ready,stop,consumer)
        try:
            self.wait_marker(ready,parent);parent.kill();parent.wait(timeout=3)
            with self.assertRaisesRegex(ScratchError,'SCRATCH_BUSY'):
                with workspace(root=self.root,slots=1,timeout=.05):self.fail('live consumer deleted')
            self.assertEqual((self.root/'slot-0/bundle/keep').read_text(),'consumer data')
            stop.write_text('exit')
            with workspace(root=self.root,slots=1,timeout=3) as (bundle,fd):
                self.assertFalse((bundle/'keep').exists())
        finally:
            stop.touch()
            if parent.poll() is None:parent.kill();parent.wait(timeout=3)
            parent.stdin.close()
    def test_invalid_limits(self):
        with self.assertRaisesRegex(ScratchError,'INVALID_SCRATCH_LIMIT'):
            with workspace(root=self.root,slots=5):pass

if __name__=='__main__':unittest.main(verbosity=2)
