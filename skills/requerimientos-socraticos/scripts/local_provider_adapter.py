"""Supervise one trusted local provider process and admit its bounded JSON.

No provider account or network service is configured here. The command comes
from trusted configuration, never from model output. This is a direct-child
control boundary, not a sandbox or a guarantee of physical timing.
"""

import math
import json
import os
import subprocess
import threading

from process_supervision import run_supervised
from source_snapshot import SourceSnapshot
from weak_model_gate import admit_response


MAX_REQUEST_BYTES = 8 * 1024
MAX_RESPONSE_BYTES = 16 * 1024
CHILD_AS_BYTES = 256 * 1024 * 1024
CONFIRMED_CLEANUP = 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED'


def _closed(admission, reason, *, stderr_observed=False):
    return {'admission': admission, 'reason_code': reason, 'ast': None,
            'proposal_sha256': None, 'stderr_observed': stderr_observed,
            'source_binding': 'NOT_ASSESSED',
            'authority_verification': 'NOT_ESTABLISHED',
            'execution_authorized': False}


class LocalProviderAdapter:
    def __init__(self, command, source_snapshot, *, timeout_seconds=5):
        if (type(command) is not tuple or not 1 <= len(command) <= 16
                or any(type(arg) is not str or '\x00' in arg for arg in command)
                or sum(len(arg.encode('utf-8')) for arg in command) > 4096
                or not os.path.isabs(command[0]) or not os.path.isfile(command[0])
                or not os.access(command[0], os.X_OK)):
            raise ValueError('TRUSTED_ABSOLUTE_COMMAND_REQUIRED')
        if type(source_snapshot) is not SourceSnapshot:
            raise ValueError('CALLER_SOURCE_SNAPSHOT_REQUIRED')
        if (type(timeout_seconds) not in (int, float)
                or not math.isfinite(timeout_seconds)
                or not 0 < timeout_seconds <= 30):
            raise ValueError('INVALID_TIMEOUT')
        self.command = command
        self.source_snapshot = source_snapshot
        self.timeout_seconds = timeout_seconds
        self._owner = threading.Lock()
        self._infra_locked = False

    def invoke(self):
        if not self._owner.acquire(blocking=False):
            return _closed('INFRA_FAILURE', 'INSTANCE_BUSY')
        try:
            if self._infra_locked:
                return _closed('INFRA_LOCK', 'CLEANUP_UNCONFIRMED')
            try:
                request_bytes = json.dumps(
                    {'schema_version': 'rs3-source-request/1',
                     'source_ref': self.source_snapshot.source_ref,
                     'source_text': self.source_snapshot.source_text},
                    ensure_ascii=False, sort_keys=True,
                    separators=(',', ':')).encode('utf-8')
            except (MemoryError, OSError, RecursionError, UnicodeError):
                return _closed('INFRA_FAILURE', 'REQUEST_ENCODING_FAILURE')
            if len(request_bytes) > MAX_REQUEST_BYTES:
                return _closed('REJECT_INPUT', 'REQUEST_SIZE_LIMIT')
            try:
                observed = run_supervised(
                    self.command, self.timeout_seconds,
                    input_data=request_bytes,
                    output_limit_bytes=MAX_RESPONSE_BYTES,
                    env={'LANG': 'C.UTF-8'},
                    address_space_limit=(CHILD_AS_BYTES, CHILD_AS_BYTES))
            except (OSError, ValueError, MemoryError, RecursionError,
                    subprocess.SubprocessError):
                return _closed('INFRA_FAILURE', 'PROVIDER_LAUNCH_OR_RESOURCE_FAILURE')
            required = {'cleanup_status', 'stderr_bytes', 'stdout_bytes',
                        'output_limit', 'timed_out', 'returncode'}
            if (type(observed) is not dict or not required <= set(observed)
                    or type(observed['stderr_bytes']) is not bytes
                    or type(observed['stdout_bytes']) is not bytes
                    or type(observed['output_limit']) is not bool
                    or type(observed['timed_out']) is not bool
                    or (observed['returncode'] is not None
                        and type(observed['returncode']) is not int)):
                self._infra_locked = True
                return _closed('INFRA_LOCK', 'MALFORMED_SUPERVISOR_RESULT')
            stderr_observed = bool(observed['stderr_bytes'])
            if observed['cleanup_status'] != CONFIRMED_CLEANUP:
                self._infra_locked = True
                return _closed('INFRA_LOCK', 'CLEANUP_UNCONFIRMED',
                               stderr_observed=stderr_observed)
            if observed['output_limit']:
                return _closed('REJECT_INPUT', 'PROVIDER_OUTPUT_LIMIT',
                               stderr_observed=stderr_observed)
            if observed['timed_out']:
                return _closed('INFRA_FAILURE', 'PROVIDER_TIMEOUT',
                               stderr_observed=stderr_observed)
            if observed['returncode'] is None:
                return _closed('INFRA_FAILURE', 'PROVIDER_EXIT_UNOBSERVED',
                               stderr_observed=stderr_observed)
            if observed['returncode'] < 0:
                return _closed('INFRA_FAILURE', 'PROVIDER_SIGNAL_OBSERVED',
                               stderr_observed=stderr_observed)
            if observed['returncode'] != 0:
                return _closed('INFRA_FAILURE', 'PROVIDER_EXIT_NONZERO',
                               stderr_observed=stderr_observed)
            if not observed['stdout_bytes']:
                return _closed('REJECT_INPUT', 'PROVIDER_EMPTY_OUTPUT',
                               stderr_observed=stderr_observed)
            admitted = admit_response(observed['stdout_bytes'],
                                      source_snapshot=self.source_snapshot)
            return {**admitted, 'stderr_observed': stderr_observed}
        finally:
            self._owner.release()
