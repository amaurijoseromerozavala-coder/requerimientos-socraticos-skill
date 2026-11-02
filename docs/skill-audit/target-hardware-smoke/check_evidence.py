"""Documentary consistency check; does not authenticate the human's measurements."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).with_name('observation.json')
LIMITATIONS = [
    'The structured report was supplied by the owner; raw process logs were not provided.',
    'One bounded run does not establish behavior under memory, CPU or I/O contention.',
    'RSS belongs to the measured command and is not a global host-memory guarantee.',
    'No cause is assigned to pre/post changes in Windows free memory or PSI I/O.',
    'The run does not authorize CI, deployment, production or hardware stress.',
]


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('DUPLICATE_KEY')
        result[key] = value
    return result


def verify(data, readme):
    assert data['schema'] == 'target-hardware-smoke/v1'
    assert data['provenance'] == {
        'class': 'USER_REPORTED', 'raw_logs': 'NOT_PROVIDED',
        'independent_reproduction': 'NOT_PERFORMED',
        'observed_at_utc': 'NOT_REPORTED'}
    assert data['commit'] == '6ca7fe48ecd730cbe58e3872bdeff00c45631a61'
    gates = data['preconditions']
    assert gates['windows_c_free_bytes'] >= 5 * 1024**3
    assert gates['windows_free_memory_kib'] >= 1200 * 1024
    assert gates['wsl_available_bytes'] >= 1024**3
    assert len(gates['psi_io_full_avg10_percent']) == 2
    assert all(0 <= x <= 5 for x in gates['psi_io_full_avg10_percent'])
    run = data['execution']
    assert run['command'] == 'python3 -B -m unittest discover -s supervisor/tests -q'
    assert run['virtual_memory_limit_kib'] == 524288
    assert run['timeout_seconds'] == 90
    assert run['exit_code'] == 0 and run['tests'] == 62 and run['result'] == 'OK'
    assert 0 < run['unittest_elapsed_ms'] <= run['wall_ms'] <= 90000
    assert 0 < run['peak_rss_kib'] < 524288
    assert data['claims'] == {'production_ready': False, 'stress_calibrated': False,
                              'scope': 'ONE_BOUNDED_RUN'}
    # This fixed report uses a closed vocabulary. A changed or additional
    # causal statement needs a new reviewed candidate, not a passing linter.
    assert data['limitations'] == LIMITATIONS
    assert 'USER_REPORTED' in readme and '62 pruebas' in readme
    assert 'READY para producción' not in readme


def main():
    raw = EVIDENCE.read_bytes()
    if len(raw) > 16384:
        raise ValueError('EVIDENCE_SIZE_LIMIT')
    data = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs)
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    verify(data, readme)
    print('DOCUMENTARY_CONTRACT_OK')


if __name__ == '__main__':
    main()
