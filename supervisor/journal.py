"""Cooperative Linux reservation ledger, not launch admission or recovery.

An unresolved reservation never resets automatically. Trusted callers supply
identity metadata; this module does not authenticate it or reserve disk capacity.
Durability relies on the filesystem honoring fsync. Account/root changes and
arbitrary descendants are outside the single-owner trust boundary.
"""
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import threading
import uuid

MAX_BYTES = 16384
IDENTITY_FIELDS = {'run_id', 'boot_id', 'pid_namespace_identity', 'owner_uid',
                   'checker_manifest_digest', 'policy_digest'}


class JournalBlocked(RuntimeError):
    pass


def _identity(value):
    if not isinstance(value, dict) or set(value) != IDENTITY_FIELDS:
        raise JournalBlocked('INVALID_IDENTITY_FIELDS')
    if type(value['owner_uid']) is not int or value['owner_uid'] != os.getuid():
        raise JournalBlocked('OWNER_MISMATCH')
    for field in IDENTITY_FIELDS - {'owner_uid'}:
        text = value[field]
        if not isinstance(text, str) or not 1 <= len(text) <= 256 or any(ord(c) < 32 for c in text):
            raise JournalBlocked('INVALID_IDENTITY_VALUE')
    for field in ('checker_manifest_digest', 'policy_digest'):
        if re.fullmatch('[0-9a-f]{64}', value[field]) is None:
            raise JournalBlocked('INVALID_DIGEST')


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise JournalBlocked('DUPLICATE_KEY')
        result[key] = value
    return result


def _validate(doc):
    if not isinstance(doc, dict) or set(doc) != {'schema_version', 'state', 'identity'}:
        raise JournalBlocked('INVALID_RECORD')
    if doc['schema_version'] != 'reservation-journal/v1':
        raise JournalBlocked('UNKNOWN_SCHEMA')
    if doc['state'] == 'IDLE' and doc['identity'] is None:
        return doc
    if doc['state'] == 'RESERVED':
        _identity(doc['identity'])
        return doc
    if doc['state'] in ('ACTIVE', 'STOPPING'):
        identity = doc['identity']
        if not isinstance(identity, dict) or set(identity) != IDENTITY_FIELDS | {'pid', 'process_start_identity'}:
            raise JournalBlocked('INCOMPLETE_PROCESS_IDENTITY')
        _identity({key: identity[key] for key in IDENTITY_FIELDS})
        if (type(identity['pid']) is not int or identity['pid'] <= 0
                or not isinstance(identity['process_start_identity'], str)
                or not 1 <= len(identity['process_start_identity']) <= 256
                or any(ord(char) < 32 for char in identity['process_start_identity'])):
            raise JournalBlocked('INVALID_PROCESS_IDENTITY')
        return doc
    raise JournalBlocked('UNKNOWN_OR_INCOHERENT_STATE')


def _regular(fd):
    info = os.fstat(fd)
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or info.st_nlink != 1 or info.st_mode & 0o077):
        raise JournalBlocked('PRIVATE_REGULAR_FILE_REQUIRED')
    return info


