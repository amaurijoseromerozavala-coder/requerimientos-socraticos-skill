"""Bounded suite runner: sanitize pipe bytes in memory before any file write."""
import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'skills/requerimientos-socraticos/scripts'))
from process_supervision import run_supervised  # noqa: E402
from supervisor.safe_capture import redact_pair  # noqa: E402

LIMIT = 1024 * 1024


def write_sanitized(stdout_path, stderr_path, stdout, stderr):
    paths = (Path(stdout_path), Path(stderr_path))
    if paths[0].parent != paths[1].parent:
        raise OSError('CAPTURE_DIRECTORY_MISMATCH')
    parent = paths[0].parent
    info = parent.stat()
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise OSError('PRIVATE_CAPTURE_DIRECTORY_REQUIRED')
    created = []
    try:
        for path, data in zip(paths, (stdout, stderr)):
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            created.append(path)
            try:
                with os.fdopen(fd, 'wb', closefd=False) as output:
                    output.write(data)
                    output.flush()
                    os.fsync(fd)
            finally:
                os.close(fd)
    except BaseException:
        for path in created:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def run_capture(command, stdout_path, stderr_path, *, timeout=90):
    try:
        result = run_supervised(command, timeout, output_limit_bytes=LIMIT)
        if result['status'] != 'EXITED' or result['cleanup_status'] != 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED':
            return 124 if result['timed_out'] else 3
        stdout, stderr = redact_pair(result['stdout_bytes'], result['stderr_bytes'])
        if len(stdout) > LIMIT or len(stderr) > LIMIT:
            return 3
        write_sanitized(stdout_path, stderr_path, stdout, stderr)
        code = result['returncode']
        return code if code is not None and code >= 0 else 128 - code if code is not None else 3
    except (OSError, ValueError, TypeError, KeyError, MemoryError, RecursionError):
        return 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stdout_path')
    parser.add_argument('stderr_path')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        return 3
    return run_capture(command, args.stdout_path, args.stderr_path)


if __name__ == '__main__':
    sys.exit(main())
