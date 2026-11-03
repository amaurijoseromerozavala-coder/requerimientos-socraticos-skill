"""Local PBKDF2 credential check with an audit event, without human authority.

The caller must supply a trusted human input channel and a separately protected
OS account before this can support a human confirmation workflow. Neither is
established by a password match alone. This module emits no authorization.
"""

import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import stat

from supervisor.rs3_audit_log import AuditBlocked, AuditLog


ITERATIONS = 600_000
VERIFIER_MAX_BYTES = 512
DECISION_MAX_BYTES = 4096
SCHEMA = 'rs3-pbkdf2-verifier/v2'


class PasswordAuditBlocked(RuntimeError):
    pass


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True).encode('ascii')


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PasswordAuditBlocked('DUPLICATE_KEY')
        result[key] = value
    return result


def _password_bytes(password, *, enrolling=False):
    if not isinstance(password, str) or len(password) > 1024:
        raise PasswordAuditBlocked('INVALID_CREDENTIAL_INPUT')
    try:
        raw = password.encode('utf-8')
    except UnicodeError as error:
        raise PasswordAuditBlocked('INVALID_CREDENTIAL_INPUT') from error
    if len(raw) > 2048 or (enrolling and (len(password) < 15 or not password)):
        raise PasswordAuditBlocked('INVALID_CREDENTIAL_INPUT')
    return raw


def _decision(proposal_id, snapshot_sha256, decision_text, nonce):
    if not isinstance(proposal_id, str) or re.fullmatch(r'[A-Za-z0-9_.-]{1,64}', proposal_id) is None:
        raise PasswordAuditBlocked('INVALID_PROPOSAL_ID')
    if not isinstance(snapshot_sha256, str) or re.fullmatch(r'[0-9a-f]{64}', snapshot_sha256) is None:
        raise PasswordAuditBlocked('INVALID_SNAPSHOT_DIGEST')
    if not isinstance(nonce, str) or re.fullmatch(r'[0-9a-f]{32}', nonce) is None:
        raise PasswordAuditBlocked('INVALID_NONCE')
    if not isinstance(decision_text, str) or not decision_text:
        raise PasswordAuditBlocked('INVALID_DECISION_TEXT')
    try:
        raw = decision_text.encode('utf-8')
    except UnicodeError as error:
        raise PasswordAuditBlocked('INVALID_DECISION_TEXT') from error
    if len(raw) > DECISION_MAX_BYTES or any(ord(c) < 32 and c not in '\n\t' for c in decision_text):
        raise PasswordAuditBlocked('INVALID_DECISION_TEXT')
    decision_sha256 = hashlib.sha256(raw).hexdigest()
    subject_sha256 = hashlib.sha256(_encode({
        'proposal_id': proposal_id, 'snapshot_sha256': snapshot_sha256,
        'decision_sha256': decision_sha256})).hexdigest()
    return decision_sha256, subject_sha256


