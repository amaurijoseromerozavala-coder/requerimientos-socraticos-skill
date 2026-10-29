"""Provisional engineering budgets, Linux virtual limits and cooperative admission.

RLIMIT_AS limits a process's virtual address space, not its RSS. Call the mutating
helper only in a dedicated child or an explicitly owned fresh CLI. Ordinary API
callers must leave their own process limits unchanged. Admission is same-account
cooperation, not isolation from same-UID/noncooperating code or a physical reserve.
"""
from contextlib import contextmanager
import importlib.util
import os
from pathlib import Path
import stat
import sys

try:
    import fcntl
    import resource
except ImportError:
    fcntl = resource = None

try:
    import probe_environment
except ModuleNotFoundError as error:
    if error.name != 'probe_environment':
        raise
    spec = importlib.util.spec_from_file_location(
        'requirements_probe_environment', Path(__file__).with_name('probe_environment.py'))
    probe_environment = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe_environment)
read_small = probe_environment.read_small

MIB = 1024 * 1024


class ResourceBudgetError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def memory_policy(total_mib=512):
    """Return a configurable profile, not measured hardware capacity."""
    if type(total_mib) is not int or not 256 <= total_mib <= 1024 or total_mib % 8:
        raise ResourceBudgetError('RESOURCE_POLICY_INVALID')
    unit = total_mib // 8
    roles = {'caller': unit, 'coordinator': unit * 4, 'consumer': unit * 2, 'git': unit}
    return {'total_mib': total_mib, 'total_bytes': total_mib * MIB,
            'roles_mib': roles, 'roles_bytes': {key: value * MIB for key, value in roles.items()},
            'kind': 'PROVISIONAL_ENGINEERING_POLICY', 'hardware_capacity_calibrated': False,
            'aggregate_kernel_quota': False}


def logic_memory_policy(total_mib=512):
    """Return the provisional Boolean-analysis virtual-address-space profile."""
    if type(total_mib) is not int or not 256 <= total_mib <= 1024 or total_mib % 8:
        raise ResourceBudgetError('RESOURCE_POLICY_INVALID')
    unit = total_mib // 8
    roles = {'caller': unit, 'solver': unit * 7}
    return {'total_mib': total_mib, 'total_bytes': total_mib * MIB,
            'roles_mib': roles, 'roles_bytes': {key: value * MIB for key, value in roles.items()},
            'kind': 'PROVISIONAL_ENGINEERING_POLICY', 'hardware_capacity_calibrated': False,
            'aggregate_kernel_quota': False, 'workload': 'BOOLEAN_ANALYSIS'}


def _matches_policy(value, canonical):
    """Compare canonical shapes and exact types, without numeric coercion."""
    if type(value) is not type(canonical):
        return False
    if type(canonical) is dict:
        return (all(type(key) is str for key in value)
                and value.keys() == canonical.keys()
                and all(_matches_policy(value[key], expected) for key, expected in canonical.items()))
    return value == canonical


def _canonical_policy(policy):
    """Validate a supported profile and return a fresh authoritative snapshot."""
    if type(policy) is not dict:
        raise ResourceBudgetError('RESOURCE_POLICY_INVALID')
    factory = logic_memory_policy if policy.get('workload') == 'BOOLEAN_ANALYSIS' else memory_policy
    canonical = factory(policy.get('total_mib'))
    if not _matches_policy(policy, canonical):
        raise ResourceBudgetError('RESOURCE_POLICY_INVALID')
    return canonical


def _require_linux():
    if not sys.platform.startswith('linux') or resource is None or fcntl is None or not hasattr(resource, 'RLIMIT_AS'):
        raise ResourceBudgetError('RESOURCE_CONTROL_UNSUPPORTED')


def enforce_address_space(soft_bytes, hard_bytes=None):
    """Set this process's RLIMIT_AS explicitly; return actual (soft, hard).

    Omitted hard limit preserves the inherited hard limit, so a fresh CLI can
    retain room to exec its larger coordinator. No inherited hard limit is raised.
    This function never finds or alters another process.
    """
    _require_linux()
    try:
        inherited = resource.getrlimit(resource.RLIMIT_AS)[1]
    except (OSError, ValueError) as error:
        raise ResourceBudgetError('RESOURCE_LIMIT_FAILED') from error
    selected_hard = inherited if hard_bytes is None else hard_bytes
    if (type(soft_bytes) is not int or soft_bytes <= 0
            or (hard_bytes is not None and (type(hard_bytes) is not int or hard_bytes <= 0))
            or (selected_hard != resource.RLIM_INFINITY and soft_bytes > selected_hard)
            or (inherited != resource.RLIM_INFINITY
                and (selected_hard == resource.RLIM_INFINITY or selected_hard > inherited))):
        raise ResourceBudgetError('RESOURCE_LIMIT_INVALID')
    try:
        resource.setrlimit(resource.RLIMIT_AS, (soft_bytes, selected_hard))
        return resource.getrlimit(resource.RLIMIT_AS)
    except (OSError, ValueError, OverflowError) as error:
        raise ResourceBudgetError('RESOURCE_LIMIT_FAILED') from error


