"""Bounded, non-authoritative identity builder for printed-code proposals.

This module does not issue cards, verify codes, consume nonces, sign receipts,
or establish human authority. All caller inputs remain untrusted proposals.
"""

import hashlib
import json
import re
import unicodedata


MAX_QUESTION_BYTES = 8192
MAX_OPTION_BYTES = 4096
MAX_MANIFEST_BYTES = 16384
MAX_OPTIONS = 32
CONFIRMATION_KINDS = frozenset({
    'SEMANTIC_ACCEPTANCE', 'EXCEPTION_ACCEPTANCE', 'OPERATION_AUTHORIZATION'})
METADATA_FIELDS = frozenset({
    'proposal_sha256', 'snapshot_sha256', 'confirmation_kind', 'nonce',
    'audience', 'policy_sha256', 'card_id', 'coordinate', 'expiry'})


class ChallengeBlocked(ValueError):
    """A proposal cannot be identified under the strict v1 contract."""


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True).encode('ascii')


def _digest(domain, value):
    return hashlib.sha256(domain.encode('ascii') + b'\n' + _canonical(value)).hexdigest()


def _identifier(value, pattern):
    return type(value) is str and re.fullmatch(pattern, value) is not None


def _text(value, limit):
    if type(value) is not str or not value:
        raise ChallengeBlocked('INVALID_TEXT')
    try:
        raw = value.encode('utf-8')
    except UnicodeError as error:
        raise ChallengeBlocked('INVALID_TEXT') from error
    if len(raw) > limit or any(unicodedata.category(char).startswith('C')
                               for char in value):
        raise ChallengeBlocked('INVALID_TEXT')


def build_presentation(question, options, *, ui_version):
    """Build an exact, order-sensitive presentation manifest from typed options."""
    _text(question, MAX_QUESTION_BYTES)
    if ui_version != 'rs3-ui/v1' or type(options) is not list or not 1 <= len(options) <= MAX_OPTIONS:
        raise ChallengeBlocked('INVALID_PRESENTATION')
    seen = set()
    clean = []
    for option in options:
        if (type(option) is not dict or set(option) != {'id', 'type', 'text'}
                or not _identifier(option['id'], r'[A-Za-z0-9_.-]{1,64}')
                or option['id'] in seen or option['type'] != 'OPTION'):
            raise ChallengeBlocked('INVALID_OPTION')
        _text(option['text'], MAX_OPTION_BYTES)
        seen.add(option['id'])
        clean.append({'id': option['id'], 'type': 'OPTION', 'text': option['text']})
    manifest = {'schema': 'rs3-presentation/v1', 'question': question,
                'options': clean, 'ui_version': ui_version}
    if len(_canonical(manifest)) > MAX_MANIFEST_BYTES:
        raise ChallengeBlocked('PRESENTATION_SIZE_LIMIT')
    return {**manifest, 'presentation_manifest_sha256':
            _digest('rs3-presentation/v1', manifest)}


def build_candidate_challenge(presentation, selected_option_id, **metadata):
    """Derive a proposed challenge identity; never verify or authorize it."""
    if (type(presentation) is not dict or set(presentation) !=
            {'schema', 'question', 'options', 'ui_version',
             'presentation_manifest_sha256'}
            or presentation['schema'] != 'rs3-presentation/v1'):
        raise ChallengeBlocked('INVALID_PRESENTATION')
    rebuilt = build_presentation(presentation['question'], presentation['options'],
                                 ui_version=presentation['ui_version'])
    if presentation != rebuilt:
        raise ChallengeBlocked('PRESENTATION_DIGEST_MISMATCH')
    if type(selected_option_id) is not str:
        raise ChallengeBlocked('OPTION_NOT_FOUND')
    option = next((item for item in rebuilt['options']
                   if item['id'] == selected_option_id), None)
    if option is None:
        raise ChallengeBlocked('OPTION_NOT_FOUND')
    if set(metadata) != METADATA_FIELDS:
        raise ChallengeBlocked('INVALID_METADATA_FIELDS')
    for field in ('proposal_sha256', 'snapshot_sha256', 'policy_sha256'):
        if not _identifier(metadata[field], r'[0-9a-f]{64}'):
            raise ChallengeBlocked('INVALID_DIGEST')
    if (type(metadata['confirmation_kind']) is not str
            or metadata['confirmation_kind'] not in CONFIRMATION_KINDS
            or not _identifier(metadata['nonce'], r'[0-9a-f]{32}')
            or not _identifier(metadata['audience'], r'[A-Za-z0-9_.-]{1,64}')
            or not _identifier(metadata['card_id'], r'[A-Za-z0-9_.-]{1,64}')
            or not _identifier(metadata['coordinate'], r'[A-Za-z0-9_.-]{1,32}')
            or type(metadata['expiry']) is not int
            or not 1 <= metadata['expiry'] < 2**63):
        raise ChallengeBlocked('INVALID_METADATA')
    option_hash = _digest('rs3-option/v1', option)
    decision_hash = _digest('rs3-decision/v1', {
        'confirmation_kind': metadata['confirmation_kind'],
        'selected_option_id': option['id'],
        'selected_option_sha256': option_hash})
    binding = {'protocol_version': 'rs3-printed-codes/v1',
               'confirmation_kind': metadata['confirmation_kind'],
               'proposal_sha256': metadata['proposal_sha256'],
               'snapshot_sha256': metadata['snapshot_sha256'],
               'canonical_decision_sha256': decision_hash,
               'presentation_manifest_sha256': rebuilt['presentation_manifest_sha256'],
               'selected_option_id': option['id'],
               'selected_option_sha256': option_hash,
               'nonce': metadata['nonce'], 'audience': metadata['audience'],
               'policy_sha256': metadata['policy_sha256'],
               'card_id': metadata['card_id'], 'coordinate': metadata['coordinate'],
               'expiry': metadata['expiry']}
    return {'schema': 'rs3-candidate-challenge/v1',
            'status': 'PROPOSED_UNAUTHENTICATED', **binding,
            'challenge_sha256': _digest('rs3-challenge/v1', binding),
            'authority_verification': 'NOT_ESTABLISHED',
            'execution_authorized': False}
