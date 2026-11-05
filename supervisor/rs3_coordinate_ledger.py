"""Private, bounded coordinate reservation ledger without codes or authority.

Reserve before a future human code prompt. A pending coordinate survives restart
and can only be burned, never returned to AVAILABLE. This module does not check
codes, authenticate callers, issue receipts, or establish the D05 account wall.
"""

from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import stat


MAX_BYTES = 32768
MAX_COORDINATES = 128
SCHEMA = 'rs3-coordinate-ledger/v1'


class LedgerBlocked(RuntimeError):
    pass


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True).encode('ascii') + b'\n'


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise LedgerBlocked('DUPLICATE_KEY')
        result[key] = value
    return result


def _id(value, limit):
    return type(value) is str and re.fullmatch(
        r'[A-Za-z0-9_.-]{1,' + str(limit) + r'}', value) is not None


def _digest(value):
    return type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def _validate(doc):
    if (type(doc) is not dict or set(doc) != {'schema', 'card_id', 'coordinates'}
            or doc['schema'] != SCHEMA or not _id(doc['card_id'], 64)
            or type(doc['coordinates']) is not dict
            or not 1 <= len(doc['coordinates']) <= MAX_COORDINATES):
        raise LedgerBlocked('INVALID_LEDGER')
    for coordinate, record in doc['coordinates'].items():
        if (not _id(coordinate, 32) or type(record) is not dict
                or set(record) != {'state', 'challenge_sha256'}):
            raise LedgerBlocked('INVALID_COORDINATE')
        if record['state'] == 'AVAILABLE' and record['challenge_sha256'] is None:
            continue
        if record['state'] in ('PENDING', 'SPENT') and _digest(record['challenge_sha256']):
            continue
        raise LedgerBlocked('INVALID_COORDINATE_STATE')
    return doc


def _private_regular(fd):
    info = os.fstat(fd)
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600):
        raise LedgerBlocked('PRIVATE_FILE_REQUIRED')
    return info


def _result(state, coordinate, digest):
    return {'state': state, 'coordinate': coordinate,
            'challenge_sha256': digest,
            'authority_verification': 'NOT_ESTABLISHED',
            'execution_authorized': False}


