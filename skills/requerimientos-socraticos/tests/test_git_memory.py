"""Integration against tiny, synthetic Git documentation commits."""
from pathlib import Path
import sys
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import validate_git
import git_validation_engine
import test_sealed


class GitMemoryTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_sealed.SealedTests('test_sha256_git_objects')
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.commit = self.fixture.stage()

    def test_no_candidate_scratch_and_original_status_preserved(self):
        with patch.object(validate_git, 'workspace', create=True,
                          side_effect=AssertionError('Git must not materialize candidate files')):
            result = validate_git.validate_commit(self.fixture.repo, self.commit, 'prd.json')
        self.assertEqual(result['status'], 'DOCUMENT_VALIDATED_GIT')
        self.assertEqual(result['advance'], 'BLOCKED_GLOBAL_ENFORCEMENT')
        self.assertEqual(result['document_transport'], 'VERIFIED_BYTES_STDIN')
        self.assertTrue(result['consumed_files'])
        manifest = {entry['path']: entry for entry in result['files']}
        for consumed in result['consumed_files']:
            self.assertEqual(consumed, manifest[consumed['path']])

    def test_git_and_document_worker_use_shared_supervision(self):
        # This is a wiring test of the internal coordinator; public budget
        # enforcement is exercised separately in test_validation_budget.
        with patch.object(git_validation_engine, 'run_supervised', wraps=git_validation_engine.run_supervised) as run:
            git_validation_engine.validate_local(self.fixture.repo, self.commit, 'prd.json')
        self.assertGreater(len(run.call_args_list), 1)
        self.assertTrue(any(call.kwargs.get('input_data') for call in run.call_args_list))
        self.assertTrue(any(call.kwargs.get('env') for call in run.call_args_list))

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux direct-child lifecycle')
    def test_git_consumer_stops_after_parent_termination(self):
        # Adoption/reaping is confined to a separate, owned fixture harness.
        code = r'''
import ctypes,json,os,signal,subprocess,sys,tempfile,time
from pathlib import Path
libc=ctypes.CDLL(None)
if libc.prctl(36,1,0,0,0)!=0:
 print(json.dumps({'supported':False}));raise SystemExit(0)
parent=None;worker=None;reaped=False
with tempfile.TemporaryDirectory() as temporary:
 marker=Path(temporary)/'ready'
 child='import os,time;from pathlib import Path;Path('+repr(str(marker))+').write_text(str(os.getpid()));time.sleep(5)'
 program=''' + '"""' + r'''
import sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import git_validation_engine as validate_git
original=validate_git.run_supervised
def controlled_consumer(command, timeout, **kwargs):
 if command[-1].endswith('git_document_worker.py'):
  command=[sys.executable,'-c',sys.argv[4]]
 return original(command,timeout,**kwargs)
validate_git.run_supervised=controlled_consumer
validate_git.validate_local(Path(sys.argv[2]),sys.argv[3],'prd.json',5)
''' + '"""' + r'''
 try:
  parent=subprocess.Popen([sys.executable,'-B','-c',program,sys.argv[1],sys.argv[2],sys.argv[3],child],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  deadline=time.monotonic()+3
  while not marker.exists() and time.monotonic()<deadline:
   if parent.poll() is not None:raise RuntimeError('parent exited before checkpoint')
   time.sleep(.01)
  if not marker.exists():raise RuntimeError('consumer checkpoint missing')
  worker=int(marker.read_text());parent.kill();parent.wait(timeout=2)
  deadline=time.monotonic()+2
  while time.monotonic()<deadline:
   pid,status=os.waitpid(worker,os.WNOHANG)
   if pid:
    reaped=True
    print(json.dumps({'supported':True,'terminated':os.WIFSIGNALED(status) and os.WTERMSIG(status)==signal.SIGKILL}));break
   time.sleep(.01)
  if not reaped:raise RuntimeError('consumer did not terminate')
 finally:
  if parent is not None and parent.poll() is None:parent.kill();parent.wait(timeout=2)
  if worker is not None and not reaped:
   try:os.kill(worker,signal.SIGKILL);os.waitpid(worker,0)
   except (ProcessLookupError,ChildProcessError):pass
'''
        result = subprocess.run([sys.executable, '-B', '-c', code, str(ROOT/'scripts'),
                                 str(self.fixture.repo), self.commit], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        import json
        record = json.loads(result.stdout)
        if not record['supported']:
            self.skipTest('owned harness cannot establish child subreaping')
        self.assertTrue(record['terminated'])


if __name__ == '__main__':
    unittest.main()
