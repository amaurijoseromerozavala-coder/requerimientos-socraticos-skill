"""Linux direct-child lifecycle primitive, not the integrated QA supervisor.

Trusted callers supply the fixed command, never QA input. The instance latches
uncertain cleanup. No durable state, sandbox, descendant containment, QA semantics,
result authorization or cross-instance admission is provided here.
"""
from dataclasses import dataclass
import math
import os
from pathlib import Path
import resource
import selectors
import signal
import subprocess
import sys
import threading
import time


@dataclass(frozen=True)
class Limits:
    wall_seconds: float = 30
    grace_seconds: float = 2
    cleanup_seconds: float = 2
    stdout_bytes: int = 262144
    stderr_bytes: int = 65536
    memory_mib: int = 256

    def validate(self):
        for name, cap in [('wall_seconds', 30), ('grace_seconds', 2), ('cleanup_seconds', 2)]:
            value = getattr(self, name)
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= cap:
                raise ValueError('INVALID_LIMIT: ' + name)
        for name, low, high in [('stdout_bytes', 1, 262144), ('stderr_bytes', 1, 65536), ('memory_mib', 64, 256)]:
            value = getattr(self, name)
            if type(value) is not int or not low <= value <= high:
                raise ValueError('INVALID_LIMIT: ' + name)


