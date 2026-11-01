"""Confirm duplicate-key coverage rejects a permissive parser in a temporary copy."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[3]
with tempfile.TemporaryDirectory(prefix='journal-duplicates-') as directory:
    temp=Path(directory)
    for relative in ('supervisor/journal.py','supervisor/tests/test_journal.py'):
        target=temp/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(root/relative,target)
    path=temp/'supervisor/journal.py';source=path.read_text()
    assert source.count('object_pairs_hook=_pairs')==1
    path.write_text(source.replace('object_pairs_hook=_pairs','object_pairs_hook=dict'))
    result=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','supervisor/tests',
                           '-p','test_journal.py','-k','test_invalid_records_rejected_without_rewrite'],
                          cwd=temp,capture_output=True,text=True,timeout=10)
    print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr)
    assert result.returncode==1
    assert 'INVALID_RECORD_MUST_BLOCK' in result.stderr
    assert 'FAILED (failures=1)' in result.stderr
    print('NEGATIVE_CONTROL_CONFIRMED: duplicate state ending IDLE cannot be admitted')