class Journal:
    def __init__(self, root):
        self.root = Path(root).absolute()
        self._directory = None
        self._lock = None
        self._failed = False
        self._operation = threading.Lock()

    @classmethod
    def initialize(cls, root):
        """Create a new private store only; never repair or overwrite a store."""
        root = Path(root).absolute()
        os.mkdir(root, 0o700)  # Existing or partially initialized stores stay blocked.
        directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for name, data in (('owner.lock', b''), ('state.json', b'{"schema_version":"reservation-journal/v1","state":"IDLE","identity":null}\n')):
                fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory)
                try:
                    with os.fdopen(fd, 'wb', closefd=False) as output:
                        output.write(data)
                        output.flush()
                        os.fsync(fd)
                finally:
                    os.close(fd)
            os.fsync(directory)
            parent = os.open(root.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
        finally:
            os.close(directory)

    def __enter__(self):
        if self._failed or self._directory is not None:
            raise JournalBlocked('INSTANCE_UNAVAILABLE')
        try:
            self._directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            info = os.fstat(self._directory)
            if info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise JournalBlocked('PRIVATE_DIRECTORY_REQUIRED')
            self._lock = os.open('owner.lock', os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK,
                                 dir_fd=self._directory)
            _regular(self._lock)
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.inspect()
            return self
        except (OSError, ValueError, JournalBlocked) as error:
            self._failed = True
            self.__exit__(None, None, None)
            raise JournalBlocked('STORE_UNAVAILABLE') from error

    def __exit__(self, *_):
        if self._lock is not None:
            os.close(self._lock)
            self._lock = None
        if self._directory is not None:
            os.close(self._directory)
            self._directory = None

    def inspect(self):
        if self._failed or self._lock is None or self._directory is None:
            raise JournalBlocked('NO_ACTIVE_LEASE')
        try:
            fd = os.open('state.json', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=self._directory)
            try:
                if _regular(fd).st_size > MAX_BYTES:
                    raise JournalBlocked('STATE_TOO_LARGE')
                with os.fdopen(fd, 'rb', closefd=False) as source:
                    raw = source.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise JournalBlocked('STATE_TOO_LARGE')
            finally:
                os.close(fd)
            return _validate(json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs))
        except (OSError, ValueError, RecursionError, JournalBlocked) as error:
            self._failed = True
            raise JournalBlocked('STATE_UNAVAILABLE') from error

    def reserve(self, identity):
        if not self._operation.acquire(blocking=False):
            raise JournalBlocked('RESERVATION_BUSY')
        try:
            return self._reserve(identity)
        finally:
            self._operation.release()

    def _reserve(self, identity):
        _identity(identity)
        if self.inspect()['state'] != 'IDLE':
            raise JournalBlocked('UNRESOLVED_RESERVATION')
        self._persist('RESERVED', identity)

    def record_active(self, pid, process_start_identity):
        if not self._operation.acquire(blocking=False):
            raise JournalBlocked('RESERVATION_BUSY')
        try:
            state = self.inspect()
            if state['state'] != 'RESERVED':
                raise JournalBlocked('ACTIVE_REQUIRES_RESERVED')
            identity = dict(state['identity'], pid=pid,
                            process_start_identity=process_start_identity)
            _validate({'schema_version': 'reservation-journal/v1',
                       'state': 'ACTIVE', 'identity': identity})
            self._persist('ACTIVE', identity)
        finally:
            self._operation.release()

    def record_stopping(self):
        if not self._operation.acquire(blocking=False):
            raise JournalBlocked('RESERVATION_BUSY')
        try:
            state = self.inspect()
            if state['state'] != 'ACTIVE':
                raise JournalBlocked('STOPPING_REQUIRES_ACTIVE')
            self._persist('STOPPING', state['identity'])
        finally:
            self._operation.release()

    def _persist(self, state, identity):
        raw = json.dumps({'schema_version': 'reservation-journal/v1',
                          'state': state, 'identity': identity},
                         allow_nan=False, sort_keys=True).encode('utf-8')
        if len(raw) > MAX_BYTES:
            raise JournalBlocked('STATE_TOO_LARGE')
        name = '.pending-' + uuid.uuid4().hex
        created = False
        try:
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=self._directory)
            created = True
            try:
                with os.fdopen(fd, 'wb', closefd=False) as output:
                    output.write(raw)
                    output.flush()
                    os.fsync(fd)
            finally:
                os.close(fd)
            os.replace(name, 'state.json', src_dir_fd=self._directory, dst_dir_fd=self._directory)
            os.fsync(self._directory)
        except (OSError, ValueError) as error:
            self._failed = True
            blocked = JournalBlocked('RESERVATION_NOT_CONFIRMED')
            if created:
                try:
                    os.unlink(name, dir_fd=self._directory)
                except FileNotFoundError:
                    pass  # Replacement may already have consumed the temporary name.
                except OSError as cleanup_error:
                    blocked.add_note('CLEANUP_FAILED: errno=' + str(cleanup_error.errno))
            raise blocked from error
