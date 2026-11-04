"""Bound and classify untrusted model JSON without granting authority.

This is an in-process, local admission gate. The caller must supervise its own
process and preserve the original source independently; neither a model-supplied
source_ref nor a proposal digest authenticates a person or the source text.
"""

import json

from candidate_ir import CandidateError, check_candidate
from json_preflight import preflight_json
from source_snapshot import SourceSnapshot


MAX_RESPONSE_BYTES = 16 * 1024
MAX_RESPONSE_DEPTH = 8


class _DuplicateKey(ValueError):
    pass


class _NonJsonConstant(ValueError):
    pass


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey()
        result[key] = value
    return result


def _reject_constant(_value):
    raise _NonJsonConstant()


def _result(admission, reason_code, ast=None, proposal_sha256=None,
            source_binding='NOT_ASSESSED'):
    return {'admission': admission, 'reason_code': reason_code, 'ast': ast,
            'proposal_sha256': proposal_sha256,
            'source_binding': source_binding,
            'authority_verification': 'NOT_ESTABLISHED',
            'execution_authorized': False}


def admit_response(raw, *, source_snapshot=None):
    """Admit only a bounded CandidateIR proposal; never echo raw model text."""
    if source_snapshot is not None and type(source_snapshot) is not SourceSnapshot:
        return _result('INFRA_FAILURE', 'INVALID_CALLER_SNAPSHOT')
    if type(raw) is not bytes:
        return _result('REJECT_INPUT', 'BYTES_REQUIRED')
    if len(raw) > MAX_RESPONSE_BYTES:
        return _result('REJECT_INPUT', 'JSON_SIZE_LIMIT')
    try:
        preflight_json(raw, max_depth=MAX_RESPONSE_DEPTH,
                       max_bytes=MAX_RESPONSE_BYTES)
    except ValueError as error:
        code = ('JSON_DEPTH_LIMIT' if 'maximum depth' in str(error)
                else 'INVALID_JSON')
        return _result('REJECT_INPUT', code)
    except (MemoryError, OSError, RecursionError):
        return _result('INFRA_FAILURE', 'RESOURCE_FAILURE')
    try:
        decoded = raw.decode('utf-8')
    except UnicodeError:
        return _result('REJECT_INPUT', 'INVALID_UTF8')
    try:
        proposal = json.loads(decoded, object_pairs_hook=_unique_object,
                              parse_constant=_reject_constant)
    except _DuplicateKey:
        return _result('REJECT_INPUT', 'DUPLICATE_JSON_KEY')
    except _NonJsonConstant:
        return _result('REJECT_INPUT', 'NON_JSON_CONSTANT')
    except ValueError:
        return _result('REJECT_INPUT', 'INVALID_JSON')
    except (MemoryError, OSError, RecursionError):
        return _result('INFRA_FAILURE', 'RESOURCE_FAILURE')
    try:
        checked = check_candidate(proposal)
    except CandidateError as error:
        return _result('REJECT_INPUT', str(error))
    except (MemoryError, OSError, RecursionError):
        return _result('INFRA_FAILURE', 'RESOURCE_FAILURE')
    source_binding = 'NOT_ASSESSED'
    if source_snapshot is not None:
        if (proposal['source_ref'] != source_snapshot.source_ref
                or proposal['source_text'] != source_snapshot.source_text):
            return _result('REJECT_INPUT', 'SOURCE_BINDING_MISMATCH')
        source_binding = 'MATCHED_CALLER_SNAPSHOT'
    if checked['ast'] is None:
        reason = checked['semantic_fidelity']
        if reason == 'MATCHED_MINI_GRAMMAR':
            reason = 'UNCOMPILED_MODALITY_OR_CONTEXT'
        return _result('NEEDS_CLARIFICATION', reason,
                       proposal_sha256=checked['proposal_sha256'],
                       source_binding=source_binding)
    return _result('PROPOSED_FOR_REVIEW', 'BOUNDED_PROPOSAL_ONLY',
                   ast=checked['ast'], proposal_sha256=checked['proposal_sha256'],
                   source_binding=source_binding)
