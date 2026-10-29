#!/usr/bin/env python3
"""Supervise a memory-budgeted Git documentation validation; never change caller API limits."""
import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from git_bundle import canonical_path
from git_validation_engine import InvalidGit, Objects
import activation_preflight
from memory_budget import (ResourceBudgetError, admission, enforce_address_space,
                           memory_policy, observe_process_memory)
from process_supervision import run_supervised

MEMORY_FAILURE = b'{"status":"BLOCKED","error":"MEMORY_BUDGET_EXCEEDED","error_code":"MEMORY_BUDGET_EXCEEDED"}\n'


def validate_commit(repo, commit, prd, timeout=60, memory_budget_mib=None, *, _caller_limited=False):
    started = time.monotonic()
    if memory_budget_mib is not None:
        try:
            memory_policy(memory_budget_mib)
        except ResourceBudgetError as error:
            raise InvalidGit('INVALID_MEMORY_BUDGET') from error
    if not isinstance(commit, str) or not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', commit):
        raise InvalidGit('FULL_COMMIT_OID_REQUIRED')
    if len(commit) != 64:
        raise InvalidGit('SHA256_REQUIRED')
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= 300:
        raise InvalidGit('INVALID_TIMEOUT')
    try:
        canonical_path(prd)
    except ValueError as error:
        raise InvalidGit('UNSAFE_PRD_PATH') from error
    try:
        preflight = activation_preflight.evaluate(
            Path.cwd(), memory_budget_mib, workload='git',
            caller_scope='OWNED_CLI' if _caller_limited else 'EXTERNAL_CALLER')
    except ResourceBudgetError as error:
        raise InvalidGit(str(error)) from error
    if preflight['status'] != 'READY_FOR_LIVE_ADMISSION':
        raise InvalidGit(preflight.get('error', {}).get('code', 'RESOURCE_HEADROOM_UNKNOWN'))
    effective_mib = preflight['policy']['effective_profile_mib']
    try:
        policy = memory_policy(effective_mib)
        with admission(policy) as (lease_fd, admitted):
            preflight['execution']['control_state'] = 'PARTIALLY_APPLIED'
            preflight['execution']['enforced'] = [
                'cooperative account admission lock acquired',
                'visible headroom >= 2x profile at live admission sample']
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                raise InvalidGit('GIT_DEADLINE')
            command = [os.path.abspath(sys.executable), '-B',
                       str(Path(__file__).with_name('git_validation_engine.py')), str(repo),
                       '--commit', commit, '--prd', prd, '--timeout', str(remaining),
                       '--memory-budget-mib', str(effective_mib), '--lease-fd', str(lease_fd)]
            try:
                result = run_supervised(command, remaining, pass_fds=(lease_fd,),
                                        output_limit_bytes=8*1024*1024,
                                        address_space_limit=(policy['roles_bytes']['coordinator'],)*2)
            except (ValueError, OSError, subprocess.SubprocessError) as error:
                raise InvalidGit('RESOURCE_CONTROL_SETUP_FAILED') from error
            preflight['execution']['control_state'] = 'APPLIED'
            preflight['execution']['enforced'].append(
                'coordinator role-specific RLIMIT_AS applied before exec')
            preflight['execution']['workers'] = 'COMPLETED'
            if result['timed_out']:
                raise InvalidGit('GIT_DEADLINE')
            if result['output_limit']:
                raise InvalidGit('COORDINATOR_OUTPUT_LIMIT')
            if result['cleanup_status'] == 'INCOMPLETE':
                raise InvalidGit('COORDINATOR_CLEANUP_INCOMPLETE')
            try:
                document = json.loads(result['stdout'])
            except ValueError as error:
                raise InvalidGit('COORDINATOR_FAILED_WITHOUT_STRUCTURED_RESULT') from error
            if not isinstance(document, dict):
                raise InvalidGit('COORDINATOR_INVALID_RESULT')
            if result['returncode'] != 0:
                raise InvalidGit(str(document.get('error', 'COORDINATOR_FAILED')))
            if document.get('status') != 'DOCUMENT_VALIDATED_GIT':
                raise InvalidGit('COORDINATOR_INVALID_RESULT')
            caller = observe_process_memory()
            caller['sample_scope'] = caller['scope']
            caller['scope'] = 'OWNED_CLI_PROCESS' if _caller_limited else 'EXTERNAL_CALLER_NOT_LIMITED'
            document['memory_budget']['activation_preflight'] = preflight
            document['memory_budget']['admission'] = admitted
            document['memory_budget']['caller'] = caller
            document['memory_budget']['limits'] = [
                'Virtual address-space limits, not RSS quotas or physical reservations.',
                'API caller process is not altered; coordinator and direct workers are limited.',
                'Admission serializes cooperating calls per account; not global host enforcement.',
                'Sequential local memory samples and lifetime peaks do not prove simultaneous aggregate RSS.',
                'Signals and missing diagnostics are not classified as proven OOM.']
            return document
    except ResourceBudgetError as error:
        raise InvalidGit(str(error)) from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', type=Path)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--prd', required=True)
    parser.add_argument('--timeout', type=float, default=60)
    parser.add_argument('--memory-budget-mib', type=int, default=None,
                        help='Legacy budget range 256..1024 MiB; admission profile auto-caps at 512 MiB')
    args = parser.parse_args()
    try:
        preflight = activation_preflight.evaluate(
            Path.cwd(), args.memory_budget_mib, workload='git', caller_scope='OWNED_CLI')
        if preflight['status'] != 'READY_FOR_LIVE_ADMISSION':
            raise InvalidGit(preflight.get('error', {}).get('code', 'RESOURCE_HEADROOM_UNKNOWN'))
        selected_mib = preflight['policy']['effective_profile_mib']
        policy = memory_policy(selected_mib)
        baseline = observe_process_memory()['virtual_bytes']
        if baseline is None:
            raise ResourceBudgetError('RESOURCE_BASELINE_UNKNOWN')
        if baseline > policy['roles_bytes']['caller']:
            raise ResourceBudgetError('RESOURCE_BASELINE_EXCEEDS_ROLE_BUDGET')
        # This main is only the fresh owned CLI. The ordinary validate_commit API
        # never changes the address-space limits of its external caller.
        enforce_address_space(policy['roles_bytes']['caller'], policy['roles_bytes']['coordinator'])
        print(json.dumps(validate_commit(args.repo, args.commit, args.prd, args.timeout,
                                        selected_mib, _caller_limited=True), ensure_ascii=True))
        return 0
    except MemoryError:
        os.write(1, MEMORY_FAILURE)
        return 1
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        code = str(error)
        record = {'status': 'BLOCKED', 'error': code}
        if code.startswith(('RESOURCE_', 'MEMORY_', 'INVALID_MEMORY_BUDGET', 'COORDINATOR_')):
            record['error_code'] = code.split(':', 1)[0]
        print(json.dumps(record, ensure_ascii=True))
        return 1
    except KeyboardInterrupt:
        print('{"status":"BLOCKED","error":"INTERRUPTED","error_code":"INTERRUPTED"}')
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
