#!/usr/bin/env python3
"""Linux-only bounded tree observation. Integrity evidence is not READY authority."""
import argparse
import contextlib
import ctypes
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import struct
import subprocess
import sys
import tempfile
import time

class GuardError(ValueError):
    pass

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode()

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

class Observation:
    """Reject all relevant events, including overflow, watch loss and unmount.

    No historical coverage; local Linux filesystem only; trusted kernel/user.
    All existing directories are armed before the content-read window begins.
    Preparation itself is not claimed as covered. New directories cause rejection, not silent
    recursive resubscription. Reads do not trigger the chosen mask.
    """
    MASK = 0x2 | 0x4 | 0x8 | 0x40 | 0x80 | 0x100 | 0x200 | 0x400 | 0x800 | 0x2000
    def __enter__(self):
        self.lib = ctypes.CDLL(None, use_errno=True)
        self.fd = self.lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        if self.fd < 0:
            raise GuardError('MONITOR_UNAVAILABLE')
        return self

    def add(self, path):
        # IN_ONLYDIR | IN_DONT_FOLLOW; watches pin directory inodes.
        if self.lib.inotify_add_watch(self.fd, os.fsencode(path), self.MASK | 0x1000000 | 0x2000000) < 0:
            raise GuardError('WATCH_UNAVAILABLE')

    def arm(self, root):
        # Two phases: register the whole existing hierarchy, then begin reading
        # contents. Ancestor watches reject topology changes during preparation.
        pending = [root]
        count = 0
        while pending:
            path = pending.pop()
            if len(path.relative_to(root).parts) > 64:
                raise GuardError('DEPTH_LIMIT')
            self.add(path)
            count += 1
            if count > 4096:
                raise GuardError('WATCH_DIRECTORY_LIMIT')
            for child in sorted(path.iterdir(), key=lambda p: p.name):
                if stat.S_ISDIR(child.lstat().st_mode):
                    pending.append(child)
            self.check()
        self.check()
        return time.time_ns()

    def check(self):
        try:
            data = os.read(self.fd, 65536)
        except BlockingIOError:
            return
        events = []
        at = 0
        while at < len(data):
            wd, mask, cookie, size = struct.unpack_from('iIII', data, at)
            events.append({'watch': wd, 'mask': mask})
            at += 16 + size
        if events:
            raise GuardError('OBSERVED_CHANGE_OR_MONITOR_LOSS:' + json.dumps(events))

    def __exit__(self, *args):
        os.close(self.fd)

