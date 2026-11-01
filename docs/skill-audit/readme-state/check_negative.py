"""Reject removal of a verified component row in a temporary copy."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[3]
with tempfile.TemporaryDirectory(prefix='readme-state-') as directory:
    temp=Path(directory)
    for relative in ('README.md','docs/skill-audit/readme-state/check_readme.py',
                     'supervisor/process_core.py','supervisor/qa_adapter.py',
                     'supervisor/journal.py'):
        target=temp/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(root/relative,target)
    path=temp/'README.md';source=path.read_text();assert '| adaptador QA |' in source
    path.write_text(source.replace('| adaptador QA |','| componente omitido |',1))
    run=subprocess.run([sys.executable,str(temp/'docs/skill-audit/readme-state/check_readme.py')],
                       capture_output=True,text=True,timeout=5)
    print(run.stderr,end='',file=sys.stderr)
    assert run.returncode==1 and 'README_MISSING_COMPONENT:adaptador QA' in run.stderr
    print('NEGATIVE_CONTROL_CONFIRMED')
