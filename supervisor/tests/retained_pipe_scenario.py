"""Isolated Linux test fixture; subreaper ownership permits explicit grandchild reaping."""
import ctypes
import json
import os
from pathlib import Path
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from supervisor.process_core import ProcessSupervisor, Limits


def scenario():
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER, this fixture only
        raise OSError(ctypes.get_errno(), 'subreaper unavailable')
    script = '''import os,time
pid=os.fork()
if pid==0:
    os.setsid()  # Deliberately outside the direct child's group; fixture owns reaping.
    time.sleep(3)
    os._exit(0)
os.write(1,(str(pid)+"\\n").encode())
os._exit(0)
'''
    result = None
    reaped = []
    try:
        result = ProcessSupervisor((sys.executable, '-B', '-c', script),
            Limits(wall_seconds=.4, grace_seconds=.2, cleanup_seconds=.2)).run()
        auxiliary = int(result['stdout'].strip())
        # A positive WNOHANG result would mean the fixture ended too early.
        observed, _ = os.waitpid(auxiliary, os.WNOHANG)
        if observed:
            reaped.append(observed)
        assert observed == 0, 'HELPER_MUST_REMAIN_ALIVE_AT_RETURN'
        assert result['returncode'] == 0, 'DIRECT_CHILD_EXIT_REQUIRED'
        assert result['cleanup'] == 'CONFIRMED', 'OWNED_GROUP_TERMINATED'
        assert result['status'] == 'STOPPED', 'RETAINED_PIPES_REACH_DEADLINE'
        assert result['capture_complete'] is False, 'CAPTURE_MUST_BE_INCOMPLETE'
        assert result['signals_requested'] == [], 'DETACHED_GROUP_MUST_NOT_BE_SIGNALED'
        assert result['elapsed_seconds'] < 2, 'FIXED_BUDGET_WITH_SCHEDULING_TOLERANCE'
        try:
            os.waitpid(result['pid'], os.WNOHANG)
        except ChildProcessError:
            pass
        else:
            raise AssertionError('DIRECT_CHILD_NOT_ALREADY_REAPED')
        return result, auxiliary, reaped
    finally:
        # All remaining children belong to this isolated fixture. Adoption may
        # happen during cleanup, so repeatedly collect through the finite bound.
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                break
            if pid:
                reaped.append(pid)
            else:
                time.sleep(.01)
        else:
            raise AssertionError('FIXTURE_REAP_DEADLINE')
        # No unconfirmed cleanup hidden behind successful test output.
        try:
            os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            pass
        else:
            raise AssertionError('FIXTURE_CHILDREN_REMAIN')


if __name__ == '__main__':
    result, auxiliary, reaped = scenario()
    for stream in ('stdout', 'stderr'):
        result[stream] = result[stream].hex()
    print(json.dumps({'result': result, 'auxiliary_pid': auxiliary,
                      'fixture_reaped_pids': reaped, 'fixture_children_remaining': False,
                      'stream_encoding': 'hex'}))
