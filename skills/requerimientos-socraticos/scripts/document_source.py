"""Bounded document reads from a directory or immutable Git-bound byte records.

These sources do not isolate an interpreter from another process with the same
UID. Installed schemas remain trusted assets outside the candidate source.
"""
import hashlib
from pathlib import Path, PurePosixPath
from types import MappingProxyType

from safe_io import MAX_FILE_BYTES, read_regular


class Invalid(ValueError):
    def __init__(self, code, detail):
        self.code = code
        self.detail = detail
        super().__init__(f'{code}: {detail}')


def canonical_relative(relative, *, allow_root=False):
    """Reject alternate spellings before PurePath can normalize them away."""
    value = str(relative) if isinstance(relative, PurePosixPath) else relative
    if not isinstance(value, str):
        raise Invalid('UNSAFE_PATH', repr(relative))
    path = PurePosixPath(value)
    if (not value or '\x00' in value or '\\' in value or path.is_absolute()
            or '..' in path.parts or path.as_posix() != value
            or (value == '.' and not allow_root)):
        raise Invalid('UNSAFE_PATH', value)
    return path


def safe_file(base, relative):
    """Retain the legacy path API and symlink diagnostic for filesystem users."""
    base = Path(base)
    path = Path(relative)
    target = (base / path).resolve()
    if path.is_absolute() or not target.is_relative_to(base.resolve()):
        raise Invalid('UNSAFE_PATH', relative)
    cursor = base.resolve()
    for component in path.parts:
        cursor = cursor / component
        if cursor.is_symlink():
            raise Invalid('UNSAFE_PATH', relative)
    return base.resolve() / path


class FilesystemSource:
    def __init__(self, base):
        self.base = Path(base).resolve()

    def read(self, relative):
        path = canonical_relative(relative)
        safe_file(self.base, path)
        return read_regular(self.base, path)

    def scope(self, relative_parent):
        path = canonical_relative(relative_parent, allow_root=True)
        return FilesystemSource(safe_file(self.base, path))


class MemorySource:
    def __init__(self, mapping, blob_oids):
        records, ids = dict(mapping), dict(blob_oids)
        for name in set(records) | set(ids):
            if type(name) is not str:
                raise Invalid('UNSAFE_PATH', repr(name))
            canonical_relative(name)
        if set(records) != set(ids):
            raise Invalid('BLOB_OID_MISSING', 'Document and blob OID paths differ')
        for name, raw in records.items():
            if type(raw) is not bytes:
                raise TypeError(f'Document {name!r} must contain immutable bytes')
            if type(ids[name]) is not str:
                raise TypeError(f'Blob OID for {name!r} must be a string')
        self._records = MappingProxyType(records)
        self._blob_oids = MappingProxyType(ids)
        self._prefix = PurePosixPath('.')
        self._consumed = {}

    @property
    def consumed_files(self):
        return [dict(self._consumed[name]) for name in sorted(self._consumed)]

    def read(self, relative):
        path = canonical_relative(relative)
        name = (self._prefix / path).as_posix()
        try:
            raw = self._records[name]
        except KeyError:
            raise FileNotFoundError(name) from None
        if len(raw) > MAX_FILE_BYTES:
            raise ValueError('FILE_SIZE_LIMIT')
        actual = hashlib.sha256(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()
        if actual != self._blob_oids[name]:
            raise Invalid('BLOB_OID_MISMATCH', name)
        self._consumed[name] = {'path': name, 'git_oid': actual, 'sha256': hashlib.sha256(raw).hexdigest()}
        return raw

    def scope(self, relative_parent):
        path = canonical_relative(relative_parent, allow_root=True)
        scoped = object.__new__(MemorySource)
        scoped._records = self._records
        scoped._blob_oids = self._blob_oids
        scoped._prefix = self._prefix / path
        scoped._consumed = self._consumed
        return scoped
