"""Bounded local documentary audit log; never an authority or deployment gate.

The hash chain detects inconsistent surviving bytes or a partial final line.
Removing complete trailing records produces a valid prefix and is undetectable
without an external checkpoint. This module cannot authenticate an actor with
write access to the same account.
"""

import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat


DEFAULT_MAX_BYTES = 1024 * 1024
KINDS = frozenset({'PROPOSAL_RECORDED', 'MODEL_CHECK_RECORDED',
                   'REVIEW_REQUESTED', 'REVIEW_OBSERVED',
                   'PASSWORD_CHECK_ACCEPTED', 'PASSWORD_CHECK_REJECTED'})
ZERO_HASH = '0' * 64


class AuditBlocked(RuntimeError):
    pass


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True).encode('ascii')


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AuditBlocked('DUPLICATE_KEY')
        result[key] = value
    return result


def _event(value):
    if not isinstance(value, dict) or set(value) != {'kind', 'ref', 'subject_sha256'}:
        raise AuditBlocked('INVALID_EVENT_FIELDS')
    if not isinstance(value['kind'], str) or value['kind'] not in KINDS:
        raise AuditBlocked('UNSUPPORTED_EVENT_KIND')
    if not isinstance(value['ref'], str) or re.fullmatch(r'[A-Za-z0-9_.-]{1,64}', value['ref']) is None:
        raise AuditBlocked('INVALID_REFERENCE')
    if not isinstance(value['subject_sha256'], str) or re.fullmatch(r'[0-9a-f]{64}', value['subject_sha256']) is None:
        raise AuditBlocked('INVALID_SUBJECT_DIGEST')


class AuditLog:
    def __init__(self, root, *, max_bytes=DEFAULT_MAX_BYTES):
        if type(max_bytes) is not int or not 1 <= max_bytes <= DEFAULT_MAX_BYTES:
            raise AuditBlocked('INVALID_CAPACITY')
        self.root = Path(root).absolute()
        self.max_bytes = max_bytes

    @classmethod
    def initialize(cls, root):
        """Create once; never reset or repair an existing store."""
        root = Path(root).absolute()
        os.mkdir(root, 0o700)
        directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            info = os.fstat(directory)
            if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
                raise AuditBlocked('PRIVATE_DIRECTORY_REQUIRED')
            fd = os.open('events.jsonl', os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         os.O_NOFOLLOW, 0o600, dir_fd=directory)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            os.fsync(directory)
        finally:
            os.close(directory)

    def _open(self):
        try:
            directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                info = os.fstat(directory)
                if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
                    raise AuditBlocked('PRIVATE_DIRECTORY_REQUIRED')
                fd = os.open('events.jsonl', os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=directory)
                try:
                    info = os.fstat(fd)
                    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                            or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600):
                        raise AuditBlocked('PRIVATE_REGULAR_FILE_REQUIRED')
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return fd
                except BaseException:
                    os.close(fd)
                    raise
            finally:
                os.close(directory)
        except OSError as error:
            raise AuditBlocked('STORE_UNAVAILABLE') from error

    def _read(self, fd):
        size = os.fstat(fd).st_size
        if size > self.max_bytes:
            raise AuditBlocked('CAPACITY_EXCEEDED')
        os.lseek(fd, 0, os.SEEK_SET)
        raw = os.read(fd, self.max_bytes + 1)
        if len(raw) != size or len(raw) > self.max_bytes or (raw and not raw.endswith(b'\n')):
            raise AuditBlocked('INCOMPLETE_LOG')
        rows = []
        previous = ZERO_HASH
        for line in raw.splitlines():
            try:
                row = json.loads(line, object_pairs_hook=_unique)
                if _encode(row) != line or set(row) != {'sequence', 'event', 'prev_sha256',
                                                         'authority_verification',
                                                         'execution_authorized', 'sha256'}:
                    raise AuditBlocked('INVALID_RECORD')
                _event(row['event'])
                if (type(row['sequence']) is not int or row['sequence'] != len(rows) + 1
                        or row['prev_sha256'] != previous
                        or row['authority_verification'] != 'NOT_PERFORMED'
                        or row['execution_authorized'] is not False):
                    raise AuditBlocked('INCOHERENT_RECORD')
                body = {key: value for key, value in row.items() if key != 'sha256'}
                digest = hashlib.sha256(_encode(body)).hexdigest()
                if row['sha256'] != digest:
                    raise AuditBlocked('INTEGRITY_MISMATCH')
                previous = digest
                rows.append(row)
            except (ValueError, TypeError, UnicodeError, RecursionError) as error:
                raise AuditBlocked('INVALID_RECORD') from error
        return rows, size

    def read_all(self):
        fd = self._open()
        try:
            rows, _ = self._read(fd)
            return rows
        finally:
            os.close(fd)

    def append(self, event, *, unique_ref=False):
        _event(event)
        fd = self._open()
        try:
            rows, size = self._read(fd)
            if unique_ref and any(row['event']['ref'] == event['ref'] for row in rows):
                raise AuditBlocked('DUPLICATE_REFERENCE')
            body = {'sequence': len(rows) + 1, 'event': dict(event),
                    'prev_sha256': rows[-1]['sha256'] if rows else ZERO_HASH,
                    'authority_verification': 'NOT_PERFORMED',
                    'execution_authorized': False}
            record = {**body, 'sha256': hashlib.sha256(_encode(body)).hexdigest()}
            line = _encode(record) + b'\n'
            if size + len(line) > self.max_bytes:
                raise AuditBlocked('CAPACITY_EXCEEDED')
            os.lseek(fd, 0, os.SEEK_END)
            if os.write(fd, line) != len(line):
                raise AuditBlocked('INCOMPLETE_WRITE')
            os.fsync(fd)
            return record
        finally:
            os.close(fd)
