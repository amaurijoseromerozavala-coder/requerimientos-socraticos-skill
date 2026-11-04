"""Check a bounded RS3 *proposal*; never confirm a person or a product.

The caller supplies an interpretation of the original text. This module checks
its form and direction, not whether that interpretation matches human intent.
"""
import hashlib
import json
import re

from semantic_mini_oracle import assess


SCHEMA_VERSION = '0.1-proposed'
FIELDS = frozenset({'schema_version', 'id', 'source_ref', 'source_text',
                    'status', 'kind', 'modality', 'subject', 'condition',
                    'direction', 'assumptions', 'exceptions',
                    'human_confirmation'})
KINDS = frozenset({'NECESSARY_CONDITION', 'SUFFICIENT_CONDITION', 'EQUIVALENCE',
                   'PROHIBITION', 'PERMISSION', 'OBLIGATION', 'EXCEPTION',
                   'TEMPORAL_REQUIREMENT', 'MEASURED_LIMIT'})
MODALITIES = frozenset({'MUST', 'MUST_NOT', 'MAY', 'SHOULD', 'UNDETERMINED'})
DIRECTIONS = {
    'NECESSARY_CONDITION': 'SUBJECT_IMPLIES_CONDITION',
    'SUFFICIENT_CONDITION': 'CONDITION_IMPLIES_SUBJECT',
    'EQUIVALENCE': 'BICONDITIONAL',
}
NAME = re.compile(r'^[A-Za-z][A-Za-z0-9_]{0,63}$')
IDENTIFIER = re.compile(r'^RS3-[A-Z0-9-]{1,61}$')


class CandidateError(ValueError):
    """A proposal cannot be admitted under this bounded syntax contract."""


def _text(value, limit, code):
    if type(value) is not str or not value.strip():
        raise CandidateError(code)
    try:
        size = len(value.encode('utf-8'))
    except UnicodeError as error:
        raise CandidateError(code) from error
    if size > limit:
        raise CandidateError(code)


def check_candidate(candidate):
    if type(candidate) is not dict or set(candidate) != FIELDS:
        raise CandidateError('SCHEMA_ERROR')
    if candidate['schema_version'] != SCHEMA_VERSION:
        raise CandidateError('SCHEMA_VERSION_UNSUPPORTED')
    if type(candidate['id']) is not str or not IDENTIFIER.fullmatch(candidate['id']):
        raise CandidateError('INVALID_ID')
    _text(candidate['source_ref'], 256, 'SOURCE_REQUIRED')
    _text(candidate['source_text'], 4096, 'SOURCE_REQUIRED')
    for field in ('subject', 'condition'):
        value = candidate[field]
        if type(value) is not str or not NAME.fullmatch(value):
            raise CandidateError('INVALID_PROPOSITION_NAME')
    if candidate['status'] not in ('PROPOSED', 'NEEDS_CLARIFICATION'):
        raise CandidateError('UNTRUSTED_STATUS')
    if candidate['human_confirmation'] != 'PENDING':
        raise CandidateError('UNTRUSTED_CONFIRMATION')
    if (type(candidate['kind']) is not str or type(candidate['modality']) is not str
            or candidate['kind'] not in KINDS or candidate['modality'] not in MODALITIES):
        raise CandidateError('UNSUPPORTED_KIND_OR_MODALITY')
    direction = DIRECTIONS.get(candidate['kind'], 'NOT_COMPILABLE_YET')
    if candidate['direction'] != direction:
        raise CandidateError('DIRECTION_MISMATCH')
    for field in ('assumptions', 'exceptions'):
        values = candidate[field]
        if type(values) is not list or len(values) > 16:
            raise CandidateError('CONTEXT_LIMIT')
        for value in values:
            _text(value, 512, 'INVALID_CONTEXT')

    source_sha256 = hashlib.sha256(candidate['source_text'].encode('utf-8')).hexdigest()
    proposal_bytes = json.dumps(candidate, ensure_ascii=False, sort_keys=True,
                                separators=(',', ':')).encode('utf-8')
    proposal_sha256 = hashlib.sha256(proposal_bytes).hexdigest()
    semantic_fidelity = assess(candidate['source_text'], candidate)
    compilable = (candidate['status'] == 'PROPOSED' and
                  semantic_fidelity == 'MATCHED_MINI_GRAMMAR' and
                  candidate['modality'] == 'MUST' and not candidate['assumptions']
                  and not candidate['exceptions'] and candidate['kind'] in DIRECTIONS)
    ast = None
    if compilable:
        subject = {'var': candidate['subject']}
        condition = {'var': candidate['condition']}
        if candidate['kind'] == 'NECESSARY_CONDITION':
            ast = {'op': 'implies', 'args': [subject, condition]}
        elif candidate['kind'] == 'SUFFICIENT_CONDITION':
            ast = {'op': 'implies', 'args': [condition, subject]}
        else:
            ast = {'op': 'eq', 'args': [subject, condition]}
    return {'schema_version': SCHEMA_VERSION,
            'status': 'PROPOSED' if compilable else 'NEEDS_CLARIFICATION',
            'authority': 'NOT_GRANTED', 'source_sha256': source_sha256,
            'proposal_sha256': proposal_sha256,
            'semantic_fidelity': semantic_fidelity,
            'source_ref': candidate['source_ref'], 'ast': ast,
            'scope': 'SYNTAX_AND_DIRECTION_ONLY',
            'limitation': 'Only four bounded Spanish Boolean patterns are checked; source provenance and human meaning are not authenticated.'}
