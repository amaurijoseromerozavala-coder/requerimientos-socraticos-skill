#!/usr/bin/env python3
"""Private POSIX custody for proposed questions and unverified replies."""

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import select
import stat
import subprocess
import sys
import time
import unicodedata

from record_interrogation import (_read_json, _read_response, respond, start)
from render_gap_questions import _unique_object
from json_preflight import preflight_json


SESSION = re.compile(r'^[0-9a-f]{32}$')
MAX_STORED = 1024 * 1024
WRITE_DEADLINE_SECONDS = 3.0
FILE_FLAGS = os.O_CLOEXEC | os.O_NOFOLLOW
DELIVERY_KEYS = {'schema_version', 'status', 'session_id',
                 'question_sha256', 'bytes_sha256', 'byte_count',
                 'human_viewed', 'authority_verification'}


def _root_fd(root):
    path = Path(root).absolute()
    if '..' in path.parts:
        raise ValueError('UNSAFE_PRIVATE_ROOT')
    for component in (path, *path.parents):
        if component.is_symlink():
            raise ValueError('SYMLINK_PRIVATE_ROOT')
        marker = component / '.git'
        if marker.exists() or marker.is_symlink():
            raise ValueError('PRIVATE_ROOT_IN_GIT')
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | FILE_FLAGS)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid()
                or stat.S_IMODE(info.st_mode) != 0o700):
            raise ValueError('INSECURE_PRIVATE_ROOT')
        environment = {key: value for key, value in os.environ.items()
                       if not key.startswith('GIT_')}
        environment['GIT_OPTIONAL_LOCKS'] = '0'
        probe = subprocess.run(['git', '-C', str(path), 'rev-parse',
                                '--is-inside-work-tree'], capture_output=True,
                               timeout=2, env=environment)
        if probe.returncode not in (0, 128):
            raise ValueError('GIT_LOCATION_UNVERIFIED')
        if probe.returncode == 0:
            raise ValueError('PRIVATE_ROOT_IN_GIT')
        return fd
    except BaseException:
        os.close(fd)
        raise


def _regular(fd):
    info = os.fstat(fd)
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1):
        raise ValueError('INSECURE_PRIVATE_FILE')


@contextmanager
def _locked(root):
    directory = _root_fd(root)
    lock = None
    try:
        lock = os.open('.history.lock', os.O_RDWR | os.O_CREAT | FILE_FLAGS,
                       0o600, dir_fd=directory)
        _regular(lock)
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield directory
    finally:
        if lock is not None:
            os.close(lock)
        os.close(directory)


def _filename(session, prefix):
    if type(session) is not str or not SESSION.fullmatch(session):
        raise ValueError('INVALID_SESSION_ID')
    return prefix + '-' + session + '.json'


def _json_bytes(value):
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')
    if len(raw) > MAX_STORED:
        raise ValueError('STORE_SIZE_LIMIT')
    return raw


def _create(directory, name, raw):
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | FILE_FLAGS,
                 0o600, dir_fd=directory)
    try:
        _regular(fd)
        offset = 0
        while offset < len(raw):
            offset += os.write(fd, raw[offset:])
        os.fsync(fd)
        os.fsync(directory)
    except BaseException:
        os.close(fd)
        os.unlink(name, dir_fd=directory)
        raise
    os.close(fd)


def _publish_exclusive(directory, name, raw):
    """Write and sync privately before linking the final name without overwrite."""
    session = name.removeprefix('delivery-').removesuffix('.json')
    staging = _filename(session, 'stage')
    _create(directory, staging, raw)
    try:
        os.link(staging, name, src_dir_fd=directory,
                dst_dir_fd=directory, follow_symlinks=False)
        os.fsync(directory)
    finally:
        try:
            os.unlink(staging, dir_fd=directory)
        except FileNotFoundError:
            pass
        os.fsync(directory)


