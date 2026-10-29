"""Bounded POSIX supervision of trusted, caller-selected local commands.

Deadlines require a responsive OS, and cleanup has one extra second. Linux binds
the direct child to its parent; this is not containment of arbitrary descendants
or a hard real-time, kernel, account, or hardware guarantee. The preexec adapter
is intended for the skill's single-threaded command-line entry points.
"""
import ctypes
import math
import os
import selectors
import signal
import subprocess
import sys
import time

try:
    import resource
except ImportError:
    resource = None


MAX_INPUT_BYTES = 34 * 1024 * 1024 + 8
MAX_OUTPUT_BYTES = 8 * 1024 * 1024
DEFAULT_OUTPUT_BYTES = 2 * 1024 * 1024
CLEANUP_GRACE_SECONDS = 1


def run_supervised(command, timeout, *, input_data=None, pass_fds=(),
                   output_limit_bytes=DEFAULT_OUTPUT_BYTES, env=None,
                   address_space_limit=None):
    """Return bounded text and raw outputs, lifecycle status, and cleanup evidence.

    Input is bytes (at most 34 MiB + 8), or None for an empty stdin. Each output
    stream is retained up to the caller's limit (1 byte through 8 MiB). Exceeding
    either limit kills the owned group and returns OUTPUT_LIMIT. Only explicitly
    listed descriptors are inherited. Commands must never come from model data.
    Optional Linux address_space_limit is a (soft_bytes, hard_bytes) tuple for
    RLIMIT_AS in the direct child before exec; it never changes caller limits.
    Returned limit metadata records the request, not an observed child limit.
    Virtual address space limits do not promise MemoryError for every failure,
    bound RSS, or reserve physical memory.
    """
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('timeout must be finite and greater than zero')
    if input_data is not None and not isinstance(input_data, bytes):
        raise TypeError('input_data must be bytes or None')
    if input_data is not None and len(input_data) > MAX_INPUT_BYTES:
        raise ValueError('input_data exceeds maximum byte limit')
    if type(output_limit_bytes) is not int or not 0 < output_limit_bytes <= MAX_OUTPUT_BYTES:
        raise ValueError('output_limit_bytes must be an integer from 1 through 8 MiB')
    if os.name != 'posix':
        raise OSError('SUPERVISION_UNSUPPORTED_PLATFORM: POSIX adapter required')
    if address_space_limit is not None:
        if (type(address_space_limit) is not tuple or len(address_space_limit) != 2
                or any(type(value) is not int or value <= 0 for value in address_space_limit)
                or address_space_limit[0] > address_space_limit[1]):
            raise ValueError('address_space_limit must be a (soft_bytes, hard_bytes) tuple of positive integers with soft <= hard')
        if (not sys.platform.startswith('linux') or resource is None
                or not hasattr(resource, 'RLIMIT_AS')):
            raise OSError('RESOURCE_CONTROL_UNSUPPORTED: Linux RLIMIT_AS adapter required')
        inherited_hard = resource.getrlimit(resource.RLIMIT_AS)[1]
        if inherited_hard != resource.RLIM_INFINITY and address_space_limit[1] > inherited_hard:
            raise ValueError('address_space_limit exceeds inherited hard RLIMIT_AS')
    started = time.monotonic()
    deadline = started + timeout
    preexec = None
    death_signal = 'UNSUPPORTED_PLATFORM'
    if sys.platform.startswith('linux'):
        libc = ctypes.CDLL(None, use_errno=True)
        parent = os.getpid()

        def bind_parent():
            if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0 or os.getppid() != parent:
                os._exit(70)
            if address_space_limit is not None:
                resource.setrlimit(resource.RLIMIT_AS, address_space_limit)

        preexec = bind_parent
        death_signal = 'LINUX_DIRECT_CHILD_PDEATHSIG'

    out, err = bytearray(), bytearray()
    output_limit = False
    timed_out = False
    cleanup_status = 'INCOMPLETE'
    with selectors.DefaultSelector() as selected:
        process = subprocess.Popen(
            command, stdin=subprocess.PIPE if input_data is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
            preexec_fn=preexec, pass_fds=pass_fds, env=env)
        input_view = memoryview(input_data) if input_data is not None else None
        written = 0

        def close_stream(stream):
            if stream is not None and not stream.closed:
                try:
                    selected.unregister(stream)
                except KeyError:
                    pass
                stream.close()

        def stop_owned_group():
            # The identifier comes solely from this successful Popen, whose
            # start_new_session establishes its owned group before exec.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        def pump(until, cleaning=False):
            nonlocal written, output_limit
            while selected.get_map():
                remaining = until - time.monotonic()
                if remaining <= 0:
                    return False
                if process.poll() is not None:
                    close_stream(process.stdin)
                for key, _ in selected.select(min(remaining, .05)):
                    if time.monotonic() >= until:
                        return False
                    stream = key.fileobj
                    if key.data == 'stdin':
                        try:
                            count = os.write(stream.fileno(), input_view[written:written + 65536])
                            written += count
                        except BlockingIOError:
                            continue
                        except BrokenPipeError:
                            close_stream(stream)
                            continue
                        if written == len(input_view):
                            close_stream(stream)
                    else:
                        target = out if key.data == 'stdout' else err
                        available = output_limit_bytes - len(target)
                        try:
                            chunk = os.read(stream.fileno(), 65536 if cleaning else min(65536, available + 1))
                        except BlockingIOError:
                            continue
                        if not chunk:
                            close_stream(stream)
                            continue
                        target.extend(chunk[:available])
                        if len(chunk) > available:
                            output_limit = True
                            if not cleaning:
                                return False
            try:
                process.wait(timeout=max(0, until - time.monotonic()))
                return True
            except subprocess.TimeoutExpired:
                return False

        try:
            for stream, name in [(process.stdout, 'stdout'), (process.stderr, 'stderr')]:
                os.set_blocking(stream.fileno(), False)
                selected.register(stream, selectors.EVENT_READ, name)
            if process.stdin is not None:
                if input_data:
                    os.set_blocking(process.stdin.fileno(), False)
                    selected.register(process.stdin, selectors.EVENT_WRITE, 'stdin')
                else:
                    close_stream(process.stdin)
            complete = pump(deadline)
            if not complete:
                timed_out = not output_limit
                cleanup_deadline = time.monotonic() + CLEANUP_GRACE_SECONDS
                close_stream(process.stdin)
                stop_owned_group()
                complete = pump(cleanup_deadline, cleaning=True)
            if complete:
                cleanup_status = 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED'
        except BaseException:
            cleanup_deadline = time.monotonic() + CLEANUP_GRACE_SECONDS
            close_stream(process.stdin)
            stop_owned_group()
            try:
                pump(cleanup_deadline, cleaning=True)
            finally:
                raise
        finally:
            for stream in [process.stdin, process.stdout, process.stderr]:
                close_stream(stream)

    stdout_bytes, stderr_bytes = bytes(out), bytes(err)
    result = {'pid': process.pid, 'returncode': process.returncode,
            'stdout': stdout_bytes.decode('utf-8', errors='replace'),
            'stderr': stderr_bytes.decode('utf-8', errors='replace'),
            'stdout_bytes': stdout_bytes, 'stderr_bytes': stderr_bytes,
            'timed_out': timed_out, 'output_limit': output_limit,
            'status': 'OUTPUT_LIMIT' if output_limit else ('TIMED_OUT' if timed_out else 'EXITED'),
            'elapsed_seconds': time.monotonic() - started,
            'cleanup_status': cleanup_status, 'parent_death_policy': death_signal}
    if address_space_limit is not None:
        result['address_space_limit'] = {
            'requested_soft_bytes': address_space_limit[0],
            'requested_hard_bytes': address_space_limit[1],
            'scope': 'direct child RLIMIT_AS before exec'}
    return result