class ProcessSupervisor:
    def __init__(self, command, limits=None):
        self.limits = limits or Limits()
        self.limits.validate()
        if (not isinstance(command, tuple) or not 1 <= len(command) <= 64
                or any(not isinstance(x, str) or '\x00' in x for x in command)
                or sum(len(x) for x in command) > 65536
                or not os.path.isabs(command[0]) or not os.path.isfile(command[0])
                or not os.access(command[0], os.X_OK)):
            raise ValueError('TRUSTED_ABSOLUTE_EXECUTABLE_REQUIRED')
        self.command = command
        self._state = 'IDLE'
        self._owner = threading.Lock()

    @property
    def state(self):
        return self._state

    def _wait(self, child, timeout):
        return child.wait(timeout=max(0, timeout))

    def run(self):
        if not self._owner.acquire(blocking=False):
            return {'status': 'BUSY', 'launched': False}
        child = None
        selected = None
        outputs = {'stdout': bytearray(), 'stderr': bytearray()}
        signals = []
        truncated = {'stdout': False, 'stderr': False}
        eof = {'stdout': False, 'stderr': False}
        reason = None
        error = None
        cleanup = 'NOT_STARTED'
        returncode = None
        started = time.monotonic()

        def drain_once(until, cleaning=False):
            """One bounded, fair read per ready stream; never extend the deadline."""
            if selected is None:
                return False
            remaining = max(0, until - time.monotonic())
            exceeded = False
            for key, _ in selected.select(min(.02, remaining)):
                if time.monotonic() >= until:
                    break
                name = key.data
                cap = getattr(self.limits, name + '_bytes')
                available = cap - len(outputs[name])
                try:
                    chunk = os.read(key.fileobj.fileno(),
                                    65536 if cleaning else min(65536, available + 1))
                except BlockingIOError:
                    continue
                if not chunk:
                    selected.unregister(key.fileobj)
                    eof[name] = True
                else:
                    outputs[name].extend(chunk[:available])
                    if len(chunk) > available:
                        truncated[name] = True
                        exceeded = True
            return exceeded

        def wait_draining(until):
            """Reap with zero-time waits while draining until EOF or fixed deadline.

            Reaped child with non-EOF channels returns at the deadline with
            capture_complete=False; this does not claim descendant containment.
            """
            observed = None
            while True:
                if observed is None:
                    try:
                        observed = self._wait(child, 0)
                    except subprocess.TimeoutExpired:
                        pass
                if observed is not None and all(eof.values()):
                    return observed
                if time.monotonic() >= until:
                    if observed is not None:
                        return observed
                    # Preserve timeout as the trigger for the forced-stop phase.
                    return self._wait(child, 0)
                drain_once(until, cleaning=True)
                if selected is None or not selected.get_map():
                    time.sleep(min(.005, max(0, until - time.monotonic())))
        try:
            if self._state == 'INFRA_LOCK':
                return {'status': 'INFRA_LOCK', 'launched': False, 'cleanup': 'UNCONFIRMED'}
            if not sys.platform.startswith('linux'):
                return {'status': 'UNSUPPORTED_ENVIRONMENT', 'launched': False}
            memory = self.limits.memory_mib * 1024 * 1024
            inherited = resource.getrlimit(resource.RLIMIT_AS)[1]
            if inherited != resource.RLIM_INFINITY and memory > inherited:
                return {'status': 'RESOURCE_ADMISSION_REJECTED', 'launched': False}
            self._state = 'ACTIVE'
            cleanup = 'UNCONFIRMED'  # Until launch failure or reaping is established.
            deadline = started + self.limits.wall_seconds
            try:
                child = subprocess.Popen(
                    [sys.executable, '-I', '-B', str(Path(__file__).with_name('_child_entry.py')),
                     str(os.getpid()), str(memory), str(math.ceil(self.limits.wall_seconds + self.limits.grace_seconds + self.limits.cleanup_seconds)),
                     *self.command], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, shell=False, close_fds=True, start_new_session=True)
                selected = selectors.DefaultSelector()
                for stream, name in [(child.stdout, 'stdout'), (child.stderr, 'stderr')]:
                    os.set_blocking(stream.fileno(), False)
                    selected.register(stream, selectors.EVENT_READ, name)
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        reason = 'WALL_DEADLINE'
                        break
                    if not selected.get_map() and child.poll() is not None:
                        break
                    if drain_once(deadline):
                        reason = 'OUTPUT_LIMIT'
                    if reason:
                        break
            except Exception as exc:
                reason = 'OBSERVATION_FAILURE' if child is not None else 'LAUNCH_FAILURE'
                error = type(exc).__name__
                if child is None and isinstance(exc, OSError):
                    cleanup = 'NOT_STARTED'
            finally:
                if child is not None:
                    self._state = 'INFRA_LOCK'  # Latch before any interruptible cleanup.
                    try:
                        if child.poll() is None:
                            signals.append('SIGTERM')
                            child.terminate()
                        try:
                            returncode = wait_draining(time.monotonic() + self.limits.grace_seconds)
                        except subprocess.TimeoutExpired:
                            signals.append('SIGKILL')
                            child.kill()
                            returncode = wait_draining(time.monotonic() + self.limits.cleanup_seconds)
                        cleanup = 'CONFIRMED'
                    except BaseException as exc:
                        # Best effort stop request is not confirmation of reaping.
                        error = type(exc).__name__
                        try:
                            if child.poll() is None:
                                signals.append('SIGKILL')
                                child.kill()
                        except OSError:
                            pass
                        cleanup = 'UNCONFIRMED'
                        if not isinstance(exc, Exception):
                            raise
                    finally:
                        if selected is not None:
                            selected.close()
                        for stream in (child.stdout, child.stderr):
                            if stream is not None:
                                stream.close()
                self._state = 'INFRA_LOCK' if cleanup == 'UNCONFIRMED' else 'IDLE'
            status = ('INFRA_LOCK' if cleanup == 'UNCONFIRMED' else
                      'LAUNCH_FAILED' if child is None else
                      'STOPPED' if reason else
                      'SIGNALED' if returncode is not None and returncode < 0 else 'EXITED')
            return {'status': status, 'launched': child is not None,
                    'pid': child.pid if child else None, 'returncode': returncode,
                    'cleanup': cleanup, 'stop_reason': reason, 'signal_cause': 'NOT_DETERMINED',
                    'signals_requested': signals, 'diagnostic': error,
                    'capture_complete': all(eof.values()), 'capture_truncated': truncated,
                    'stdout': bytes(outputs['stdout']), 'stderr': bytes(outputs['stderr']),
                    'elapsed_seconds': time.monotonic() - started,
                    'requested_address_space_bytes': memory,
                    'scope': 'DIRECT_CHILD_ONLY_NO_DURABLE_RECOVERY'}
        finally:
            self._owner.release()
