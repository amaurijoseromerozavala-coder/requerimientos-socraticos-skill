"""Bounded private scratch slots with leases; no shared-/tmp glob cleanup.

Same-account processes cooperate. This is lifecycle coordination, not security
against hostile same-UID code. A child consuming the bundle must inherit its
lease descriptor and finish before a normal context exit.
"""
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import shutil
import stat
import tempfile
import time

SLOTS = 4

class ScratchError(ValueError):
    pass

def private_directory(path):
    path.mkdir(mode=0o700, exist_ok=True)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise ScratchError('UNSAFE_SCRATCH_DIRECTORY')

def remove_bundle(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise ScratchError('UNSAFE_SCRATCH_BUNDLE')
    # On supported Linux Python, rmtree uses descriptor-based symlink-resistant
    # traversal. Refuse platforms where that protection is unavailable.
    if not shutil.rmtree.avoids_symlink_attacks:
        raise ScratchError('SAFE_RMTREE_UNAVAILABLE')
    shutil.rmtree(path)

@contextmanager
def workspace(timeout=5, root=None, slots=SLOTS):
    if not 0 < timeout <= 300 or not 1 <= slots <= SLOTS:
        raise ScratchError('INVALID_SCRATCH_LIMIT')
    root = Path(root) if root is not None else Path(tempfile.gettempdir()) / ('requirements-workspaces-' + str(os.getuid()))
    private_directory(root)
    deadline = time.monotonic() + timeout
    held = None
    bundle = None
    try:
        while held is None:
            for index in range(slots):
                slot = root / ('slot-' + str(index))
                private_directory(slot)
                fd = os.open(slot / '.lease', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
                try:
                    info = os.fstat(fd)
                    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600:
                        raise ScratchError('UNSAFE_SCRATCH_LEASE')
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        continue
                    held = fd
                    bundle = slot / 'bundle'
                    break
                finally:
                    if held != fd:
                        os.close(fd)
            if held is None:
                if time.monotonic() >= deadline:
                    raise ScratchError('SCRATCH_BUSY')
                time.sleep(min(.01, max(0, deadline-time.monotonic())))
        # Exclusive lease proves no cooperating parent/consumer is using this
        # slot. Reclaim only its exact bundle, never siblings or old /tmp globs.
        remove_bundle(bundle)
        bundle.mkdir(mode=0o700)
        try:
            yield bundle, held
        finally:
            remove_bundle(bundle)
    finally:
        if held is not None:
            os.close(held)
