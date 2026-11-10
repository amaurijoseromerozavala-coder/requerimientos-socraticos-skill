"""Synthetic printed-code check that burns a reserved coordinate first.

No issuer, receipt, human channel, or account boundary is implemented here.
Even a matching code is NOT_ESTABLISHED and never authorizes execution.
"""

import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import stat

from supervisor.rs3_coordinate_ledger import CoordinateLedger, LedgerBlocked


SCHEMA = 'rs3-printed-code-verifiers/v1'
MAX_BYTES = 32768


class CodeVerifierBlocked(RuntimeError):
    pass


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True).encode('ascii') + b'\n'


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise CodeVerifierBlocked('DUPLICATE_KEY')
        result[key] = value
    return result


def _hex(value, length):
    return (type(value) is str and len(value) == length
            and re.fullmatch(r'[0-9a-f]+', value) is not None)


def _check_doc(doc, ledger):
    if (type(doc) is not dict or set(doc) != {'schema', 'card_id', 'verifiers'}
            or doc['schema'] != SCHEMA or doc['card_id'] != ledger['card_id']
            or type(doc['verifiers']) is not dict
            or set(doc['verifiers']) != set(ledger['coordinates'])):
        raise CodeVerifierBlocked('INVALID_VERIFIERS')
    for item in doc['verifiers'].values():
        if (type(item) is not dict or set(item) != {'salt_hex', 'digest_hex'}
                or not _hex(item['salt_hex'], 32)
                or not _hex(item['digest_hex'], 64)):
            raise CodeVerifierBlocked('INVALID_VERIFIER_ENTRY')
    return doc


class PrintedCodeVerifier:
    def __init__(self, root):
        self.root = Path(root).absolute()

    @classmethod
    def initialize(cls, root, codes):
        """Provision fixture codes once; does not prove entropy or custody."""
        if type(codes) is not dict or not codes or any(
                not _hex(code, 32) for code in codes.values()):
            raise CodeVerifierBlocked('INVALID_CODE_INPUT')
        if len(set(codes.values())) != len(codes):
            raise CodeVerifierBlocked('DUPLICATE_CODE')
        ledger = CoordinateLedger(root)
        try:
            with ledger._locked() as directory:
                if ledger._stage_present(directory):
                    raise CodeVerifierBlocked('LEDGER_STAGE_PENDING')
                state = ledger._read(directory)
                if (set(codes) != set(state['coordinates'])
                        or any(item['state'] != 'AVAILABLE'
                               for item in state['coordinates'].values())):
                    raise CodeVerifierBlocked('COORDINATE_SET_MISMATCH')
                verifiers = {}
                for coordinate, code in codes.items():
                    salt = os.urandom(16)
                    digest = hashlib.sha256(salt + bytes.fromhex(code)).hexdigest()
                    verifiers[coordinate] = {'salt_hex': salt.hex(),
                                             'digest_hex': digest}
                doc = _check_doc({'schema': SCHEMA, 'card_id': state['card_id'],
                                  'verifiers': verifiers}, state)
                raw = _encode(doc)
                if len(raw) > MAX_BYTES:
                    raise CodeVerifierBlocked('CAPACITY_EXCEEDED')
                marker = os.open('provision.pending', os.O_WRONLY | os.O_CREAT |
                                 os.O_EXCL | os.O_NOFOLLOW, 0o600,
                                 dir_fd=directory)
                os.close(marker)
                os.fsync(directory)
                fd = os.open('verifiers.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             os.O_NOFOLLOW, 0o600, dir_fd=directory)
                try:
                    if os.write(fd, raw) != len(raw):
                        raise CodeVerifierBlocked('INCOMPLETE_WRITE')
                    os.fsync(fd)
                finally:
                    os.close(fd)
                os.fsync(directory)
                # The verifier is durable before unblocking. If this unlink is
                # lost across a crash, the marker reappears and blocks use.
                os.unlink('provision.pending', dir_fd=directory)
        except (OSError, LedgerBlocked) as error:
            raise CodeVerifierBlocked('PROVISIONING_UNAVAILABLE') from error

    def _read(self):
        ledger = CoordinateLedger(self.root)
        try:
            with ledger._locked() as directory:
                if ledger._stage_present(directory):
                    raise CodeVerifierBlocked('LEDGER_STAGE_PENDING')
                try:
                    os.stat('provision.pending', dir_fd=directory,
                            follow_symlinks=False)
                except FileNotFoundError:
                    pass
                else:
                    raise CodeVerifierBlocked('PROVISION_RECONCILIATION_REQUIRED')
                state = ledger._read(directory)
                fd = os.open('verifiers.json', os.O_RDONLY | os.O_NOFOLLOW |
                             os.O_NONBLOCK, dir_fd=directory)
                try:
                    info = os.fstat(fd)
                    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                            or info.st_nlink != 1
                            or stat.S_IMODE(info.st_mode) != 0o600
                            or info.st_size < 1 or info.st_size > MAX_BYTES):
                        raise CodeVerifierBlocked('PRIVATE_VERIFIER_REQUIRED')
                    raw = os.read(fd, MAX_BYTES + 1)
                    if len(raw) != info.st_size or not raw.endswith(b'\n'):
                        raise CodeVerifierBlocked('INCOMPLETE_VERIFIER')
                finally:
                    os.close(fd)
            doc = json.loads(raw.decode('ascii'), object_pairs_hook=_pairs)
            _check_doc(doc, state)
            if _encode(doc) != raw:
                raise CodeVerifierBlocked('NONCANONICAL_VERIFIER')
            return doc
        except (OSError, LedgerBlocked, ValueError, UnicodeError, RecursionError) as error:
            raise CodeVerifierBlocked('VERIFIER_UNAVAILABLE') from error

    def check_and_spend(self, coordinate, challenge_sha256, code):
        """Return match only after the ledger durably burns PENDING."""
        doc = self._read()
        if coordinate not in doc['verifiers']:
            raise CodeVerifierBlocked('UNKNOWN_COORDINATE')
        try:
            snapshot = CoordinateLedger(self.root).snapshot()
        except LedgerBlocked as error:
            raise CodeVerifierBlocked('LEDGER_UNAVAILABLE') from error
        entry = snapshot['coordinates'].get(coordinate)
        if (entry is None or entry['state'] != 'PENDING'
                or entry['challenge_sha256'] != challenge_sha256):
            raise CodeVerifierBlocked('PENDING_MATCH_REQUIRED')
        item = doc['verifiers'][coordinate]
        if _hex(code, 32):
            actual = hashlib.sha256(bytes.fromhex(item['salt_hex']) +
                                    bytes.fromhex(code)).digest()
            matched = hmac.compare_digest(actual, bytes.fromhex(item['digest_hex']))
        else:
            matched = False
        try:
            CoordinateLedger(self.root).spend_pending(coordinate, challenge_sha256)
        except LedgerBlocked as error:
            raise CodeVerifierBlocked('SPEND_UNCONFIRMED') from error
        return {'state': 'SPENT', 'code_match': matched,
                'coordinate': coordinate, 'challenge_sha256': challenge_sha256,
                'authority_verification': 'NOT_ESTABLISHED',
                'execution_authorized': False}
