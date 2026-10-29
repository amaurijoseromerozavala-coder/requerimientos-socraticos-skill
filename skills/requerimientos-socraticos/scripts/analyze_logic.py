#!/usr/bin/env python3
"""Supervise bounded Boolean analysis in a separate worker; never execute model code."""
import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

# Also support tools/tests that load this public script by absolute file path.
try:
    from process_supervision import run_supervised
except ModuleNotFoundError as error:
    if error.name != 'process_supervision':
        raise
    spec = importlib.util.spec_from_file_location(
        'requirements_process_supervision', Path(__file__).with_name('process_supervision.py'))
    supervision_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(supervision_module)
    run_supervised = supervision_module.run_supervised


try:
    from memory_budget import (ResourceBudgetError, admission, enforce_address_space,
                               logic_memory_policy, observe_process_memory)
except ModuleNotFoundError as error:
    if error.name != 'memory_budget':
        raise
    spec = importlib.util.spec_from_file_location(
        'requirements_memory_budget', Path(__file__).with_name('memory_budget.py'))
    memory_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(memory_module)
    ResourceBudgetError = memory_module.ResourceBudgetError
    admission = memory_module.admission
    enforce_address_space = memory_module.enforce_address_space
    logic_memory_policy = memory_module.logic_memory_policy
    observe_process_memory = memory_module.observe_process_memory


try:
    import activation_preflight
except ModuleNotFoundError as error:
    if error.name != 'activation_preflight':
        raise
    spec = importlib.util.spec_from_file_location(
        'requirements_activation_preflight', Path(__file__).with_name('activation_preflight.py'))
    activation_preflight = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(activation_preflight)


def artifact_identity(path):
    try:
        resolved = Path(path).resolve(strict=True)
        size = resolved.stat().st_size
        if not resolved.is_file() or size > 64 * 1024 * 1024:
            return {'status': 'UNKNOWN', 'reason': 'not a bounded regular artifact'}
        digest = hashlib.sha256()
        with resolved.open('rb') as f:
            remaining = 64 * 1024 * 1024 + 1
            while remaining:
                chunk = f.read(min(65536, remaining))
                if not chunk:
                    break
                digest.update(chunk)
                remaining -= len(chunk)
        if not remaining:
            return {'status': 'UNKNOWN', 'reason': 'artifact grew past byte limit'}
        return {'status': 'OBSERVED', 'resolved_path': str(resolved), 'sha256': digest.hexdigest()}
    except (OSError, ValueError, RuntimeError):
        return {'status': 'UNKNOWN', 'reason': 'artifact unavailable'}


def runtime_identity():
    artifact = artifact_identity(sys.executable)
    versions = {}
    for name in ['z3-solver', 'jsonschema']:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {'executable': os.path.abspath(sys.executable), 'python_version': sys.version.split()[0],
            'executable_sha256': artifact.get('sha256'), 'artifact': artifact,
            'distributions': versions, 'authentication': 'NOT_ESTABLISHED',
            'limits': 'Observed bytes/metadata in a trusted local account; not a signed runtime or dependency attestation.'}



class InputError(ValueError):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError(message)