class PasswordAuditor:
    def __init__(self, root):
        self.root = Path(root).absolute()

    @classmethod
    def initialize(cls, root, password, *, agent_uid):
        """One-time enrollment; partial stores remain blocked, never repaired."""
        authority_uid = os.getuid()
        if (type(agent_uid) is not int or agent_uid < 0 or agent_uid == authority_uid
                or os.geteuid() != authority_uid):
            raise PasswordAuditBlocked('SEPARATE_ACCOUNT_REQUIRED')
        raw = _password_bytes(password, enrolling=True)
        root = Path(root).absolute()
        try:
            AuditLog.initialize(root)
            salt = os.urandom(16)
            digest = hashlib.pbkdf2_hmac('sha256', raw, salt, ITERATIONS)
            payload = _encode({'schema': SCHEMA, 'iterations': ITERATIONS,
                               'authority_uid': authority_uid, 'agent_uid': agent_uid,
                               'salt_hex': salt.hex(), 'digest_hex': digest.hex()}) + b'\n'
            directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                fd = os.open('verifier.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             os.O_NOFOLLOW, 0o600, dir_fd=directory)
                try:
                    if os.write(fd, payload) != len(payload):
                        raise PasswordAuditBlocked('INCOMPLETE_VERIFIER_WRITE')
                    os.fsync(fd)
                finally:
                    os.close(fd)
                os.fsync(directory)
            finally:
                os.close(directory)
        except (OSError, AuditBlocked) as error:
            raise PasswordAuditBlocked('ENROLLMENT_UNAVAILABLE') from error

    def _verifier(self):
        try:
            directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                info = os.fstat(directory)
                if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
                    raise PasswordAuditBlocked('PRIVATE_DIRECTORY_REQUIRED')
                fd = os.open('verifier.json', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=directory)
                try:
                    info = os.fstat(fd)
                    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                            or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600
                            or info.st_size > VERIFIER_MAX_BYTES):
                        raise PasswordAuditBlocked('PRIVATE_VERIFIER_REQUIRED')
                    raw = os.read(fd, VERIFIER_MAX_BYTES + 1)
                    if len(raw) != info.st_size or not raw.endswith(b'\n'):
                        raise PasswordAuditBlocked('INVALID_VERIFIER')
                finally:
                    os.close(fd)
            finally:
                os.close(directory)
            doc = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique)
            if (not isinstance(doc, dict) or set(doc) != {'schema', 'iterations',
                    'authority_uid', 'agent_uid', 'salt_hex', 'digest_hex'}
                    or doc['schema'] != SCHEMA
                    or type(doc['iterations']) is not int or doc['iterations'] != ITERATIONS
                    or type(doc['authority_uid']) is not int
                    or doc['authority_uid'] != os.getuid()
                    or os.geteuid() != os.getuid()
                    or type(doc['agent_uid']) is not int or doc['agent_uid'] < 0
                    or doc['agent_uid'] == doc['authority_uid']
                    or not isinstance(doc['salt_hex'], str)
                    or re.fullmatch(r'[0-9a-f]{32}', doc['salt_hex']) is None
                    or not isinstance(doc['digest_hex'], str)
                    or re.fullmatch(r'[0-9a-f]{64}', doc['digest_hex']) is None
                    or _encode(doc) + b'\n' != raw):
                raise PasswordAuditBlocked('INVALID_VERIFIER')
            return bytes.fromhex(doc['salt_hex']), bytes.fromhex(doc['digest_hex'])
        except (OSError, ValueError, UnicodeError, RecursionError) as error:
            raise PasswordAuditBlocked('VERIFIER_UNAVAILABLE') from error

    def audit_events(self):
        try:
            return AuditLog(self.root).read_all()
        except AuditBlocked as error:
            raise PasswordAuditBlocked('AUDIT_UNAVAILABLE') from error

    def check(self, *, proposal_id, snapshot_sha256, decision_text, nonce, password):
        decision_sha256, subject_sha256 = _decision(
            proposal_id, snapshot_sha256, decision_text, nonce)
        raw = _password_bytes(password)
        salt, expected = self._verifier()
        actual = hashlib.pbkdf2_hmac('sha256', raw, salt, ITERATIONS)
        matched = hmac.compare_digest(actual, expected)
        event = {'kind': 'PASSWORD_CHECK_ACCEPTED' if matched else 'PASSWORD_CHECK_REJECTED',
                 'ref': nonce, 'subject_sha256': subject_sha256}
        try:
            AuditLog(self.root).append(event, unique_ref=True)
        except AuditBlocked as error:
            raise PasswordAuditBlocked('AUDIT_UNAVAILABLE') from error
        return {'proposal_id': proposal_id, 'snapshot_sha256': snapshot_sha256,
                'decision_sha256': decision_sha256, 'subject_sha256': subject_sha256,
                'credential_match': matched, 'authority_verification': 'NOT_ESTABLISHED',
                'execution_authorized': False}