class CoordinateLedger:
    def __init__(self, root):
        self.root = Path(root).absolute()

    @classmethod
    def initialize(cls, root, *, card_id, coordinates):
        """Initialize once. Partial initialization remains blocked."""
        if (not _id(card_id, 64) or type(coordinates) is not list
                or not 1 <= len(coordinates) <= MAX_COORDINATES
                or any(not _id(value, 32) for value in coordinates)
                or len(set(coordinates)) != len(coordinates)):
            raise LedgerBlocked('INVALID_INITIALIZATION')
        doc = _validate({'schema': SCHEMA, 'card_id': card_id,
                         'coordinates': {key: {'state': 'AVAILABLE',
                                               'challenge_sha256': None}
                                         for key in coordinates}})
        raw = _encode(doc)
        if len(raw) > MAX_BYTES:
            raise LedgerBlocked('CAPACITY_EXCEEDED')
        root = Path(root).absolute()
        try:
            os.mkdir(root, 0o700)
            directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                for name, data in (('owner.lock', b''), ('state.json', raw)):
                    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                 os.O_NOFOLLOW, 0o600, dir_fd=directory)
                    try:
                        if os.write(fd, data) != len(data):
                            raise LedgerBlocked('INCOMPLETE_WRITE')
                        os.fsync(fd)
                    finally:
                        os.close(fd)
                os.fsync(directory)
            finally:
                os.close(directory)
            parent = os.open(root.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
        except OSError as error:
            raise LedgerBlocked('INITIALIZATION_UNAVAILABLE') from error

    @contextmanager
    def _locked(self):
        directory = None
        lock = None
        try:
            directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            info = os.fstat(directory)
            if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
                raise LedgerBlocked('PRIVATE_DIRECTORY_REQUIRED')
            lock = os.open('owner.lock', os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK,
                           dir_fd=directory)
            _private_regular(lock)
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield directory
        except OSError as error:
            raise LedgerBlocked('STORE_UNAVAILABLE') from error
        finally:
            if lock is not None:
                os.close(lock)
            if directory is not None:
                os.close(directory)

    def _stage_present(self, directory):
        try:
            info = os.stat('state.stage', dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            return False
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600
                or info.st_size > MAX_BYTES):
            raise LedgerBlocked('UNSAFE_STAGE')
        return True

    def _read(self, directory):
        fd = os.open('state.json', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=directory)
        try:
            size = _private_regular(fd).st_size
            if size < 1 or size > MAX_BYTES:
                raise LedgerBlocked('CAPACITY_EXCEEDED')
            raw = os.read(fd, MAX_BYTES + 1)
            if len(raw) != size or not raw.endswith(b'\n'):
                raise LedgerBlocked('INCOMPLETE_STATE')
        finally:
            os.close(fd)
        try:
            doc = json.loads(raw.decode('ascii'), object_pairs_hook=_pairs)
            _validate(doc)
            if _encode(doc) != raw:
                raise LedgerBlocked('NONCANONICAL_STATE')
            return doc
        except (ValueError, TypeError, UnicodeError, RecursionError) as error:
            raise LedgerBlocked('INVALID_STATE') from error

    def _write(self, directory, doc):
        raw = _encode(_validate(doc))
        if len(raw) > MAX_BYTES:
            raise LedgerBlocked('CAPACITY_EXCEEDED')
        fd = os.open('state.stage', os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     os.O_NOFOLLOW, 0o600, dir_fd=directory)
        try:
            if os.write(fd, raw) != len(raw):
                raise LedgerBlocked('INCOMPLETE_WRITE')
            os.fsync(fd)
        finally:
            os.close(fd)
        os.replace('state.stage', 'state.json', src_dir_fd=directory,
                   dst_dir_fd=directory)
        os.fsync(directory)

    def snapshot(self):
        with self._locked() as directory:
            if self._stage_present(directory):
                raise LedgerBlocked('STAGE_RECONCILIATION_REQUIRED')
            doc = self._read(directory)
            return {**doc, 'authority_verification': 'NOT_ESTABLISHED',
                    'execution_authorized': False}

    def reserve(self, coordinate, challenge_sha256):
        if not _id(coordinate, 32) or not _digest(challenge_sha256):
            raise LedgerBlocked('INVALID_REQUEST')
        with self._locked() as directory:
            if self._stage_present(directory):
                raise LedgerBlocked('STAGE_RECONCILIATION_REQUIRED')
            doc = self._read(directory)
            entry = doc['coordinates'].get(coordinate)
            if entry is None or entry['state'] != 'AVAILABLE':
                raise LedgerBlocked('COORDINATE_UNAVAILABLE')
            entry['state'], entry['challenge_sha256'] = 'PENDING', challenge_sha256
            self._write(directory, doc)
            return _result('PENDING', coordinate, challenge_sha256)

    def spend_pending(self, coordinate, challenge_sha256):
        if not _id(coordinate, 32) or not _digest(challenge_sha256):
            raise LedgerBlocked('INVALID_REQUEST')
        with self._locked() as directory:
            if self._stage_present(directory):
                raise LedgerBlocked('STAGE_RECONCILIATION_REQUIRED')
            doc = self._read(directory)
            entry = doc['coordinates'].get(coordinate)
            if (entry is None or entry['state'] != 'PENDING'
                    or entry['challenge_sha256'] != challenge_sha256):
                raise LedgerBlocked('PENDING_MATCH_REQUIRED')
            entry['state'] = 'SPENT'
            self._write(directory, doc)
            return _result('SPENT', coordinate, challenge_sha256)

    def reconcile_stage(self):
        """Discard an uncommitted stage only after validating the main state.

        PENDING remains PENDING; this does not authorize reuse or infer success.
        """
        with self._locked() as directory:
            if not self._stage_present(directory):
                raise LedgerBlocked('NO_STAGE')
            self._read(directory)
            os.unlink('state.stage', dir_fd=directory)
            os.fsync(directory)
            return {'status': 'STAGE_DISCARDED',
                    'authority_verification': 'NOT_ESTABLISHED',
                    'execution_authorized': False}
