"""Reject omission of observation-based escalation in an isolated source copy."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
with tempfile.TemporaryDirectory(prefix='qa-partial-mutant-') as directory:
    temp = Path(directory)
    for relative in ('supervisor/qa_adapter.py', 'supervisor/process_core.py',
                     'supervisor/tests/test_qa_adapter.py',
                     'skills/requerimientos-socraticos/scripts/json_preflight.py'):
        target = temp / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / relative, target)
    adapter = temp / 'supervisor/qa_adapter.py'
    source = adapter.read_text()
    old = "failure['scan_status'] != 'COMPLETE'\n                    or failure['status'] != 'NO_DECLARATIONS_FOUND'\n                    or doc['proposed_event'] != 'RECORD_CURRENT_SUCCESS'"
    assert source.count(old) == 1, 'MUTATION_SITE_REQUIRED'
    adapter.write_text(source.replace(old, "doc['proposed_event'] != 'RECORD_CURRENT_SUCCESS'"))
    result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover',
                             '-s', 'supervisor/tests', '-p', 'test_qa_adapter.py',
                             '-k', 'test_partial_escalates'], cwd=temp,
                            capture_output=True, text=True, timeout=10)
    print(result.stdout, end='')
    print(result.stderr, end='', file=sys.stderr)
    assert result.returncode == 1, 'MUTANT_MUST_FAIL'
    assert 'PARTIAL_MUST_REQUIRE_REVIEW' in result.stderr, 'EXPECTED_ASSERTION_REQUIRED'
    assert 'FAILED (failures=1)' in result.stderr, 'SINGLE_EXPECTED_FAILURE_REQUIRED'
    print('NEGATIVE_CONTROL_CONFIRMED: partial observation cannot lose human review')
