"""Bounded observations only. No changes to installed skill/configuration."""
import hashlib,json,os
from pathlib import Path
import subprocess,sys,tempfile,time
ROOT=Path('/workspace/replica-gentle-ai');SCRIPT=ROOT/'skills/requerimientos-socraticos/scripts'
tracked=[p for p in (ROOT/'skills/requerimientos-socraticos').rglob('*') if p.is_file() and '__pycache__' not in str(p)]
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked}
report={}
with tempfile.TemporaryDirectory(prefix='qa-analysis-bounded-') as td:
    base=Path(td);repo=base/'repo';repo.mkdir();scratch=base/'scratch';scratch.mkdir()
    sys.path.insert(0,str(ROOT/'skills/requerimientos-socraticos/tests'))
    import test_interview
    test_interview.ContractTests().stage_prd(repo)
    def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],stderr=subprocess.DEVNULL,text=True).strip()
    git('init','-q');git('add','.')
    git('-c','user.name=Bounded fixture','-c','user.email=fixture@invalid','commit','--no-gpg-sign','-qm','Temporary analysis fixture')
    oid=git('rev-parse','HEAD')
    raw=base/'input';raw.write_bytes(b'test\r\n');destination=base/'output'
    result=subprocess.run([sys.executable,'-B',str(SCRIPT/'normalize_text.py'),str(raw),str(destination)],capture_output=True,text=True,timeout=5)
    assert result.returncode==0
    report['permissions']={'mode':oct(destination.stat().st_mode & 0o777),'owner_uid':destination.stat().st_uid,'cross_uid_read_test':'NOT_RUN; no privilege changes or sudo'}
    # Pause the actual engine on the second blob, after at least one file has
    # been materialized. SIGKILL just this synthetic child once; never flood /tmp.
    marker=base/'ready'
    child_code="""
import sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import validate_git
original=validate_git.Objects.object
counter=[0]
def paused(self,kind,oid,limit):
    raw=original(self,kind,oid,limit)
    if kind=='blob':
        counter[0]+=1
        if counter[0]==2:
            Path(sys.argv[4]).write_text('second blob reached')
            sys.stdin.read(1)
    return raw
validate_git.Objects.object=paused
validate_git.validate_commit(Path(sys.argv[2]),sys.argv[3],'prd.json')
"""
    env=os.environ.copy();env['TMPDIR']=str(scratch)
    p=subprocess.Popen([sys.executable,'-B','-c',child_code,str(SCRIPT),str(repo),oid,str(marker)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,env=env)
    try:
        deadline=time.monotonic()+5
        while not marker.exists():
            if p.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Child did not reach bounded checkpoint')
            time.sleep(.01)
        p.kill();p.wait(timeout=3)
        orphans=list(scratch.glob('requirements-git-*'))
        files=[f for directory in orphans for f in directory.rglob('*') if f.is_file()]
        report['sigkill']={'child_exit_code':p.returncode,'orphan_directories':len(orphans),'remaining_files':len(files),'remaining_bytes':sum(f.stat().st_size for f in files),'repetitions':1,'cleanup':'Outer temporary-directory context removes only this experiment namespace','oom_or_disk_exhaustion':'NOT_INDUCED'}
    finally:
        if p.poll() is None:p.kill();p.wait(timeout=3)
        p.stdin.close();p.stderr.close()
assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked}
report['installed_source']='UNCHANGED'
print(json.dumps(report,indent=2))
