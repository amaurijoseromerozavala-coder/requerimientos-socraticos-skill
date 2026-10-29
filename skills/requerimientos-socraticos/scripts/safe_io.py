"""Bounded regular-file reads anchored at a caller-selected trusted directory."""
import os
from pathlib import Path
import stat

MAX_FILE_BYTES = 8 * 1024 * 1024

def read_regular(base, relative, limit=MAX_FILE_BYTES):
    """Open each relative component with openat/O_NOFOLLOW; never read devices.

    The base directory is a trust anchor selected by the caller. This does not
    establish global atomicity or protect a compromised kernel/same-UID runtime.
    The size/mtime/ctime comparison is a best-effort change detector, not proof
    of a coherent read against an adversarial in-place writer. Use pinned Git
    objects/private copies for integrity validation, not this helper alone.
    """
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('UNSAFE_PATH')
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
    directory = os.open(Path(base).resolve(strict=True), flags | os.O_DIRECTORY)
    fd = None
    try:
        for component in relative.parts[:-1]:
            child = os.open(component, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(relative.parts[-1], flags, dir_fd=directory)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError('NOT_REGULAR_FILE')
        if before.st_size > limit:
            raise ValueError('FILE_SIZE_LIMIT')
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, limit - total + 1))
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise ValueError('FILE_SIZE_LIMIT')
            chunks.append(chunk)
        after = os.fstat(fd)
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError('FILE_CHANGED_DURING_READ')
        return b''.join(chunks)
    finally:
        if fd is not None:
            os.close(fd)
        os.close(directory)

def canonical_lf(raw):
    """Normalize physical UTF-8 CRLF/CR to LF without Unicode normalization.

    Literal backslash escape sequences inside JSON are unchanged. Intended for
    authoring new evidence copies, never silently rehashing historical receipts.
    """
    text = raw.decode('utf-8')
    if text.startswith('\ufeff'):
        raise ValueError('UTF8_BOM_NOT_ALLOWED')
    return text.replace('\r\n', '\n').replace('\r', '\n').encode('utf-8')
