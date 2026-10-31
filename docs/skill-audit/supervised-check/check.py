import hashlib,json,os,subprocess,sys,tempfile,time
from pathlib import Path
r=Path('/workspace/replica-gentle-ai');s=r/'skills/requerimientos-socraticos';a=r/'docs/skill-audit/supervised-check'
sys.path.insert(0,str(s/'scripts'));sys.path.insert(0,str(s/'tests'))
import validate_git,test_sealed
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in s.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
fixture=test_sealed.SealedTests();fixture.setUp()
try:
 commit=fixture.stage()
 engine=fixture.base/'engine';engine.mkdir();pidfile=fixture.base/'consumer-pid'
 (engine/'validate_prd.py').write_text('import os,time\nfrom pathlib import Path\nPath('+repr(str(pidfile))+').write_text(str(os.getpid()))\ntime.sleep(30)\n')
 original=validate_git.__file__;validate_git.__file__=str(engine/'validate_git.py')
 started=time.monotonic()
 try:
  validate_git.validate_commit(fixture.repo,commit,'prd.json',timeout=.5)
  raise AssertionError('Timeout not enforced')
 except subprocess.TimeoutExpired:
  elapsed=time.monotonic()-started
 finally:validate_git.__file__=original
 assert pidfile.exists(),'Consumer was not started'
 pid=int(pidfile.read_text())
 try:os.kill(pid,0);alive=True
 except ProcessLookupError:alive=False
 assert not alive,'Timed-out child remains alive'
 recovered=validate_git.validate_commit(fixture.repo,commit,'prd.json',timeout=5)
 assert recovered['status']=='DOCUMENT_VALIDATED_GIT'
 report={'timeout_test':{'scope':'Synthetic waiting consumer; no CPU/memory stress','budget_seconds':.5,'elapsed_seconds':elapsed,'child_alive_after_timeout':alive,'next_validation':'PASS'},'qa_claims':{'no_child_timeout':'REFUTED_FOR_LIVE_PARENT','same_account_isolation':'NOT_PROVIDED_BY_MODEL','utimensat_restores_ctime':'INCORRECT: API sets atime/mtime; not arbitrary ctime','0600_impossible_consumption':'NOT_ESTABLISHED; consumer channel unspecified'},'limits':['No claim for parent terminated while an indefinitely waiting child survives.','Same-UID hostile process and compromised engine/kernel remain outside declared trust boundary.','Not physical WSL or hardware acceptance.']}
 assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in s.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
 (a/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
finally:fixture.tearDown()
