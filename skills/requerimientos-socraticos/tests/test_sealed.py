"""Synthetic temporary repositories and bounded negative controls; never real approvals."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
from safe_io import canonical_lf,read_regular
from validate_git import validate_commit,InvalidGit
import test_interview

class SealedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.repo=self.base/'repo';self.repo.mkdir()
    def tearDown(self):self.tmp.cleanup()
    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.repo),*args],stderr=subprocess.DEVNULL).decode().strip()
    def stage(self,algorithm='sha256'):
        self.git('init','-q','--object-format='+algorithm)
        test_interview.ContractTests().stage_prd(self.repo)
        self.git('add','.')
        self.git('-c','user.name=Fixture','-c','user.email=fixture@invalid','commit','--no-gpg-sign','-qm','Synthetic bounded fixture')
        return self.git('rev-parse','HEAD')
    def cli(self,script,*args):
        return subprocess.run([sys.executable,'-B',str(ROOT/'scripts'/script),*map(str,args)],capture_output=True,text=True,timeout=10)
    def test_direct_fifo_rejected_without_waiting(self):
        path=self.repo/'prd.json';os.mkfifo(path)
        p=self.cli('validate_prd.py',path)
        self.assertEqual(p.returncode,1);self.assertIn('NOT_REGULAR_FILE',p.stdout)
    def test_external_symlink_rejected(self):
        (self.repo/'alias').symlink_to('/dev/zero')
        with self.assertRaises(OSError):read_regular(self.repo,'alias')
    def test_component_symlink_rejected(self):
        elsewhere=self.base/'outside';elsewhere.mkdir();(elsewhere/'a').write_text('secret fixture')
        (self.repo/'alias').symlink_to(elsewhere,target_is_directory=True)
        with self.assertRaises(OSError):read_regular(self.repo,'alias/a')
    def test_regular_limit(self):
        (self.repo/'a').write_bytes(b'1234')
        with self.assertRaisesRegex(ValueError,'FILE_SIZE_LIMIT'):read_regular(self.repo,'a',limit=3)
    def test_device_rejected_without_reading(self):
        with self.assertRaisesRegex(ValueError,'NOT_REGULAR_FILE'):read_regular(Path('/dev'),'zero')
    def test_traversal_rejected(self):
        with self.assertRaisesRegex(ValueError,'UNSAFE_PATH'):read_regular(self.repo,'../outside')
    def test_utf8_lf_normalization(self):
        self.assertEqual(canonical_lf('á\r\nb\rc\n'.encode()),'á\nb\nc\n'.encode())
    def test_normalization_does_not_change_json_escape_semantics(self):
        raw=b'{"value":"a\\r\\nb"}\r\n'
        self.assertEqual(json.loads(raw),json.loads(canonical_lf(raw)))
    def test_invalid_utf8_rejected(self):
        with self.assertRaises(ValueError):canonical_lf(b'\xff')
    def test_normalizer_preserves_source_and_refuses_overwrite(self):
        source=self.repo/'raw';source.write_bytes(b'a\r\n');destination=self.repo/'lf'
        p=self.cli('normalize_text.py',source,destination)
        self.assertEqual(p.returncode,0,p.stdout);self.assertEqual(source.read_bytes(),b'a\r\n');self.assertEqual(destination.read_bytes(),b'a\n');self.assertEqual(destination.stat().st_mode & 0o777,0o600);self.assertEqual(json.loads(p.stdout)['output_mode'],'0600')
        self.assertEqual(self.cli('normalize_text.py',source,destination).returncode,1)
    def test_file_quota_failure_leaves_no_partial_destination_and_retries(self):
        source=self.repo/'raw';source.write_bytes(b'ab\r\n');destination=self.repo/'lf'
        code="import resource,signal,runpy,sys; from pathlib import Path; resource.setrlimit(resource.RLIMIT_FSIZE,(1,1)); signal.signal(signal.SIGXFSZ,signal.SIG_IGN); script=sys.argv.pop(1); sys.argv[0]=script; sys.path.insert(0,str(Path(script).parent)); runpy.run_path(script,run_name='__main__')"
        failed=subprocess.run([sys.executable,'-B','-c',code,str(ROOT/'scripts/normalize_text.py'),str(source),str(destination)],capture_output=True,text=True,timeout=10)
        self.assertEqual(failed.returncode,1,failed.stdout+failed.stderr)
        self.assertEqual(json.loads(failed.stdout)['status'],'BLOCKED')
        self.assertFalse(destination.exists(),'Failed write must not publish partial output')
        self.assertFalse(list(self.repo.glob('.normalize-*')))
        retry=self.cli('normalize_text.py',source,destination)
        self.assertEqual(retry.returncode,0,retry.stdout)
        self.assertEqual(destination.read_bytes(),b'ab\n')

    def test_bom_rejected(self):
        with self.assertRaisesRegex(ValueError,'UTF8_BOM'):canonical_lf(b'\xef\xbb\xbfhello')
    def test_pinned_commit_survives_dirty_worktree(self):
        commit=self.stage();(self.repo/'prd.json').write_text('corrupted worktree');(self.repo/'extra').write_text('uncommitted')
        report=validate_commit(self.repo,commit,'prd.json')
        self.assertEqual(report['status'],'DOCUMENT_VALIDATED_GIT');self.assertNotIn('extra',[x['path'] for x in report['files']]);self.assertEqual(report['advance'],'BLOCKED_GLOBAL_ENFORCEMENT')
    def test_moving_head_does_not_change_requested_commit(self):
        commit=self.stage();(self.repo/'prd.json').write_text('{}');self.git('add','.')
        self.git('-c','user.name=Fixture','-c','user.email=fixture@invalid','commit','--no-gpg-sign','-qm','Other synthetic commit')
        self.assertEqual(validate_commit(self.repo,commit,'prd.json')['commit_oid'],commit)
    def test_symbolic_reference_not_accepted(self):
        self.stage()
        with self.assertRaisesRegex(InvalidGit,'FULL_COMMIT_OID_REQUIRED'):validate_commit(self.repo,'HEAD','prd.json')
    def test_tree_oid_not_commit(self):
        self.stage()
        with self.assertRaisesRegex(InvalidGit,'COMMIT_REQUIRED'):validate_commit(self.repo,self.git('rev-parse','HEAD^{tree}'),'prd.json')
    def test_committed_symlink_is_rejected(self):
        self.stage();(self.repo/'evil').symlink_to('/dev/zero');self.git('add','.')
        self.git('-c','user.name=Fixture','-c','user.email=fixture@invalid','commit','--no-gpg-sign','-qm','Symlink negative fixture')
        with self.assertRaisesRegex(InvalidGit,'UNSUPPORTED_GIT_ENTRY'):validate_commit(self.repo,self.git('rev-parse','HEAD'),'prd.json')
    def test_invalid_prd_path(self):
        commit=self.stage()
        with self.assertRaisesRegex(InvalidGit,'UNSAFE_PRD_PATH'):validate_commit(self.repo,commit,'../prd.json')
    def test_invalid_commit_fails_closed(self):
        self.stage()
        with self.assertRaisesRegex(InvalidGit,'GIT_COMMAND_FAILED'):validate_commit(self.repo,'f'*64,'prd.json')
    def test_sha1_rejected_for_crypto_profile(self):
        commit=self.stage('sha1')
        with self.assertRaisesRegex(InvalidGit,'SHA256_REQUIRED'):
            validate_commit(self.repo,commit,'prd.json')

    def test_sha256_git_objects(self):
        commit=self.stage('sha256');self.assertEqual(len(commit),64)
        self.assertEqual(validate_commit(self.repo,commit,'prd.json')['commit_oid'],commit)
    def test_actual_engine_recovers_after_interruption_during_blob_collection(self):
        commit=self.stage();scratch=self.base/'scratch';scratch.mkdir();marker=self.base/'ready'
        env=os.environ.copy();env['TMPDIR']=str(scratch)
        code="import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import git_validation_engine as validate_git;original=validate_git.Objects.object;count=[0];\ndef pause(self,kind,oid,limit):\n data=original(self,kind,oid,limit)\n if kind=='blob':\n  count[0]+=1\n  if count[0]==2:Path(sys.argv[4]).write_text('ready');sys.stdin.read(1)\n return data\nvalidate_git.Objects.object=pause\nvalidate_git.validate_local(Path(sys.argv[2]),sys.argv[3],'prd.json')"
        child=subprocess.Popen([sys.executable,'-B','-c',code,str(ROOT/'scripts'),str(self.repo),commit,str(marker)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
        try:
            deadline=time.monotonic()+5
            while not marker.exists():
                if child.poll() is not None or time.monotonic()>deadline:self.fail('engine checkpoint not reached')
                time.sleep(.01)
            child.kill();child.wait(timeout=3)
            pool=scratch/('requirements-workspaces-'+str(os.getuid()))
            # The Git path now collects bytes; interrupted collection must not
            # leave a candidate bundle or lease on disk.
            self.assertFalse(pool.exists())
            recovered=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/validate_git.py'),str(self.repo),'--commit',commit,'--prd','prd.json'],env=env,capture_output=True,text=True,timeout=10)
            self.assertEqual(recovered.returncode,0,recovered.stdout+recovered.stderr)
            self.assertFalse(pool.exists())
        finally:
            if child.poll() is None:child.kill();child.wait(timeout=3)
            child.stdin.close()

    def test_crlf_dependency_keeps_byte_identity_gate(self):
        path=test_interview.ContractTests().stage_prd(self.repo)
        interview=self.repo/'interview.json';doc=json.loads(interview.read_bytes());lf=(json.dumps(doc,indent=2)+'\n').encode();interview.write_bytes(lf)
        prd=json.loads(path.read_bytes());prd['candidate']['interview_ref']['sha256']=hashlib.sha256(lf).hexdigest();prd['assurance']['candidate_sha256']=hashlib.sha256(json.dumps(prd['candidate'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();path.write_text(json.dumps(prd))
        self.assertEqual(self.cli('validate_prd.py',path).returncode,0)
        interview.write_bytes(lf.replace(b'\n',b'\r\n'))
        p=self.cli('validate_prd.py',path)
        self.assertEqual(p.returncode,1);self.assertIn('STALE_DEPENDENCY',p.stdout)
        self.assertEqual(json.loads(lf),json.loads(interview.read_bytes()))

if __name__=='__main__':unittest.main(verbosity=2)
