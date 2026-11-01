"""Run the public README checker against a false reservation claim in isolation."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
root=Path(__file__).resolve().parents[3]
with tempfile.TemporaryDirectory(prefix='readme-false-scope-') as directory:
    temp=Path(directory)
    for relative in ('README.md','docs/skill-audit/readme-state/check_readme.py',
                     'supervisor/process_core.py','supervisor/qa_adapter.py','supervisor/journal.py'):
        target=temp/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(root/relative,target)
    p=temp/'README.md';s=p.read_text()
    old='Registro cooperativo implementado hasta RESERVED; no está conectado al lanzamiento'
    assert s.count(old)==1
    p.write_text(s.replace(old,'Registro cooperativo implementado hasta RESERVED; recuperación y lanzamiento completos'))
    r=subprocess.run([sys.executable,str(temp/'docs/skill-audit/readme-state/check_readme.py')],
                     capture_output=True,text=True,timeout=5)
    print(r.stdout,end='');print(r.stderr,end='',file=sys.stderr)
    assert r.returncode==1 and 'README_FALSE_RESERVATION_SCOPE' in r.stderr
    print('FALSE_SCOPE_REJECTED')