def preexec_limit(soft_bytes, hard_bytes=None):
    """Closure for an explicitly selected child; avoid preexec_fn in threads."""
    return lambda: enforce_address_space(soft_bytes, hard_bytes)


def observe_process_memory():
    """Observe current virtual/RSS pages, Linux lifetime high-water RSS and limits."""
    result = {'scope': 'PROCESS_LOCAL_SAMPLES', 'virtual_bytes': None, 'rss_bytes': None,
              'peak_rss_bytes': None, 'peak_rss_scope': 'PROCESS_LIFETIME_HIGH_WATER',
              'as_soft_bytes': None, 'as_hard_bytes': None, 'rss_quota_enforced': False,
              'source': '/proc/self/statm, getrusage(RUSAGE_SELF), getrlimit(RLIMIT_AS)',
              'sampling': 'SEQUENTIAL_NOT_ATOMIC', 'status': 'UNKNOWN'}
    if not sys.platform.startswith('linux') or resource is None:
        return result
    try:
        raw = read_small('/proc/self/statm')
        pages = (raw or '').split()
        virtual, resident = int(pages[0]), int(pages[1])
        page_size = os.sysconf('SC_PAGE_SIZE')
        if virtual >= 0 and resident >= 0 and page_size > 0:
            result.update(virtual_bytes=virtual * page_size, rss_bytes=resident * page_size)
    except (OSError, ValueError, IndexError):
        pass
    try:
        result['peak_rss_bytes'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        result['as_soft_bytes'] = None if soft == resource.RLIM_INFINITY else soft
        result['as_hard_bytes'] = None if hard == resource.RLIM_INFINITY else hard
        result['as_unlimited'] = {'soft': soft == resource.RLIM_INFINITY, 'hard': hard == resource.RLIM_INFINITY}
    except (OSError, ValueError):
        pass
    if result['virtual_bytes'] is not None:
        result['status'] = 'OBSERVED_PROCESS_LOCAL'
    return result


def _admission_directory():
    return Path('/tmp') / ('requirements-admission-' + str(os.getuid()))


def _visible_headroom():
    memory = probe_environment.memory_observation()
    cgroup = probe_environment.cgroup_observation()
    available = memory.get('available_bytes')
    states = cgroup.get('limit_states', [])
    rows = cgroup.get('memory_limits', [])
    if (memory.get('status') != 'OBSERVED' or type(available) is not int or available < 0
            or cgroup.get('status') != 'OBSERVED_VISIBLE_SCOPE' or not states
            or any(row.get('memory') not in ('FINITE', 'UNLIMITED_VISIBLE_SCOPE') for row in states)
            or sum(row.get('memory') == 'FINITE' for row in states) != len(rows)):
        raise ResourceBudgetError('RESOURCE_HEADROOM_UNKNOWN')
    candidates = [available]
    for row in rows:
        limit, current = row.get('limit_bytes'), row.get('current_bytes')
        if type(limit) is not int or type(current) is not int or limit < 0 or current < 0:
            raise ResourceBudgetError('RESOURCE_HEADROOM_UNKNOWN')
        candidates.append(max(0, limit - current))
    return min(candidates), memory, cgroup


@contextmanager
def admission(policy):
    """Hold one account's nonblocking lease; yield (fd, observation).

    Pass fd explicitly with subprocess pass_fds to every consumer, and wait for
    consumers before leaving this context. Descriptors stay non-inheritable in
    the parent. Closing, rather than LOCK_UN, preserves a child's inherited lock
    if its parent dies. No glob, deletion, GC, cgroup mutation, large allocation
    or physical memory reservation.
    """
    _require_linux()
    canonical = _canonical_policy(policy)
    directory = _admission_directory()
    directory_fd = lock_fd = None
    try:
        try:
            directory.mkdir(mode=0o700, exist_ok=True)
            named = directory.lstat()
            directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            info = os.fstat(directory_fd)
            if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
                    or stat.S_IMODE(info.st_mode) != 0o700
                    or (named.st_dev, named.st_ino) != (info.st_dev, info.st_ino)):
                raise ResourceBudgetError('RESOURCE_ADMISSION_UNSAFE')
            lock_fd = os.open('active.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC,
                              0o600, dir_fd=directory_fd)
            info = os.fstat(lock_fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1
                    or stat.S_IMODE(info.st_mode) != 0o600):
                raise ResourceBudgetError('RESOURCE_ADMISSION_UNSAFE')
        except OSError as error:
            raise ResourceBudgetError('RESOURCE_ADMISSION_UNSAFE') from error
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ResourceBudgetError('RESOURCE_BUSY') from error
        headroom, memory, cgroup = _visible_headroom()
        required = 2 * canonical['total_bytes']
        if headroom < required:
            raise ResourceBudgetError('RESOURCE_HEADROOM_INSUFFICIENT')
        yield lock_fd, {'status': 'ADMITTED_COOPERATIVE', 'headroom_observed_bytes': headroom,
                        'required_headroom_bytes': required, 'scope': 'VISIBLE_KERNEL_AND_CGROUP_PARTIAL',
                        'physical_reservation': False, 'sampling': 'SEQUENTIAL_NOT_ATOMIC',
                        'memory_observation': memory, 'cgroup_observation': cgroup}
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
        if directory_fd is not None:
            os.close(directory_fd)