def _reconcile_delivery_stage(directory, session):
    """Under the root lock, remove a private interrupted stage safely."""
    staging = _filename(session, 'stage')
    try:
        info = os.stat(staging, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_nlink not in (1, 2)):
        raise ValueError('UNSAFE_DELIVERY_STAGE')
    if info.st_nlink == 2:
        final = os.stat(_filename(session, 'delivery'), dir_fd=directory,
                        follow_symlinks=False)
        if (not stat.S_ISREG(final.st_mode)
                or (final.st_dev, final.st_ino) != (info.st_dev, info.st_ino)):
            raise ValueError('UNMATCHED_DELIVERY_STAGE')
    os.unlink(staging, dir_fd=directory)
    os.fsync(directory)


def _read(directory, name):
    fd = os.open(name, os.O_RDONLY | os.O_NONBLOCK | FILE_FLAGS,
                 dir_fd=directory)
    try:
        _regular(fd)
        size = os.fstat(fd).st_size
        if size > MAX_STORED:
            raise ValueError('STORE_SIZE_LIMIT')
        chunks = []
        remaining = MAX_STORED + 1
        while remaining:
            chunk = os.read(fd, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b''.join(chunks)
        preflight_json(raw, max_depth=32, max_bytes=MAX_STORED)
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              ValueError('NONFINITE_JSON_NUMBER')))
    finally:
        os.close(fd)


def _checked_history(directory, session):
    history = _read(directory, _filename(session, 'session'))
    if (type(history) is not dict or type(history.get('events')) is not list
            or not history['events'] or type(history['events'][0]) is not dict):
        raise ValueError('INVALID_STORED_HISTORY')
    handoff = history['events'][0].get('handoff')
    expected = start(handoff)
    if history.get('execution_authorized') is not False:
        raise ValueError('INVALID_AUTHORITY_FIELD')
    if history == expected:
        return history
    if (len(history['events']) == 2
            and type(history['events'][1]) is dict
            and type(history['events'][1].get('text')) is str):
        if history == respond(expected, history['events'][1]['text']):
            return history
    raise ValueError('INVALID_STORED_HISTORY')


def create(root, handoff):
    history = start(handoff)
    with _locked(root) as directory:
        session = secrets.token_hex(16)
        _create(directory, _filename(session, 'session'), _json_bytes(history))
    return session


def load(root, session):
    with _locked(root) as directory:
        return _checked_history(directory, session)


def _presentation(history):
    question = history['events'][0]['handoff']['question']
    lines = ['Escenario propuesto; ninguna decisión queda confirmada.']
    for clause in question['scenario_clauses']:
        value = 'verdadero' if clause['value'] else 'falso'
        phrase = ''.join(
            (f'\\u{ord(char):04x}' if ord(char) <= 0xffff
             else f'\\U{ord(char):08x}')
            if unicodedata.category(char) in ('Cc', 'Cf') else char
            for char in clause['proposed_phrase'])
        lines.append(f"{clause['variable']} = {value}: {phrase}")
    lines.append(question['text'])
    raw = ('\n'.join(lines) + '\n').encode('utf-8')
    if len(raw) > 32768:
        raise ValueError('PRESENTATION_SIZE_LIMIT')
    return raw


def _write_tty(fd, raw):
    if not os.isatty(fd):
        raise ValueError('TTY_REQUIRED')
    previous = os.get_blocking(fd)
    deadline = time.monotonic() + WRITE_DEADLINE_SECONDS
    offset = 0
    try:
        os.set_blocking(fd, False)
        while offset < len(raw):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('TTY_WRITE_LIMIT')
            if not select.select([], [fd], [], remaining)[1]:
                raise TimeoutError('TTY_WRITE_LIMIT')
            try:
                offset += os.write(fd, raw[offset:])
            except BlockingIOError:
                continue
    finally:
        os.set_blocking(fd, previous)