def main(_own_cli=False):
    """Analyze with bounded children; only a fresh owned CLI limits itself."""
    started = time.monotonic()
    runtime = supervision = None
    memory = {'policy': None, 'admission': None, 'caller': None,
              'limits': [
                  'Virtual address-space limits, not RSS quotas or physical reservations.',
                  'Admission serializes cooperating calls per account; not global host enforcement.',
                  'Sequential local samples and lifetime peaks do not prove aggregate RSS.',
                  'Signals and missing diagnostics do not establish OOM.']}

    def emit(document, returncode):
        if runtime is not None:
            document['runtime'] = runtime
        if supervision is not None:
            document['supervision'] = supervision
        if memory['policy'] is not None:
            document['memory_budget'] = memory
        print(json.dumps(document, ensure_ascii=False))
        return returncode

    def exhausted():
        return {'timed_out': True, 'elapsed_seconds': 0,
                'parent_death_policy': 'WORKER_NOT_STARTED', 'cleanup_status': 'NOT_REQUIRED'}

    try:
        parser = Parser(description=__doc__)
        parser.add_argument('input', help='Bounded Boolean JSON model; not executable content')
        parser.add_argument('--timeout', type=float, default=5, help='Wall-time budget in seconds (0 < value <= 30); subject to OS scheduling')
        parser.add_argument('--table', action='store_true', help='Exact guard-activation table for up to 12 inputs, if budget permits')
        parser.add_argument('--memory-budget-mib', type=int, default=None,
                            help='Legacy budget range 256..1024 MiB; admission profile auto-caps at 512 MiB')
        args = parser.parse_args()
        if not math.isfinite(args.timeout) or not 0 < args.timeout <= 30:
            raise InputError('timeout must be greater than 0 and at most 30 seconds')
        preflight = activation_preflight.evaluate(
            Path.cwd(), args.memory_budget_mib, workload='logic',
            caller_scope='OWNED_CLI' if _own_cli else 'EXTERNAL_CALLER')
        if preflight['status'] != 'READY_FOR_LIVE_ADMISSION':
            code = preflight.get('error', {}).get('code', 'RESOURCE_HEADROOM_UNKNOWN')
            if code == 'INVALID_MEMORY_BUDGET':
                code = 'RESOURCE_POLICY_INVALID'
            raise ResourceBudgetError(code)
        effective_mib = preflight['policy']['effective_profile_mib']
        policy = logic_memory_policy(effective_mib)
        memory['activation_preflight'] = preflight
        memory['policy'] = policy
        if os.name != 'posix':
            return emit({'status': 'INCONCLUSIVE', 'error': {'code': 'SUPERVISION_UNSUPPORTED_PLATFORM',
                         'message': 'No bounded process-group supervision adapter for this platform.'}}, 2)
        runtime = runtime_identity()
        remaining = args.timeout - (time.monotonic() - started)
        if remaining <= 0:
            result = exhausted()
        else:
            caller = observe_process_memory()
            caller['sample_scope'] = caller['scope'] if 'scope' in caller else 'PROCESS_LOCAL_SAMPLES'
            caller['scope'] = 'OWNED_CLI_PROCESS' if _own_cli else 'EXTERNAL_CALLER_NOT_LIMITED'
            memory['caller'] = caller
            solver_limit = policy['roles_bytes']['solver']
            if _own_cli:
                baseline = caller.get('virtual_bytes')
                if baseline is None:
                    raise ResourceBudgetError('RESOURCE_BASELINE_UNKNOWN')
                if baseline > policy['roles_bytes']['caller']:
                    raise ResourceBudgetError('RESOURCE_BASELINE_EXCEEDS_ROLE_BUDGET')
                # Retain the larger solver ceiling for its pre-exec limit. The
                # helper rejects any attempt to raise an inherited hard limit.
                try:
                    enforce_address_space(policy['roles_bytes']['caller'], solver_limit)
                except ResourceBudgetError:
                    raise
                except (ValueError, OSError, subprocess.SubprocessError) as error:
                    raise ResourceBudgetError('RESOURCE_CONTROL_SETUP_FAILED') from error
                observed = observe_process_memory()
                observed['sample_scope'] = observed.get('scope', 'PROCESS_LOCAL_SAMPLES')
                observed['scope'] = 'OWNED_CLI_PROCESS'
                memory['caller'] = observed
            with admission(policy) as (lease_fd, admitted):
                memory['admission'] = admitted
                preflight['execution']['control_state'] = 'PARTIALLY_APPLIED'
                preflight['execution']['enforced'] = [
                    'cooperative account admission lock acquired',
                    'visible headroom >= 2x profile at live admission sample']
                remaining = args.timeout - (time.monotonic() - started)
                command = [os.path.abspath(sys.executable)]
                if sys.flags.no_site:
                    command.append('-S')
                command += ['-B', str(Path(__file__).with_name('logic_engine.py')), args.input,
                            '--timeout', str(max(.000001, remaining))]
                if args.table:
                    command.append('--table')
                # Count command setup against the same total deadline too.
                remaining = args.timeout - (time.monotonic() - started)
                if remaining <= 0:
                    result = exhausted()
                else:
                    try:
                        result = run_supervised(command, remaining, pass_fds=(lease_fd,),
                                                address_space_limit=(solver_limit, solver_limit))
                    except (ValueError, OSError, subprocess.SubprocessError) as error:
                        raise ResourceBudgetError('RESOURCE_CONTROL_SETUP_FAILED') from error
                    preflight['execution']['control_state'] = 'APPLIED'
                    preflight['execution']['enforced'].append(
                        'role-specific RLIMIT_AS applied before worker exec')
                    preflight['execution']['workers'] = 'COMPLETED'
        supervision = {'worker_elapsed_seconds': result['elapsed_seconds'], 'wall_budget_seconds': args.timeout,
                       'parent_death_policy': result['parent_death_policy'], 'cleanup_status': result['cleanup_status'],
                       'cleanup_grace_seconds': 1,
                       'limits': 'Responsive OS and live supervisor required for deadline handling; Linux death signal covers direct worker only. No arbitrary descendant or hardware isolation guarantee.'}
        if result.get('output_limit'):
            return emit({'status': 'INCONCLUSIVE', 'error': {'code': 'WORKER_OUTPUT_LIMIT', 'message': 'Worker exceeded its bounded output allowance; cleanup outcome is recorded separately.'}}, 3)
        if result['timed_out']:
            return emit({'status': 'INCONCLUSIVE', 'error': {'code': 'WALL_CLOCK_LIMIT', 'message': 'Wall-time budget exhausted; worker cleanup outcome is recorded separately.'}}, 3)
        try:
            document = json.loads(result['stdout'])
            if not isinstance(document, dict):
                raise ValueError('worker response is not an object')
            if result['returncode'] != 0 and 'error' not in document:
                raise ValueError('worker failed despite emitting a success-shaped result')
        except ValueError:
            return emit({'status': 'INCONCLUSIVE', 'error': {'code': 'WORKER_FAILED', 'message': 'Worker exited without a structured result.'},
                         'worker_returncode': result['returncode']}, 2)
        if isinstance(document.get('error'), dict) and document['error'].get('code') == 'MEMORY_BUDGET_EXCEEDED':
            # A resource failure cannot carry partial successful analysis data.
            failure = {'status': 'INCONCLUSIVE', 'error': document['error']}
            if isinstance(document.get('memory_observation'), dict):
                failure['memory_observation'] = document['memory_observation']
            return emit(failure, 3)
        if _own_cli and result['returncode'] == 0 and 'error' not in document:
            observed = document.get('memory_observation')
            if (not isinstance(observed, dict)
                    or type(observed.get('as_soft_bytes')) is not int
                    or type(observed.get('as_hard_bytes')) is not int
                    or observed['as_soft_bytes'] != solver_limit
                    or observed['as_hard_bytes'] != solver_limit):
                raise ResourceBudgetError('RESOURCE_LIMIT_NOT_OBSERVED')
        return emit(document, result['returncode'] if result['returncode'] in (0, 2, 3) else 2)
    except InputError as error:
        return emit({'error': {'code': 'INVALID_INPUT', 'message': str(error)}}, 2)
    except ResourceBudgetError as error:
        return emit({'status': 'INCONCLUSIVE', 'error': {'code': error.code, 'message': str(error)}}, 3)
    except MemoryError:
        os.write(1, b'{"status":"INCONCLUSIVE","error":{"code":"MEMORY_BUDGET_EXCEEDED"}}\n')
        return 3
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        return emit({'error': {'code': 'SUPERVISOR_ERROR', 'message': str(error)}}, 2)
    except KeyboardInterrupt:
        return emit({'status': 'INCONCLUSIVE', 'error': {'code': 'INTERRUPTED', 'message': 'Analysis interrupted; cleanup was attempted under its bounded contract.'}}, 130)


if __name__ == '__main__':
    def interrupted(signum, frame):
        raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(main(_own_cli=True))
