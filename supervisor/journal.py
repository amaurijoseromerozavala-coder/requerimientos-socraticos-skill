"""Cooperative Linux reservation ledger, not launch admission or recovery.

An unresolved reservation never resets automatically. Trusted callers supply
identity metadata; this module does not authenticate it or reserve disk capacity.
Durability relies on the filesystem honoring fsync. Account/root changes and
arbitrary descendants are outside the single-owner trust boundary.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import threading
import uuid

MAX_BYTES = 16384
ACCOUNTING_MAX_BYTES = 32768
RUN_CAPACITY = 100
TOTAL_CAPACITY = 33554432
RUN_RESERVATION = 335872
STDOUT_CAPACITY = 262144
STDERR_CAPACITY = 65536
RECEIPT_CAPACITY = 8192
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
    if doc['state'] in ('ACTIVE', 'STOPPING', 'CONFIRMED_TERMINATED'):
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
            fd = os.open('accounting.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=directory)
            try:
                os.write(fd, b'{"schema_version":"run-accounting/v1","runs":[]}\n')
                os.fsync(fd)
            finally:
                os.close(fd)
            os.mkdir('runs', 0o700, dir_fd=directory)
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
            state = self.inspect()
            account = self.accounting()
            if state['state'] == 'CONFIRMED_TERMINATED' and any(
                    row['run_id'] == state['identity']['run_id'] and row['state'] == 'STORED'
                    for row in account['runs']):
                self.reconcile_terminated()
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
        account = self.accounting()
        if any(row['state'] == 'RESERVED' for row in account['runs']):
            raise JournalBlocked('UNRESOLVED_ACCOUNTING_RESERVATION')
        if any(row['run_id'] == identity['run_id'] for row in account['runs']):
            raise JournalBlocked('RUN_ID_ALREADY_USED')
        if (len(account['runs']) + 1 > RUN_CAPACITY
                or (len(account['runs']) + 1) * RUN_RESERVATION > TOTAL_CAPACITY):
            raise JournalBlocked('RETENTION_CAPACITY_EXCEEDED')
        try:
            volume = os.fstatvfs(self._directory)
            if volume.f_bavail * volume.f_frsize < RUN_RESERVATION:
                raise JournalBlocked('VISIBLE_STORAGE_INSUFFICIENT')
        except OSError as error:
            raise JournalBlocked('STORAGE_CAPACITY_UNAVAILABLE') from error
        account['runs'].append({'run_id': identity['run_id'], 'slot': uuid.uuid4().hex,
                                'state': 'RESERVED'})
        self._persist_accounting(account)
        self._persist('RESERVED', identity)

    def accounting(self):
        if self._failed or self._lock is None or self._directory is None:
            raise JournalBlocked('NO_ACTIVE_LEASE')
        try:
            with os.scandir(self._directory) as entries:
                if {entry.name for entry in entries} != {
                        'owner.lock', 'state.json', 'accounting.json', 'runs'}:
                    raise JournalBlocked('UNACCOUNTED_ROOT_ARTIFACT')
            fd = os.open('accounting.json', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=self._directory)
            try:
                if _regular(fd).st_size > ACCOUNTING_MAX_BYTES:
                    raise JournalBlocked('ACCOUNTING_TOO_LARGE')
                raw = os.read(fd, ACCOUNTING_MAX_BYTES + 1)
            finally:
                os.close(fd)
            if len(raw) > ACCOUNTING_MAX_BYTES:
                raise JournalBlocked('ACCOUNTING_TOO_LARGE')
            doc = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs)
            if (not isinstance(doc, dict) or set(doc) != {'schema_version', 'runs'}
                    or doc['schema_version'] != 'run-accounting/v1'
                    or not isinstance(doc['runs'], list) or len(doc['runs']) > RUN_CAPACITY
                    or len(doc['runs']) * RUN_RESERVATION > TOTAL_CAPACITY):
                raise JournalBlocked('INVALID_ACCOUNTING')
            names = set(); ids = set()
            for row in doc['runs']:
                if (not isinstance(row, dict) or set(row) != {'run_id', 'slot', 'state'}
                        or not isinstance(row['run_id'], str)
                        or not 1 <= len(row['run_id']) <= 256
                        or re.fullmatch('[0-9a-f]{32}', row['slot']) is None
                        or row['state'] not in ('RESERVED', 'STORED')
                        or row['run_id'] in ids or row['slot'] in names):
                    raise JournalBlocked('INVALID_ACCOUNTING')
                names.add(row['slot']); ids.add(row['run_id'])
            directory = os.open('runs', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=self._directory)
            try:
                info = os.fstat(directory)
                if info.st_uid != os.getuid() or info.st_mode & 0o077:
                    raise JournalBlocked('PRIVATE_RUN_DIRECTORY_REQUIRED')
                with os.scandir(directory) as entries:
                    for entry in entries:
                        if entry.name not in names or not entry.is_dir(follow_symlinks=False):
                            raise JournalBlocked('UNACCOUNTED_ARTIFACT')
            finally:
                os.close(directory)
            return doc
        except (OSError, ValueError, TypeError, UnicodeError, RecursionError, JournalBlocked) as error:
            self._failed = True
            raise JournalBlocked('ACCOUNTING_UNAVAILABLE') from error

    def _persist_accounting(self, doc):
        raw = json.dumps(doc, sort_keys=True, allow_nan=False).encode('utf-8')
        if len(raw) > ACCOUNTING_MAX_BYTES:
            raise JournalBlocked('ACCOUNTING_TOO_LARGE')
        self._write_atomic('accounting.json', raw)

    def store_capture(self, pid, start, returncode, stdout, stderr, complete):
        if not self._operation.acquire(blocking=False):
            raise JournalBlocked('RESERVATION_BUSY')
        try:
            state = self.inspect()
            if (state['state'] != 'CONFIRMED_TERMINATED'
                    or state['identity']['pid'] != pid
                    or state['identity']['process_start_identity'] != start):
                raise JournalBlocked('CAPTURE_IDENTITY_MISMATCH')
            if (not isinstance(stdout, bytes) or not isinstance(stderr, bytes)
                    or len(stdout) > STDOUT_CAPACITY or len(stderr) > STDERR_CAPACITY
                    or type(returncode) is not int or type(complete) is not bool):
                raise JournalBlocked('CAPTURE_LIMIT_OR_TYPE')
            account = self.accounting()
            rows = [row for row in account['runs'] if row['run_id'] == state['identity']['run_id']]
            if len(rows) != 1 or rows[0]['state'] != 'RESERVED':
                raise JournalBlocked('CAPTURE_NOT_RESERVED')
            slot = rows[0]['slot']
            receipt = json.dumps({
                'schema_version': 'process-receipt/v1', 'run_id': rows[0]['run_id'],
                'pid': pid, 'process_start_identity': start, 'returncode': returncode,
                'capture_complete': complete,
                'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
                'stderr_sha256': hashlib.sha256(stderr).hexdigest(),
                'stdout_bytes': len(stdout), 'stderr_bytes': len(stderr),
            }, sort_keys=True).encode('utf-8')
            if len(receipt) > RECEIPT_CAPACITY:
                raise JournalBlocked('RECEIPT_TOO_LARGE')
            runs_fd = os.open('runs', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                              dir_fd=self._directory)
            try:
                os.mkdir(slot, 0o700, dir_fd=runs_fd)
                slot_fd = os.open(slot, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                  dir_fd=runs_fd)
                try:
                    for name, data in (('stdout.bin', stdout), ('stderr.bin', stderr),
                                       ('receipt.json', receipt)):
                        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                     0o600, dir_fd=slot_fd)
                        try:
                            with os.fdopen(fd, 'wb', closefd=False) as output:
                                output.write(data)
                                output.flush()
                                os.fsync(fd)
                        finally:
                            os.close(fd)
                    os.fsync(slot_fd)
                finally:
                    os.close(slot_fd)
                os.fsync(runs_fd)
            finally:
                os.close(runs_fd)
            rows[0]['state'] = 'STORED'
            self._persist_accounting(account)
        finally:
            self._operation.release()

    def reconcile_terminated(self):
        if not self._operation.acquire(blocking=False):
            raise JournalBlocked('RESERVATION_BUSY')
        try:
            state = self.inspect()
            if state['state'] != 'CONFIRMED_TERMINATED':
                raise JournalBlocked('TERMINAL_STATE_REQUIRED')
            account = self.accounting()
            rows = [row for row in account['runs'] if row['run_id'] == state['identity']['run_id']]
            if len(rows) != 1 or rows[0]['state'] != 'STORED':
                raise JournalBlocked('DURABLE_CAPTURE_REQUIRED')
            runs_fd = os.open('runs', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                              dir_fd=self._directory)
            try:
                slot_fd = os.open(rows[0]['slot'], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                  dir_fd=runs_fd)
                try:
                    captured = {}
                    for name, limit in (('stdout.bin', STDOUT_CAPACITY),
                                        ('stderr.bin', STDERR_CAPACITY), ('receipt.json', RECEIPT_CAPACITY)):
                        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                                     dir_fd=slot_fd)
                        try:
                            if _regular(fd).st_size > limit:
                                raise JournalBlocked('CAPTURE_TOO_LARGE')
                            captured[name] = os.read(fd, limit + 1)
                            if len(captured[name]) > limit:
                                raise JournalBlocked('CAPTURE_TOO_LARGE')
                        finally:
                            os.close(fd)
                finally:
                    os.close(slot_fd)
            finally:
                os.close(runs_fd)
            receipt = json.loads(captured['receipt.json'].decode('utf-8'), object_pairs_hook=_pairs)
            if (not isinstance(receipt, dict) or receipt.get('schema_version') != 'process-receipt/v1'
                    or receipt.get('run_id') != rows[0]['run_id']
                    or receipt.get('pid') != state['identity']['pid']
                    or receipt.get('process_start_identity') != state['identity']['process_start_identity']
                    or any(receipt.get(name + '_bytes') != len(captured[name + '.bin'])
                           or receipt.get(name + '_sha256') != hashlib.sha256(captured[name + '.bin']).hexdigest()
                           for name in ('stdout', 'stderr'))):
                raise JournalBlocked('CAPTURE_RECEIPT_MISMATCH')
            self._persist('IDLE', None)
        finally:
            self._operation.release()

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

    def record_terminated(self, pid, process_start_identity):
        """Persist a trusted caller's exact-child termination observation."""
        if not self._operation.acquire(blocking=False):
            raise JournalBlocked('RESERVATION_BUSY')
        try:
            state = self.inspect()
            if state['state'] not in ('ACTIVE', 'STOPPING'):
                raise JournalBlocked('TERMINATION_REQUIRES_ACTIVE_PROCESS')
            identity = state['identity']
            if (type(pid) is not int or pid != identity['pid']
                    or process_start_identity != identity['process_start_identity']):
                raise JournalBlocked('PROCESS_IDENTITY_MISMATCH')
            self._persist('CONFIRMED_TERMINATED', identity)
        finally:
            self._operation.release()

    def _persist(self, state, identity):
        raw = json.dumps({'schema_version': 'reservation-journal/v1',
                          'state': state, 'identity': identity},
                         allow_nan=False, sort_keys=True).encode('utf-8')
        if len(raw) > MAX_BYTES:
            raise JournalBlocked('STATE_TOO_LARGE')
        self._write_atomic('state.json', raw)

    def _write_atomic(self, target, raw):
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
            os.replace(name, target, src_dir_fd=self._directory, dst_dir_fd=self._directory)
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
