"""Linux setup for the direct child; internal trusted invocation, not a public CLI."""
import ctypes
import os
import resource
import signal
import sys


def main():
    expected_parent, address_bytes, cpu_seconds = map(int, sys.argv[1:4])
    command = sys.argv[4:]
    if not command or not os.path.isabs(command[0]):
        return 125
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
        return 125
    if os.getppid() != expected_parent:
        return 125
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_AS, (address_bytes, address_bytes))
    # Do not raise an inherited hard CPU limit.
    hard = resource.getrlimit(resource.RLIMIT_CPU)[1]
    if hard != resource.RLIM_INFINITY:
        cpu_seconds = min(cpu_seconds, hard)
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    os.execv(command[0], command)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError):
        sys.exit(125)
