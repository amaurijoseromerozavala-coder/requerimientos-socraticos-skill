"""Run storage tests from a temporary source export without Git metadata."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
with tempfile.TemporaryDirectory(prefix='requirements-export-test-') as temp:
    export = Path(temp)
    for relative in ('skills/requerimientos-socraticos/scripts',
                     'skills/requerimientos-socraticos/assets',
                     'skills/requerimientos-socraticos/tests',
                     'docs/skill-audit/wsl-storage'):
        shutil.copytree(root / relative, export / relative,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover',
                             '-s', 'skills/requerimientos-socraticos/tests',
                             '-p', 'test_storage_scope.py'], cwd=export, timeout=20)
    raise SystemExit(result.returncode)
