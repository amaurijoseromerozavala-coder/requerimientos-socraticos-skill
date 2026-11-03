"""Manual terminal adapter for the non-authoritative RS3 PBKDF2 auditor.

Invoke directly from a trusted local terminal under the separately protected
account once that boundary is verified. This adapter never accepts a password
from argv, stdin, an environment variable, or a decision file.
"""

import argparse
import json
import os
from pathlib import Path
import re
import secrets
import select
import stat
import sys
import termios
import time
import unicodedata

from supervisor.rs3_password_auditor import PasswordAuditBlocked, PasswordAuditor


FILE_MAX_BYTES = 8192
PASSWORD_MAX_BYTES = 2048
ENTRY_DEADLINE_SECONDS = 120


class ManualChannelBlocked(RuntimeError):
    pass


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManualChannelBlocked('DUPLICATE_KEY')
        result[key] = value
    return result


def load_decision(path):
    """Read one bounded snapshot; the later display and check use this object."""
    try:
        fd = os.open(Path(path), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_size > FILE_MAX_BYTES:
                raise ManualChannelBlocked('REGULAR_BOUNDED_FILE_REQUIRED')
            raw = os.read(fd, FILE_MAX_BYTES + 1)
            if len(raw) != info.st_size:
                raise ManualChannelBlocked('INCOMPLETE_DECISION_READ')
        finally:
            os.close(fd)
        doc = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique)
        if (not isinstance(doc, dict) or set(doc) != {'schema', 'proposal_id',
                'snapshot_sha256', 'decision_text'}
                or doc['schema'] != 'rs3-manual-decision/v1'
                or not isinstance(doc['proposal_id'], str)
                or re.fullmatch(r'[A-Za-z0-9_.-]{1,64}', doc['proposal_id']) is None
                or not isinstance(doc['snapshot_sha256'], str)
                or re.fullmatch(r'[0-9a-f]{64}', doc['snapshot_sha256']) is None
                or not isinstance(doc['decision_text'], str)
                or not 1 <= len(doc['decision_text'].encode('utf-8')) <= 4096
                or any(unicodedata.category(char) in ('Cc', 'Cf') and char not in '\n\t'
                       for char in doc['decision_text'])):
            raise ManualChannelBlocked('INVALID_DECISION')
        return doc
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        raise ManualChannelBlocked('DECISION_UNAVAILABLE') from error


def _open_tty():
    try:
        fd = os.open('/dev/tty', os.O_RDWR | os.O_NOCTTY | os.O_CLOEXEC)
        if not os.isatty(fd):
            os.close(fd)
            raise ManualChannelBlocked('TTY_REQUIRED')
        return fd
    except OSError as error:
        raise ManualChannelBlocked('TTY_REQUIRED') from error


def _close_tty(fd):
    os.close(fd)


def _write_tty(fd, raw):
    view = memoryview(raw)
    while view:
        count = os.write(fd, view)
        if count <= 0:
            raise ManualChannelBlocked('TTY_WRITE_FAILED')
        view = view[count:]


def _read_secret(fd, prompt=b'Contrasena para esta decision: '):
    """Read a bounded line with echo disabled; restore termios on exit."""
    try:
        original = termios.tcgetattr(fd)
        hidden = original.copy()
        hidden[3] &= ~(termios.ECHO | termios.ECHONL)
        termios.tcsetattr(fd, termios.TCSANOW, hidden)
        try:
            _write_tty(fd, prompt)
            deadline = time.monotonic() + ENTRY_DEADLINE_SECONDS
            result = bytearray()
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not select.select([fd], [], [], remaining)[0]:
                    raise ManualChannelBlocked('PASSWORD_ENTRY_TIMEOUT')
                byte = os.read(fd, 1)
                if byte in (b'\n', b'\r'):
                    break
                if not byte or len(result) >= PASSWORD_MAX_BYTES:
                    raise ManualChannelBlocked('INVALID_PASSWORD_ENTRY')
                result.extend(byte)
            _write_tty(fd, b'\n')
            return result.decode('utf-8')
        finally:
            termios.tcsetattr(fd, termios.TCSANOW, original)
    except (OSError, UnicodeError, ValueError, termios.error) as error:
        raise ManualChannelBlocked('TTY_UNAVAILABLE') from error


def run_check(root, decision_path):
    doc = load_decision(decision_path)
    fd = _open_tty()
    try:
        display = json.dumps(doc, ensure_ascii=False, indent=2).encode('utf-8')
        _write_tty(fd, b'Revise la decision exacta:\n' + display + b'\n')
        password = _read_secret(fd)
    finally:
        _close_tty(fd)
    return PasswordAuditor(root).check(
        proposal_id=doc['proposal_id'], snapshot_sha256=doc['snapshot_sha256'],
        decision_text=doc['decision_text'], nonce=secrets.token_hex(16),
        password=password)


def run_enroll(root):
    fd = _open_tty()
    try:
        first = _read_secret(fd, b'Nueva contrasena local: ')
        second = _read_secret(fd, b'Repetir contrasena local: ')
    finally:
        _close_tty(fd)
    try:
        same = secrets.compare_digest(first.encode('utf-8'), second.encode('utf-8'))
    except UnicodeError as error:
        raise ManualChannelBlocked('INVALID_PASSWORD_ENTRY') from error
    if not same:
        raise ManualChannelBlocked('ENROLLMENT_MISMATCH')
    PasswordAuditor.initialize(root, first)
    return {'status': 'ENROLLED', 'authority_verification': 'NOT_ESTABLISHED',
            'execution_authorized': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Auditoria local sin autoridad RS3')
    subparsers = parser.add_subparsers(dest='command', required=True)
    enroll = subparsers.add_parser('enroll')
    enroll.add_argument('--root', required=True)
    check = subparsers.add_parser('check')
    check.add_argument('--root', required=True)
    check.add_argument('--decision-file', required=True)
    args = parser.parse_args(argv)
    try:
        result = run_enroll(args.root) if args.command == 'enroll' else run_check(
            args.root, args.decision_file)
    except (ManualChannelBlocked, PasswordAuditBlocked) as error:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(error),
                          'authority_verification': 'NOT_ESTABLISHED',
                          'execution_authorized': False}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
