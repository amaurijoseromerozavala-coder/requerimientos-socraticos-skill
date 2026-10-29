#!/usr/bin/env python3
"""Bounded local observations only; no calibration, identifiers or target inference."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import time


def read_small(path):
    try:
        with Path(path).open('r', encoding='utf-8') as f:
            value = f.read(16385)
        return value if len(value) <= 16384 else None
    except (OSError, UnicodeError):
        return None


def memory_observation():
    raw = read_small('/proc/meminfo') if sys.platform.startswith('linux') else None
    values = {}
    for line in (raw or '').splitlines():
        key, _, rest = line.partition(':')
        parts = rest.split()
        if key in ['MemTotal', 'MemAvailable', 'SwapTotal', 'SwapFree'] and len(parts) == 2 and parts[1] == 'kB':
            try:
                number = int(parts[0])
                if number >= 0:
                    values[key] = number * 1024
            except ValueError:
                pass
    return {'status': 'OBSERVED' if 'MemAvailable' in values else 'UNKNOWN',
            'source': '/proc/meminfo (visible kernel scope)' if raw else 'UNAVAILABLE',
            'total_bytes': values.get('MemTotal'), 'available_bytes': values.get('MemAvailable'),
            'swap_total_bytes': values.get('SwapTotal'), 'swap_free_bytes': values.get('SwapFree')}


def cgroup_observation():
    """Observe visible cgroup-v2 ancestors, not invisible host limits."""
    source = '/proc/self/cgroup and visible /sys/fs/cgroup ancestors'
    raw = read_small('/proc/self/cgroup')
    candidates = [line[3:] for line in (raw or '').splitlines() if line.startswith('0::')]
    unknown = {'status': 'UNKNOWN', 'source': source, 'memory_limits': [], 'cpu_quotas': [], 'limit_states': [],
               'limitation': 'No safe visible cgroup-v2 path; host limits not inferred.'}
    if len(candidates) != 1:
        return unknown
    relative = Path(candidates[0].lstrip('/'))
    if '..' in relative.parts or len(relative.parts) > 64:
        return unknown
    root = Path('/sys/fs/cgroup')
    current = root / relative
    if not current.is_dir():
        return unknown
    memory = []; cpu = []; states = []; observed = False
    for _ in range(65):
        limit = read_small(current / 'memory.max')
        usage = read_small(current / 'memory.current')
        quota = read_small(current / 'cpu.max')
        observed |= any(x is not None for x in [limit, usage, quota])
        state = {'visible_ancestor': len(states), 'memory': 'UNKNOWN', 'cpu': 'UNKNOWN'}
        if limit is not None:
            if limit.strip() == 'max':
                state['memory'] = 'UNLIMITED_VISIBLE_SCOPE'
            else:
                try:
                    state['memory'] = 'FINITE' if int(limit) >= 0 else 'MALFORMED'
                except ValueError:
                    state['memory'] = 'MALFORMED'
        if quota is not None:
            parts = quota.split()
            if len(parts) == 2:
                try:
                    period = int(parts[1])
                    if period <= 0:
                        raise ValueError()
                    if parts[0] == 'max':
                        state['cpu'] = 'UNLIMITED_VISIBLE_SCOPE'
                    else:
                        state['cpu'] = 'FINITE' if int(parts[0]) > 0 else 'MALFORMED'
                except ValueError:
                    state['cpu'] = 'MALFORMED'
            else:
                state['cpu'] = 'MALFORMED'
        states.append(state)
        if limit and limit.strip() != 'max':
            try:
                n = int(limit)
                u = int(usage) if usage is not None else None
                if n >= 0 and (u is None or u >= 0):
                    memory.append({'limit_bytes': n, 'current_bytes': u,
                                   'sampled_headroom_bytes': max(0, n-u) if u is not None else None})
            except ValueError:
                pass
        if quota:
            parts = quota.split()
            if len(parts) == 2 and parts[0] != 'max':
                try:
                    q, p = map(int, parts)
                    if q > 0 and p > 0:
                        cpu.append({'quota': q, 'period': p, 'cpu_time_ratio': q/p})
                except ValueError:
                    pass
        if current == root:
            break
        current = current.parent
    return {'status': 'OBSERVED_VISIBLE_SCOPE' if observed else 'UNKNOWN', 'source': source,
            'memory_limits': memory, 'cpu_quotas': cpu, 'limit_states': states,
            'limitation': 'Sequential samples; hidden ancestors/host and concurrent changes remain unknown.'}


def cpu_model_observation():
    if not sys.platform.startswith('linux'):
        return {'status': 'UNKNOWN', 'model': None, 'class': 'UNKNOWN', 'source': 'OS adapter unavailable'}
    try:
        with Path('/proc/cpuinfo').open('r', encoding='utf-8') as stream:
            raw = stream.read(16384)
    except (OSError, UnicodeError):
        raw = None
    for line in (raw or '').splitlines():
        key, _, value = line.partition(':')
        if key.strip().lower() in ('model name', 'hardware') and value.strip():
            model = value.strip()[:160]
            return {'status': 'OBSERVED', 'model': model, 'class': 'MODEL_STRING_ONLY',
                    'source': '/proc/cpuinfo (bounded first matching field)'}
    return {'status': 'UNKNOWN', 'model': None, 'class': 'UNKNOWN', 'source': '/proc/cpuinfo unavailable or field absent'}


def probe(path):
    start = time.monotonic()
    memory = memory_observation()
    cgroup = cgroup_observation() if sys.platform.startswith('linux') else {
        'status': 'UNSUPPORTED_ADAPTER', 'source': 'cgroup-v2 Linux only', 'memory_limits': [], 'cpu_quotas': [], 'limit_states': []}
    try:
        affinity = len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        affinity = None
    release = platform.release()
    indicators = []
    if 'microsoft' in release.lower():
        indicators.append('WSL_KERNEL_INDICATOR')
    if Path('/.dockerenv').is_file():
        indicators.append('CONTAINER_FILE_INDICATOR')
    try:
        usage = shutil.disk_usage(path)
        storage = {'status': 'OBSERVED', 'source': 'disk_usage of requested path',
                   'total_bytes': usage.total, 'free_bytes': usage.free}
    except (OSError, ValueError):
        storage = {'status': 'UNKNOWN', 'source': 'requested path unavailable', 'total_bytes': None, 'free_bytes': None}
    candidates = [memory['available_bytes']] if memory['available_bytes'] is not None else []
    candidates.extend(x['sampled_headroom_bytes'] for x in cgroup['memory_limits'] if x['sampled_headroom_bytes'] is not None)
    return {'schema_version': '1.0.0', 'kind': 'OBSERVED_LOCAL_ENVIRONMENT',
            'observed_at': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic()-start,
            'platform': {'os': sys.platform, 'architecture': platform.machine(), 'kernel_release': release,
                         'python': platform.python_version()},
            'hosting': {'status': 'INDICATORS_ONLY' if indicators else 'UNKNOWN', 'indicators': indicators},
            'cpu': {'source': 'os.cpu_count / sched_getaffinity / visible cgroup CPU quotas',
                    'logical_visible': os.cpu_count(), 'affinity_count': affinity,
                    'effective_exclusive_cpu_capacity': None, 'model': cpu_model_observation()},
            'memory': memory, 'cgroup': cgroup,
            'sampled_memory_headroom': {'status': 'PARTIAL_ESTIMATE' if candidates else 'UNKNOWN',
                                       'bytes': min(candidates) if candidates else None,
                                       'not_a_budget': True},
            'storage': storage, 'thermal': {'status': 'NOT_MEASURED'},
            'capacity_estimate': {'status': 'NOT_CALIBRATED'},
            'coverage': {'status': 'NOT_COMPUTED_FROM_HARDWARE', 'percent': None},
            'execution_authorized': False, 'target_equivalence': 'NOT_ESTABLISHED',
            'observation_scope': {'visible_runtime': 'OBSERVED', 'physical_host': 'NOT_OBSERVED'},
            'resource_admission': 'NOT_ASSESSED',
            'limits': ['Local visible scope only; no hardware identity or throughput claim.',
                       'No benchmark, temperature sampling, network request or configuration mutation.',
                       'Non-Linux memory/quota adapters are not implemented; unavailable fields remain UNKNOWN.',
                       'Samples are not atomic; do not use them as enforceable resource limits.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--path', type=Path, default=Path.cwd(), help='Existing storage path to observe; no writes')
    args = p.parse_args()
    from analyze_logic import runtime_identity
    document = probe(args.path)
    document['runtime'] = runtime_identity()
    print(json.dumps(document, ensure_ascii=False, allow_nan=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