def deliver(root, session, fd):
    """Record successful kernel TTY write, never human perception."""
    with _locked(root) as directory:
        history = _checked_history(directory, session)
        if history['state'] != 'WAITING_USER':
            raise ValueError('NOT_WAITING_USER')
        _reconcile_delivery_stage(directory, session)
        name = _filename(session, 'delivery')
        try:
            os.stat(name, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ValueError('ALREADY_DELIVERED')
        raw = _presentation(history)
        _write_tty(fd, raw)
        receipt = {'schema_version': 'rs3-tty-delivery/v1',
                   'status': 'TTY_WRITE_COMPLETED', 'session_id': session,
                   'question_sha256': history['events'][0]['question_sha256'],
                   'bytes_sha256': hashlib.sha256(raw).hexdigest(),
                   'byte_count': len(raw), 'human_viewed': False,
                   'authority_verification': 'NOT_ESTABLISHED'}
        _publish_exclusive(directory, name, _json_bytes(receipt))
        return receipt


def record_response(root, session, text):
    with _locked(root) as directory:
        history = _checked_history(directory, session)
        if history['state'] != 'WAITING_USER':
            raise ValueError('RESPONSE_ALREADY_RECORDED')
        _reconcile_delivery_stage(directory, session)
        try:
            receipt = _read(directory, _filename(session, 'delivery'))
        except FileNotFoundError as error:
            raise ValueError('DELIVERY_NOT_OBSERVED') from error
        expected = _presentation(history)
        if (type(receipt) is not dict or set(receipt) != DELIVERY_KEYS
                or receipt.get('schema_version') != 'rs3-tty-delivery/v1'
                or receipt.get('status') != 'TTY_WRITE_COMPLETED'
                or receipt.get('session_id') != session
                or receipt.get('question_sha256')
                != history['events'][0]['question_sha256']
                or receipt.get('bytes_sha256') != hashlib.sha256(expected).hexdigest()
                or receipt.get('byte_count') != len(expected)
                or receipt.get('human_viewed') is not False
                or receipt.get('authority_verification') != 'NOT_ESTABLISHED'):
            raise ValueError('INVALID_DELIVERY_RECEIPT')
        updated = respond(history, text)
        temporary = 'update-' + secrets.token_hex(16) + '.json'
        _create(directory, temporary, _json_bytes(updated))
        try:
            os.replace(temporary, _filename(session, 'session'),
                       src_dir_fd=directory, dst_dir_fd=directory)
            os.fsync(directory)
        finally:
            try:
                os.unlink(temporary, dir_fd=directory)
            except FileNotFoundError:
                pass
        return updated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='mode', required=True)
    create_parser = modes.add_parser('create')
    create_parser.add_argument('private_root')
    create_parser.add_argument('handoff')
    present_parser = modes.add_parser('present')
    present_parser.add_argument('private_root')
    present_parser.add_argument('session_id')
    reply_parser = modes.add_parser('respond')
    reply_parser.add_argument('private_root')
    reply_parser.add_argument('session_id')
    reply_parser.add_argument('--response-file', required=True)
    args = parser.parse_args()
    try:
        if args.mode == 'create':
            session = create(args.private_root, _read_json(args.handoff))
            print(json.dumps({'status': 'PRIVATE_RECORD_CREATED',
                              'session_id': session}))
        elif args.mode == 'present':
            deliver(args.private_root, args.session_id, sys.stdout.fileno())
        else:
            updated = record_response(args.private_root, args.session_id,
                                      _read_response(args.response_file))
            print(json.dumps({'status': updated['state'],
                              'session_id': args.session_id,
                              'authority_verification': 'NOT_ESTABLISHED',
                              'execution_authorized': False}))
        return 0
    except (ValueError, OSError, TimeoutError, UnicodeError, RecursionError,
            subprocess.TimeoutExpired):
        print('PRIVATE_HISTORY_FAILURE', file=sys.stderr)
        return 2
    except MemoryError:
        print('INFRA_FAILURE', file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
