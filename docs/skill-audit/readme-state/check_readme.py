"""Check the README's component-state claims against tracked implementation paths."""
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[3]
readme=(root/'README.md').read_text()
claims={
 'núcleo':'supervisor/process_core.py',
 'adaptador QA':'supervisor/qa_adapter.py',
 'reserva persistente':'supervisor/journal.py',
}
for label, path in claims.items():
    assert (root/path).is_file(), 'MISSING_COMPONENT:'+path
    assert ('| '+label+' |' in readme), 'README_MISSING_COMPONENT:'+label
assert '| supervisor ampliado |' in readme, 'README_MISSING_GLOBAL_STATUS'
assert 'integración QA, incorporación ni recuperación' not in readme, 'README_STALE_CORE_CLAIM'
assert 'no implementado' in readme, 'README_MUST_DECLARE_INCOMPLETE'
print('README_COMPONENT_STATES_OK')