@contextlib.contextmanager
def lock(root, timeout):
    """Exclusive cooperative lock outside the observed tree, bounded wait."""
    if not math.isfinite(timeout) or not 0 < timeout <= 300:
        raise GuardError('INVALID_TIMEOUT')
    directory = Path(tempfile.gettempdir()) / ('requirements-guard-' + str(os.getuid()))
    directory.mkdir(mode=0o700, exist_ok=True)
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise GuardError('UNSAFE_LOCK_DIRECTORY')
    fd = os.open(directory / (digest(str(root)) + '.lock'), os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1:
            raise GuardError('UNSAFE_LOCK_FILE')
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise GuardError('LOCK_TIMEOUT')
                time.sleep(min(.01, max(0, deadline - time.monotonic())))
        yield
    finally:
        os.close(fd)

def tree(root, observer, destination=None, max_bytes=32 * 1024 * 1024, max_entries=4096):
    """Full directory inventory. No symlinks/special files. Stream bounded files.

    Flat canonical leaves commit the entire hierarchy (paths, kinds, modes,
    sizes and content SHA-256), including empty directories. This is a full-tree
    commitment, not Git's tree format or an incremental Merkle implementation.
    """
    leaves = []
    total = 0
    def walk(path, relative):
        nonlocal total
        if len(relative.parts) > 64:
            raise GuardError('DEPTH_LIMIT')
        info = path.lstat()
        if len(leaves) >= max_entries:
            raise GuardError('ENTRY_LIMIT')
        row = {'path': relative.as_posix(), 'mode': stat.S_IMODE(info.st_mode)}
        if stat.S_ISDIR(info.st_mode):
            observer.add(path)
            row['kind'] = 'directory'
            leaves.append(row)
            if destination is not None:
                (destination / relative).mkdir(parents=True, exist_ok=True)
            for child in sorted(path.iterdir(), key=lambda p: p.name):
                walk(child, relative / child.name)
        elif stat.S_ISREG(info.st_mode):
            row['kind'] = 'file'
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
            output = None
            try:
                current = os.fstat(fd)
                if not stat.S_ISREG(current.st_mode) or (info.st_dev, info.st_ino) != (current.st_dev, current.st_ino):
                    raise GuardError('FILE_REPLACED')
                if destination is not None:
                    output = (destination / relative).open('xb')
                hashed = hashlib.sha256()
                size = 0
                while True:
                    raw = os.read(fd, 65536)
                    if not raw:
                        break
                    total += len(raw)
                    size += len(raw)
                    if total > max_bytes:
                        raise GuardError('BYTE_LIMIT')
                    hashed.update(raw)
                    if output is not None:
                        output.write(raw)
                row.update(size=size, sha256=hashed.hexdigest())
                leaves.append(row)
            finally:
                os.close(fd)
                if output is not None:
                    output.close()
        else:
            raise GuardError('UNSUPPORTED_ENTRY:' + row['path'])
        observer.check()
    walk(root, Path('.'))
    observer.check()
    return {'format': 'full-tree-sha256/v1', 'tree_sha256': digest(leaves), 'entries': leaves, 'bytes': total}

def observe(root, baseline=None, prd=None, timeout=15):
    if root.is_symlink():
        raise GuardError('ROOT_SYMLINK')
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise GuardError('ROOT_NOT_DIRECTORY')
    with lock(root, timeout), Observation() as monitor, tempfile.TemporaryDirectory(prefix='requirements-snapshot-') as td:
        # Parent changes (even unrelated siblings) conservatively invalidate.
        monitor.add(root.parent)
        armed_at = monitor.arm(root)
        snapshot = Path(td) / 'bundle'
        manifest = tree(root, monitor, snapshot if prd is not None else None)
        if baseline is not None:
            if not isinstance(baseline, dict) or not isinstance(baseline.get('entries'), list) or baseline.get('format') != manifest['format'] or baseline.get('tree_sha256') != digest(baseline.get('entries')):
                raise GuardError('INVALID_BASELINE')
            if manifest['entries'] != baseline['entries']:
                raise GuardError('TREE_CHANGED')
        validation = None
        if prd is not None:
            relative = Path(prd)
            if relative.is_absolute() or '..' in relative.parts or relative == Path('.'):
                raise GuardError('UNSAFE_PRD_PATH')
            script = Path(__file__).with_name('validate_prd.py')
            result = subprocess.run([sys.executable, '-B', str(script), str(snapshot / relative)], capture_output=True, text=True, timeout=timeout)
            if result.returncode:
                raise GuardError('DOCUMENT_INVALID:' + result.stdout + result.stderr)
            validation = json.loads(result.stdout)
        monitor.check()
        manifest.update(status='OBSERVED_SNAPSHOT', document_validation=validation,
                        armed_at_unix_ns=armed_at, final_check_unix_ns=time.time_ns(),
                        limits=['Coverage only after all watches are armed through final check; preparation, past and future excluded.',
                                'Linux local filesystem, trusted validator/kernel/account; no hostile same-UID guarantee.',
                                'Cooperative lock only; no cryptographic proof of RDD or downstream enforcement.'])
        return manifest

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['snapshot', 'verify', 'validate', 'advance'])
    p.add_argument('root', type=Path)
    p.add_argument('--baseline', type=Path)
    p.add_argument('--prd')
    p.add_argument('--timeout', type=float, default=15)
    args = p.parse_args()
    try:
        if args.action == 'verify' and args.baseline is None:
            raise GuardError('BASELINE_REQUIRED')
        if args.action in ['validate', 'advance'] and not args.prd:
            raise GuardError('PRD_REQUIRED')
        baseline = json.loads(args.baseline.read_text()) if args.baseline else None
        if args.baseline is not None and not isinstance(baseline, dict):
            raise GuardError('INVALID_BASELINE')
        report = observe(args.root, baseline, args.prd, args.timeout)
        if args.action == 'advance':
            # Never infer an actual configured consumer, protected CI or authentic
            # native receipt from a self-declared JSON field or a successful check.
            raise GuardError('DOWNSTREAM_NOT_CONFIGURED: advancement blocked; snapshot validation is not READY authority')
        print(json.dumps(report, ensure_ascii=True))
        return 0
    except (GuardError, OSError, ValueError, subprocess.TimeoutExpired) as err:
        print(json.dumps({'status': 'BLOCKED', 'error': str(err)}))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
