"""Build a hash-locked, non-authoritative Python runtime in a fresh directory.

This installer is for POSIX Python 3.12 hosts. It does not create an authority
account, authenticate a human, calibrate host hardware, or enable D05.
"""

import argparse
import ctypes
import errno
import hashlib
import json
import os
import signal
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time


LOCK_PATH = Path(__file__).resolve().parents[1] / 'requirements-runtime.lock'
LOCK_SHA256 = '9414d836779bf1ab4be6ce4590e14dd88f2e8a4a638991f56ddb3854b70fe5bc'
MAX_LOCK_BYTES = 65536
MIN_VISIBLE_FREE_BYTES = 512 * 1024 * 1024


class RuntimePreparationBlocked(RuntimeError):
    def __init__(self, reason, *, cleanup_unconfirmed=False):
        super().__init__(reason)
        self.cleanup_unconfirmed = cleanup_unconfirmed


def read_verified_lock():
    try:
        flags = os.O_RDONLY
        if hasattr(os, 'O_NOFOLLOW'):
            flags |= os.O_NOFOLLOW
        fd = os.open(LOCK_PATH, flags)
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or not 1 <= info.st_size <= MAX_LOCK_BYTES:
                raise RuntimePreparationBlocked('LOCK_UNAVAILABLE')
            raw = stream.read(MAX_LOCK_BYTES + 1)
    except OSError as error:
        raise RuntimePreparationBlocked('LOCK_UNAVAILABLE') from error
    if (len(raw) != info.st_size
            or hashlib.sha256(raw).hexdigest() != LOCK_SHA256):
        raise RuntimePreparationBlocked('LOCK_DIGEST_MISMATCH')
    return raw


def validate_python_identity(identity):
    if (type(identity) is not dict or identity.get('implementation') != 'cpython'
            or identity.get('major') != 3 or identity.get('minor') != 12):
        raise RuntimePreparationBlocked('PYTHON_ABI_UNSUPPORTED')


def _python_identity(python):
    source = ('import json,sys;print(json.dumps({'
              '"implementation":sys.implementation.name,'
              '"major":sys.version_info.major,"minor":sys.version_info.minor}))')
    try:
        result = subprocess.run([str(python), '-I', '-c', source],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                timeout=10, check=False)
        if result.returncode or len(result.stdout) > 256:
            raise RuntimePreparationBlocked('PYTHON_IDENTITY_UNAVAILABLE')
        return json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        raise RuntimePreparationBlocked('PYTHON_IDENTITY_UNAVAILABLE') from error


def install_command(stage_python, snapshot_lock, report_path=None):
    report = ['--report', str(report_path)] if report_path is not None else []
    return [str(stage_python), '-I', '-m', 'pip', 'install',
            '--isolated', '--index-url', 'https://pypi.org/simple',
            '--disable-pip-version-check', '--no-input', '--require-hashes',
            '--only-binary=:all:', *report, '-r', str(snapshot_lock)]


def _installed_artifacts(report_path):
    try:
        with report_path.open('rb') as stream:
            raw = stream.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise RuntimePreparationBlocked('INSTALL_REPORT_INVALID')
        entries = json.loads(raw)['install']
        artifacts = []
        for item in entries:
            metadata = item['metadata']
            digest = item['download_info']['archive_info']['hashes']['sha256']
            if (not isinstance(digest, str) or len(digest) != 64
                    or any(char not in '0123456789abcdef' for char in digest)):
                raise ValueError('invalid digest')
            artifacts.append({'name': metadata['name'],
                              'version': metadata['version'], 'sha256': digest})
        if not artifacts:
            raise ValueError('empty report')
        return sorted(artifacts, key=lambda item: item['name'].lower())
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise RuntimePreparationBlocked('INSTALL_REPORT_INVALID') from error


def _write_snapshot(stage, raw):
    path = stage / 'requirements.lock'
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, 'wb') as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
    except OSError as error:
        raise RuntimePreparationBlocked('LOCK_SNAPSHOT_UNAVAILABLE') from error
    return path


def _promote(stage, target):
    """Linux/WSL atomic no-replace promotion; unsupported libc blocks."""
    if not sys.platform.startswith('linux'):
        raise RuntimePreparationBlocked('ATOMIC_PROMOTION_UNSUPPORTED')
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        renameat2 = libc.renameat2
        renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p,
                              ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        renameat2.restype = ctypes.c_int
        result = renameat2(-100, os.fsencode(stage), -100, os.fsencode(target), 1)
    except (AttributeError, OSError) as error:
        raise RuntimePreparationBlocked('ATOMIC_PROMOTION_UNAVAILABLE') from error
    if result != 0:
        code = ctypes.get_errno()
        reason = 'TARGET_EXISTS' if code == errno.EEXIST else 'ATOMIC_PROMOTION_UNAVAILABLE'
        raise RuntimePreparationBlocked(reason) from OSError(code, os.strerror(code))


def _repair_relocation(stage, target):
    """Rewrite venv-generated text entrypoints before atomic promotion."""
    old, new = os.fsencode(stage), os.fsencode(target)
    try:
        entries = [stage / 'pyvenv.cfg', *(stage / 'bin').iterdir()]
        for entry in entries:
            if entry.is_symlink() or not entry.is_file():
                continue
            if entry.stat().st_size > 1024 * 1024:
                continue
            flags = os.O_RDWR
            if hasattr(os, 'O_NOFOLLOW'):
                flags |= os.O_NOFOLLOW
            fd = os.open(entry, flags)
            with os.fdopen(fd, 'r+b') as stream:
                raw = stream.read(1024 * 1024 + 1)
                if old not in raw:
                    continue
                if b'\0' in raw:
                    raise RuntimePreparationBlocked('RELOCATION_UNSUPPORTED')
                stream.seek(0)
                stream.write(raw.replace(old, new))
                stream.truncate()
                stream.flush()
                os.fsync(stream.fileno())
    except OSError as error:
        raise RuntimePreparationBlocked('RELOCATION_UNAVAILABLE') from error


