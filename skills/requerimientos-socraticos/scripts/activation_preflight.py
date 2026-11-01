#!/usr/bin/env python3
"""Read-only activation preflight; output is prospective and never authorizes work."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import re

try:
    import probe_environment
except ModuleNotFoundError as error:
    if error.name != 'probe_environment':
        raise
    spec = importlib.util.spec_from_file_location(
        'requirements_probe_environment', Path(__file__).with_name('probe_environment.py'))
    probe_environment = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe_environment)
try:
    import memory_budget
except ModuleNotFoundError as error:
    if error.name != 'memory_budget':
        raise
    spec = importlib.util.spec_from_file_location(
        'requirements_memory_budget', Path(__file__).with_name('memory_budget.py'))
    memory_budget = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(memory_budget)

MIB = memory_budget.MIB
MIN_MIB = 256
MAX_MIB = 512
WORKLOADS = ('logic', 'git', 'all')
OWNED = 'OWNED_CLI'
EXTERNAL = 'EXTERNAL_CALLER'


def _failure(observation, workload, caller_scope, code, message, *, memory=None, cgroup=None,
             hard=None, hard_status='UNKNOWN', hard_unlimited=False, soft=None,
             soft_status='UNKNOWN', soft_unlimited=None, baseline=None, roles=None, headroom=None):
    uncertain = code.endswith('_UNKNOWN') or code == 'RESOURCE_CONTROL_UNSUPPORTED'
    return {
        'schema_version': '1.0.0', 'kind': 'ACTIVATION_PREFLIGHT',
        'observed_at': datetime.now(timezone.utc).isoformat(), 'status': 'INCONCLUSIVE',
        'observation': observation,
        'policy': {'kind': 'PROVISIONAL_ENGINEERING_POLICY', 'calibration': 'NOT_CALIBRATED',
                   'workload': workload, 'caller_scope': caller_scope,
                   'headroom_visible_bytes': headroom, 'inherited_as_hard_bytes': hard,
                   'inherited_as_hard_status': hard_status,
                   'inherited_as_hard_unlimited': hard_unlimited,
                   'selected_profile_mib': None, 'effective_profile_mib': None,
                   'role_limits_mib': roles, 'selection': 'NO_VIABLE_PROFILE'},
        'capabilities': {'document_analysis': 'AVAILABLE',
                         'workers': 'UNKNOWN' if uncertain else 'REJECTED'},
        'execution': {'authorized': False, 'workers': 'BLOCKED', 'gate': 'LIVE_ADMISSION_REQUIRED',
                      'effective_profile_mib': None, 'control_state': 'PENDING', 'enforced': [],
                      'prospective_controls': ['cooperative account admission lock',
                                               'visible headroom >= 2x profile',
                                               'role-specific RLIMIT_AS before exec'],
                      'advisory': ['visible CPU model/count do not estimate speed',
                                   'storage observation is not a capacity guarantee'],
                      'limits': ['No physical memory reservation or RSS quota.',
                                 'No guarantee against swap or concurrent system changes.',
                                 'Existing caller API limits are preserved.']},
        'evidence': {'memory': memory, 'cgroup': cgroup,
                     'inherited_as_soft_bytes': soft,
                     'inherited_as_soft_status': soft_status,
                     'inherited_as_soft_unlimited': soft_unlimited,
                     'caller_baseline_bytes': baseline if caller_scope == OWNED else None,
                     'caller_baseline_status': ('OBSERVED' if type(baseline) is int else 'UNKNOWN')
                                               if caller_scope == OWNED else 'NOT_APPLICABLE',
                     'unknowns': ['hidden host limits', 'physical host identity', 'thermal state', 'performance']},
        'error': {'code': code, 'message': message}}


def _workload_roles(total_mib, workload):
    if workload == 'logic':
        return memory_budget.logic_memory_policy(total_mib)['roles_mib']
    if workload == 'git':
        return memory_budget.memory_policy(total_mib)['roles_mib']
    combined = {}
    for policy in (memory_budget.logic_memory_policy(total_mib),
                   memory_budget.memory_policy(total_mib)):
        for role, amount in policy['roles_mib'].items():
            combined[role] = max(combined.get(role, 0), amount)
    return combined


def _profile_cap_for_hard(hard_bytes, workload):
    # At most33 supported profiles; use the same role amounts as the report
    # and execution policies, without a second set of allocation fractions.
    for profile in range(MAX_MIB, MIN_MIB - 1, -8):
        roles = _workload_roles(profile, workload)
        if all(amount * MIB <= hard_bytes for amount in roles.values()):
            return profile
    return 0


def _evaluate_memory(path='.', requested_mib=None, *, workload='all', caller_scope=OWNED,
             own_cli=None, baseline_bytes=None):
    """Return visible observations plus an untrusted prospective role profile.

    The caller's current limits are observed, never modified. A fresh owned CLI
    must fit its caller role before a profile can be selected. External API
    callers are not required to fit a caller role and are never limited here.
    """
    if own_cli is not None:
        caller_scope = OWNED if own_cli else EXTERNAL
    observation = probe_environment.probe(Path(path))
    if workload not in WORKLOADS:
        return _failure(observation, str(workload), caller_scope, 'RESOURCE_WORKLOAD_INVALID',
                        'Unsupported preflight workload.')
    if caller_scope not in (OWNED, EXTERNAL):
        return _failure(observation, workload, str(caller_scope), 'RESOURCE_CALLER_SCOPE_INVALID',
                        'Unsupported caller scope.')
    if requested_mib is not None and (type(requested_mib) is not int
                                     or not MIN_MIB <= requested_mib <= 1024
                                     or requested_mib % 8):
        return _failure(observation, workload, caller_scope, 'INVALID_MEMORY_BUDGET',
                        'Memory budgets must be 256..1024 MiB in multiples of 8; admission caps profiles at 512 MiB.')

    resource = memory_budget.resource
    if (not sys.platform.startswith('linux') or resource is None
            or not hasattr(resource, 'RLIMIT_AS')):
        return _failure(observation, workload, caller_scope, 'RESOURCE_CONTROL_UNSUPPORTED',
                        'Role-specific RLIMIT_AS is unavailable on this platform.')
    try:
        soft_raw, hard_raw = resource.getrlimit(resource.RLIMIT_AS)
    except (OSError, ValueError, AttributeError):
        return _failure(observation, workload, caller_scope, 'RESOURCE_HARD_LIMIT_UNKNOWN',
                        'Inherited RLIMIT_AS could not be observed.')
    infinity = resource.RLIM_INFINITY
    if type(hard_raw) is not int or hard_raw < 0 and hard_raw != infinity:
        return _failure(observation, workload, caller_scope, 'RESOURCE_HARD_LIMIT_UNKNOWN',
                        'Inherited RLIMIT_AS hard limit is malformed.',
                        soft=None if soft_raw == infinity else soft_raw,
                        soft_status='OBSERVED', soft_unlimited=soft_raw == infinity)
    hard_bytes = None if hard_raw == infinity else hard_raw
    soft_bytes = None if soft_raw == infinity else soft_raw
    limit_evidence = {'hard_status': 'OBSERVED', 'hard_unlimited': hard_bytes is None,
                      'soft': soft_bytes, 'soft_status': 'OBSERVED',
                      'soft_unlimited': soft_raw == infinity}
    if hard_bytes is None:
        hard_cap = MAX_MIB
    else:
        hard_cap = _profile_cap_for_hard(hard_bytes, workload)

    if caller_scope == OWNED:
        if baseline_bytes is None:
            try:
                baseline_bytes = memory_budget.observe_process_memory().get('virtual_bytes')
            except (OSError, ValueError):
                baseline_bytes = None
        if type(baseline_bytes) is not int or baseline_bytes < 0:
            return _failure(observation, workload, caller_scope, 'RESOURCE_BASELINE_UNKNOWN',
                            'Owned CLI virtual-size baseline is unavailable.', hard=hard_bytes, **limit_evidence,
                            baseline=baseline_bytes)
    else:
        baseline_bytes = None

    try:
        headroom, memory, cgroup = memory_budget._visible_headroom()
    except memory_budget.ResourceBudgetError as error:
        return _failure(observation, workload, caller_scope, error.code,
                        'Visible memory admission evidence is incomplete.', memory=None, cgroup=None,
                        hard=hard_bytes, baseline=baseline_bytes, **limit_evidence)

    headroom_cap = min(MAX_MIB, (headroom // (2 * MIB)) // 8 * 8)
    cap = min(headroom_cap, hard_cap)
    if cap < MIN_MIB:
        code = 'RESOURCE_HARD_LIMIT_INSUFFICIENT' if hard_cap < MIN_MIB else 'RESOURCE_HEADROOM_INSUFFICIENT'
        return _failure(observation, workload, caller_scope, code,
                        'No supported profile fits visible headroom and inherited role limits.',
                        memory=memory, cgroup=cgroup, hard=hard_bytes, **limit_evidence,
                        baseline=baseline_bytes, headroom=headroom)

    roles = _workload_roles(cap, workload)
    if caller_scope == OWNED and baseline_bytes > roles['caller'] * MIB:
        return _failure(observation, workload, caller_scope, 'RESOURCE_BASELINE_EXCEEDS_ROLE_BUDGET',
                        'Owned CLI baseline exceeds the selected caller role.', memory=memory,
                        cgroup=cgroup, hard=hard_bytes, **limit_evidence, baseline=baseline_bytes,
                        roles=roles, headroom=headroom)
    chosen = cap if requested_mib is None else requested_mib
    if chosen > cap:
        return _failure(observation, workload, caller_scope, 'RESOURCE_PROFILE_EXCEEDS_ADMITTED',
                        'Requested profile exceeds visible headroom or inherited role limits.',
                        memory=memory, cgroup=cgroup, hard=hard_bytes, **limit_evidence,
                        baseline=baseline_bytes, roles=_workload_roles(chosen, workload), headroom=headroom)
    roles = _workload_roles(chosen, workload)
    if caller_scope == OWNED and baseline_bytes > roles['caller'] * MIB:
        return _failure(observation, workload, caller_scope, 'RESOURCE_BASELINE_EXCEEDS_ROLE_BUDGET',
                        'Owned CLI baseline exceeds the requested caller role.', memory=memory,
                        cgroup=cgroup, hard=hard_bytes, **limit_evidence, baseline=baseline_bytes,
                        roles=roles, headroom=headroom)
    return {
        'schema_version': '1.0.0', 'kind': 'ACTIVATION_PREFLIGHT',
        'observed_at': datetime.now(timezone.utc).isoformat(), 'status': 'READY_FOR_LIVE_ADMISSION',
        'observation': observation,
        'policy': {'kind': 'PROVISIONAL_ENGINEERING_POLICY', 'calibration': 'NOT_CALIBRATED',
                   'workload': workload, 'caller_scope': caller_scope,
                   'headroom_visible_bytes': headroom, 'headroom_profile_cap_mib': headroom_cap,
                   'inherited_as_hard_bytes': hard_bytes,
                   'inherited_as_hard_status': 'OBSERVED',
                   'inherited_as_hard_unlimited': hard_bytes is None,
                   'selected_profile_mib': cap, 'effective_profile_mib': chosen,
                   'role_limits_mib': roles,
                   'selection_rule': 'min(512 MiB, floor8(headroom/2), each role fit under inherited RLIMIT_AS)',
                   'selection': 'PROVISIONAL_ROLE_VIABILITY'},
        'capabilities': {'document_analysis': 'AVAILABLE', 'workers': 'CANDIDATE_SUBJECT_TO_LIVE_ADMISSION'},
        'execution': {'authorized': False, 'workers': 'LIVE_GATE_REQUIRED',
                      'gate': 'LIVE_ADMISSION_REQUIRED', 'effective_profile_mib': chosen,
                      'control_state': 'PENDING', 'enforced': [],
                      'prospective_controls': ['cooperative account admission lock',
                                               'visible headroom >= 2x profile',
                                               'role-specific RLIMIT_AS before exec'],
                      'advisory': ['visible CPU model/count do not estimate speed',
                                   'storage observation is not a capacity guarantee'],
                      'limits': ['No physical memory reservation or RSS quota.',
                                 'No guarantee against swap or concurrent system changes.',
                                 'Existing caller API limits are preserved.'],
                      'existing_contract': {'analyze_timeout_seconds': 'default 5; accepted >0..30',
                                           'git_timeout_seconds': 'default 60; accepted >0..300',
                                           'boolean_variables_max': 32, 'boolean_ast_nodes_max': 4096,
                                           'boolean_input_bytes_max': 262144,
                                           'git_document_bytes_max_each': 8388608,
                                           'git_document_bytes_max_total': 33554432,
                                           'json_structural_depth_max': 96}},
        'evidence': {'memory': memory, 'cgroup': cgroup,
                     'inherited_as_soft_bytes': soft_bytes,
                     'inherited_as_soft_status': 'OBSERVED',
                     'inherited_as_soft_unlimited': soft_raw == infinity,
                     'caller_baseline_bytes': baseline_bytes,
                     'caller_baseline_status': 'OBSERVED' if caller_scope == OWNED else 'NOT_APPLICABLE',
                     'unknowns': ['hidden host limits', 'physical host identity', 'thermal state', 'performance']}}


def source_checkout():
    """Observe source clone, never fetch/reset/install or expose remote credentials.

    Origin equality is provenance metadata, not authentication. HEAD does not
    identify uncommitted files. The clone checked is the skill's, not the target.
    """
    root = Path(__file__).resolve().parents[3]
    unknown = {'status': 'CLONE_UNVERIFIED', 'origin_match': False,
               'head_commit': None, 'worktree_identity': 'NOT_ESTABLISHED'}
    def git(*args):
        r = subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                           text=True, timeout=2)
        if r.returncode or len(r.stdout) > 4096:
            raise ValueError('CLONE_METADATA_UNAVAILABLE')
        return r.stdout.strip()
    try:
        if Path(git('rev-parse', '--show-toplevel')).resolve() != root:
            return unknown
        origin = git('config', '--get', 'remote.origin.url')
        allowed = {'https://github.com/amaurijoseromerozavala-coder/requerimientos-socraticos-skill.git',
                   'https://github.com/amaurijoseromerozavala-coder/requerimientos-socraticos-skill',
                   'git@github.com:amaurijoseromerozavala-coder/requerimientos-socraticos-skill.git'}
        head = git('rev-parse', '--verify', 'HEAD^{commit}')
        if origin not in allowed or re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', head) is None:
            return unknown
        return {'status': 'VERIFIED_LOCAL_CLONE', 'origin_match': True,
                'head_commit': head, 'worktree_identity': 'NOT_ESTABLISHED'}
    except (OSError, ValueError, subprocess.SubprocessError):
        return unknown


def evaluate(path='.', requested_mib=None, *, workload='all', caller_scope=OWNED,
             own_cli=None, baseline_bytes=None, storage_required_bytes=None):
    if storage_required_bytes is not None and (
            type(storage_required_bytes) is not int or storage_required_bytes <= 0):
        raise ValueError('INVALID_STORAGE_REQUEST: expected positive integer bytes')
    report = _evaluate_memory(path, requested_mib, workload=workload,
                              caller_scope=caller_scope, own_cli=own_cli,
                              baseline_bytes=baseline_bytes)
    report['schema_version'] = '1.1.0'
    report['source_checkout'] = source_checkout()
    if report['source_checkout']['status'] != 'VERIFIED_LOCAL_CLONE':
        report['status'] = 'INCONCLUSIVE'
        report['execution']['workers'] = 'BLOCKED'
        report['capabilities']['workers'] = 'UNKNOWN'
        if 'error' not in report:
            report['error'] = {'code': 'SOURCE_CLONE_UNVERIFIED', 'message': 'Use the official cloned repository; no automatic clone or overwrite performed.'}
    report['storage_admission'] = {
        'status': 'NOT_ASSESSED' if storage_required_bytes is None else 'BLOCKED_HOST_STORAGE_UNKNOWN',
        'requested_bytes': storage_required_bytes, 'authorized': False,
        'readiness_scope': 'MEMORY_ROLE_VIABILITY_ONLY',
        'host_volume_status': 'UNKNOWN', 'host_free_bytes': None,
        'reserved_bytes': 0,
        'reason': 'Host-volume identity, live capacity, reserve margin and reservation are not established.'}
    if storage_required_bytes is not None:
        report['status'] = 'INCONCLUSIVE'
        report['execution']['workers'] = 'BLOCKED'
        report['capabilities']['workers'] = 'UNKNOWN'
        if 'error' not in report:
            report['error'] = {'code': 'HOST_STORAGE_UNKNOWN',
                               'message': 'Storage-dependent work cannot be admitted from guest filesystem free bytes.'}
    return report


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError('INVALID_ARGUMENT: ' + message)


def main():
    parser = Parser(description=__doc__)
    parser.add_argument('--path', type=Path, default=Path.cwd())
    parser.add_argument('--memory-budget-mib', type=int)
    parser.add_argument('--storage-required-bytes', type=int, help='Positive storage request; unknown host capacity blocks this work')
    parser.add_argument('--workload', choices=WORKLOADS, default='all')
    parser.add_argument('--caller-scope', choices=(OWNED, EXTERNAL), default=OWNED)
    try:
        args = parser.parse_args()
        report = evaluate(args.path, args.memory_budget_mib, workload=args.workload,
                          caller_scope=args.caller_scope, storage_required_bytes=args.storage_required_bytes)
        print(json.dumps(report, ensure_ascii=False, allow_nan=False))
        return 0 if report['status'] == 'READY_FOR_LIVE_ADMISSION' else 3
    except MemoryError:
        print(json.dumps({'status': 'INCONCLUSIVE', 'error': {'code': 'MEMORY_BUDGET_EXCEEDED'}}))
        return 3
    except (OSError, ValueError, TypeError) as error:
        code = str(error).split(':', 1)[0]
        if code not in ('INVALID_ARGUMENT', 'INVALID_MEMORY_BUDGET', 'RESOURCE_PROFILE_EXCEEDS_ADMITTED', 'INVALID_STORAGE_REQUEST'):
            code = 'PREFLIGHT_FAILED'
        print(json.dumps({'status': 'INCONCLUSIVE', 'error': {'code': code,
                                                               'message': str(error)}}))
        return 3



if __name__ == '__main__':
    raise SystemExit(main())
