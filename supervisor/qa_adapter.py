"""Internal local QA adapter; not a durable supervisor or authorization gate.

Trusted callers construct one instance per fixed report/evidence root. No CLI,
application commands, automatic retries, incorporation, or cross-instance guard.
The trusted local checkout and interpreter remain outside this protocol boundary.
"""
import importlib.util
import json
from pathlib import Path
import sys
import threading

from supervisor.process_core import Limits, ProcessSupervisor

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    'qa_adapter_json_preflight', ROOT / 'skills/requerimientos-socraticos/scripts/json_preflight.py')
_json_guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_json_guard)


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('DUPLICATE_KEY')
        result[key] = value
    return result


def _constant(value):
    raise ValueError('NONFINITE_CONSTANT')


def _decode(raw, code):
    _json_guard.preflight_json(raw, max_depth=32, max_bytes=262144)
    doc = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs, parse_constant=_constant)
    if not isinstance(doc, dict):
        raise ValueError('OBJECT_REQUIRED')
    expected = {0: ('COMPLETED', 'VALID'), 2: ('COMPLETED', 'INVALID'),
                3: ('INFRA_FAILURE', 'NOT_ASSESSED')}
    if code not in expected or (doc.get('execution_status'), doc.get('document_validation')) != expected[code]:
        raise ValueError('EXIT_PAYLOAD_MISMATCH')
    events = {0: ('RECORD_CURRENT_SUCCESS', 'RECORD_CURRENT_FAILURE', 'RECORD_GAP_OR_STALE'),
              2: ('REJECT_INPUT',), 3: (None,)}
    if 'proposed_event' not in doc or doc['proposed_event'] not in events[code]:
        raise ValueError('EVENT_MISMATCH')
    if (doc.get('authority_verification') != 'NOT_PERFORMED'
            or doc.get('execution_authorized') is not False
            or doc.get('execution_performed') is not False):
        raise ValueError('AUTHORITY_CONTRACT_MISMATCH')
    observation = doc.get('failure_observation')
    if (not isinstance(observation, dict)
            or observation.get('status') not in ('NOT_ASSESSED', 'UNVERIFIED_DECLARATIONS_FOUND', 'NO_DECLARATIONS_FOUND')
            or observation.get('scan_status') not in ('NOT_ASSESSED', 'PARTIAL', 'COMPLETE')
            or observation.get('evidence_verification') != 'NOT_ESTABLISHED'):
        raise ValueError('OBSERVATION_PROTOCOL_INVALID')
    count, scanned = observation.get('declared_failure_count'), observation.get('scanned_records')
    if (type(scanned) is not int or not 0 <= scanned <= 128
            or (count is not None and (type(count) is not int or not 0 <= count <= scanned))):
        raise ValueError('OBSERVATION_COUNTS_INVALID')
    if observation['status'] == 'NO_DECLARATIONS_FOUND' and (count != 0 or observation['scan_status'] != 'COMPLETE'):
        raise ValueError('OBSERVATION_INCONSISTENT')
    if observation['status'] == 'UNVERIFIED_DECLARATIONS_FOUND' and (count is None or count < 1):
        raise ValueError('OBSERVATION_INCONSISTENT')
    return doc


class QASupervisor:
    def __init__(self, report, evidence_root, limits=None):
        checker = ROOT / 'skills/qa-inquisidor/scripts/validate_report.py'
        command = (str(Path(sys.executable).absolute()), '-B', str(checker),
                   '--report', str(Path(report).absolute()),
                   '--evidence-root', str(Path(evidence_root).absolute()))
        self._core = ProcessSupervisor(command, limits or Limits())
        self._locked = False
        self._owner = threading.Lock()

    def run(self):
        result = {'state': 'IDLE', 'execution_status': 'INFRA_FAILURE',
                  'result_admission': 'REJECT_INFRA', 'document_admission': 'NOT_ASSESSED',
                  'cause': 'NOT_DETERMINED', 'human_review_required': True,
                  'checker_result': None, 'process': None, 'execution_authorized': False,
                  'scope': 'LOCAL_INSTANCE_NO_DURABLE_ADMISSION_OR_INCORPORATION'}
        if not self._owner.acquire(blocking=False):
            result['state'] = 'BUSY'
            return result
        try:
            if self._locked:
                result['state'] = 'INFRA_LOCK'
                return result
            try:
                observation = self._core.run()
                result['process'] = observation
                if observation.get('cleanup') == 'UNCONFIRMED' or observation.get('status') == 'INFRA_LOCK':
                    self._locked = True
                    result['state'] = 'INFRA_LOCK'
                    return result
                if (observation.get('status') != 'EXITED'
                        or observation.get('cleanup') != 'CONFIRMED'
                        or observation.get('stop_reason') is not None
                        or observation.get('capture_complete') is not True
                        or observation.get('capture_truncated') != {'stdout': False, 'stderr': False}):
                    return result
                code = observation.get('returncode')
                doc = _decode(observation['stdout'], code)
                result['checker_result'] = doc
                if code == 3:
                    return result
                result.update(execution_status='COMPLETED', result_admission='ACCEPTED',
                              document_admission='VALID' if code == 0 else 'REJECT_INPUT')
                failure = doc['failure_observation']
                result['human_review_required'] = (
                    failure['scan_status'] != 'COMPLETE'
                    or failure['status'] != 'NO_DECLARATIONS_FOUND'
                    or doc['proposed_event'] != 'RECORD_CURRENT_SUCCESS')
                return result
            except (ValueError, TypeError, KeyError, OSError, MemoryError, RecursionError) as error:
                result['protocol_error'] = type(error).__name__
                # No assured observation of cleanup after a core exception.
                if result['process'] is None:
                    self._locked = True
                    result['state'] = 'INFRA_LOCK'
                return result
        finally:
            self._owner.release()