def _run(command, remaining):
    if remaining <= 0:
        raise RuntimePreparationBlocked('PREPARATION_TIMEOUT')
    try:
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   start_new_session=True)
        try:
            returncode = process.wait(timeout=remaining)
        except subprocess.TimeoutExpired as error:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except OSError as kill_error:
                raise RuntimePreparationBlocked(
                    'PROCESS_CLEANUP_UNCONFIRMED', cleanup_unconfirmed=True) from kill_error
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired as wait_error:
                raise RuntimePreparationBlocked(
                    'PROCESS_CLEANUP_UNCONFIRMED', cleanup_unconfirmed=True) from wait_error
            raise RuntimePreparationBlocked('PREPARATION_TIMEOUT') from error
    except OSError as error:
        raise RuntimePreparationBlocked('PREPARATION_UNAVAILABLE') from error
    if returncode:
        raise RuntimePreparationBlocked('PREPARATION_UNAVAILABLE')


def prepare_runtime(target, *, python, timeout_seconds=600):
    """Create only a new venv; report readiness without any human authority."""
    if os.name != 'posix':
        raise RuntimePreparationBlocked('PLATFORM_UNSUPPORTED')
    if type(timeout_seconds) is not int or not 60 <= timeout_seconds <= 900:
        raise RuntimePreparationBlocked('INVALID_TIMEOUT')
    target, python = Path(target), Path(python)
    if not target.is_absolute() or not python.is_absolute():
        raise RuntimePreparationBlocked('ABSOLUTE_PATH_REQUIRED')
    if target.exists() or target.is_symlink():
        raise RuntimePreparationBlocked('TARGET_EXISTS')
    try:
        parent = target.parent.resolve(strict=True)
        interpreter = python.resolve(strict=True)
        if (parent != target.parent or not parent.is_dir()
                or not os.access(parent, os.W_OK | os.X_OK)
                or not interpreter.is_file() or not os.access(interpreter, os.X_OK)):
            raise RuntimePreparationBlocked('PATH_UNAVAILABLE')
        if shutil.disk_usage(parent).free < MIN_VISIBLE_FREE_BYTES:
            raise RuntimePreparationBlocked('VISIBLE_STORAGE_INSUFFICIENT')
    except OSError as error:
        raise RuntimePreparationBlocked('PATH_UNAVAILABLE') from error
    lock_bytes = read_verified_lock()
    validate_python_identity(_python_identity(interpreter))
    deadline = time.monotonic() + timeout_seconds
    try:
        stage = Path(tempfile.mkdtemp(prefix='.rs3-runtime-stage-', dir=parent))
    except OSError as error:
        raise RuntimePreparationBlocked('STAGING_UNAVAILABLE') from error
    preserve_stage = False
    promoted = False
    try:
        snapshot_lock = _write_snapshot(stage, lock_bytes)
        _run([str(interpreter), '-I', '-m', 'venv', str(stage)],
             deadline - time.monotonic())
        stage_python = stage / 'bin' / 'python'
        report_path = stage / 'install-report.json'
        _run(install_command(stage_python, snapshot_lock, report_path),
             deadline - time.monotonic())
        artifacts = _installed_artifacts(report_path)
        _run([str(stage_python), '-I', '-m', 'pip', 'check'],
             deadline - time.monotonic())
        _run([str(stage_python), '-I', '-c', 'import jsonschema,z3'],
             deadline - time.monotonic())
        _repair_relocation(stage, target)
        _promote(stage, target)
        promoted = True
        _run([str(target / 'bin/pip'), '--version'], deadline - time.monotonic())
        _run(['bash', '-c', '. "$1/bin/activate"; test "$VIRTUAL_ENV" = "$1"',
              'bash', str(target)], deadline - time.monotonic())
    except RuntimePreparationBlocked as error:
        preserve_stage = error.cleanup_unconfirmed
        if promoted and not preserve_stage:
            try:
                shutil.rmtree(target)
            except OSError as cleanup_error:
                raise RuntimePreparationBlocked(
                    'TARGET_CLEANUP_UNCONFIRMED') from cleanup_error
        raise
    finally:
        if stage.exists() and not preserve_stage:
            try:
                shutil.rmtree(stage)
            except OSError as error:
                raise RuntimePreparationBlocked('STAGING_CLEANUP_UNCONFIRMED') from error
    return {'status': 'PREPARED_RUNTIME_NOT_AUTHORITY',
            'python_minor': '3.12', 'lock_sha256': LOCK_SHA256,
            'installed_artifacts': artifacts,
            'storage_observation': 'VISIBLE_SCOPE_ONLY',
            'authority_verification': 'NOT_ESTABLISHED',
            'execution_authorized': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Prepare a hash-locked RS3 runtime')
    parser.add_argument('--python', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--timeout-seconds', type=int, default=600)
    args = parser.parse_args(argv)
    try:
        result = prepare_runtime(args.target, python=args.python,
                                 timeout_seconds=args.timeout_seconds)
    except RuntimePreparationBlocked as error:
        print(json.dumps({'status': 'BLOCKED', 'error': str(error),
                          'authority_verification': 'NOT_ESTABLISHED',
                          'execution_authorized': False}, sort_keys=True))
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
