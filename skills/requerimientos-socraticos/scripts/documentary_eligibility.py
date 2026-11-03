"""Evaluate RS3-D01/D02 over a bounded *declared* documentary dossier.

This is a structural model check. It neither verifies evidence bytes or human
authority nor grants deployment permission.
"""
import re
import hashlib
import json
from pathlib import Path
import sys

from json_preflight import preflight_json
from safe_io import read_regular


VERSION = 'rs3-documentary-v1'
IDENTIFIER = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')
DOSSIER_FIELDS = {'schema_version', 'snapshot_id', 'inventory_status',
                  'critical_gaps', 'requirements'}
REQUIREMENT_FIELDS = {'id', 'applicability', 'applicability_basis',
                      'assessment', 'evidence'}
EVIDENCE_FIELDS = {'status', 'snapshot_id', 'reference'}
MAX_BYTES = 256 * 1024


class InvalidDossier(ValueError):
    """The declared inventory does not meet this closed structural contract."""


def _identifier(value):
    if type(value) is not str or len(value) > 64 or not IDENTIFIER.fullmatch(value):
        raise InvalidDossier('INVALID_IDENTIFIER')
    return value


def _reference(value):
    if type(value) is not str or not value.strip() or len(value) > 256:
        raise InvalidDossier('INVALID_REFERENCE')
    return value


def _fields(value, expected):
    if type(value) is not dict or set(value) != expected:
        raise InvalidDossier('SCHEMA_ERROR')


def evaluate_dossier(dossier):
    _fields(dossier, DOSSIER_FIELDS)
    if dossier['schema_version'] != VERSION:
        raise InvalidDossier('SCHEMA_VERSION_UNSUPPORTED')
    snapshot = _identifier(dossier['snapshot_id'])
    if dossier['inventory_status'] not in ('DECLARED_COMPLETE', 'UNKNOWN'):
        raise InvalidDossier('INVALID_INVENTORY_STATUS')
    requirements, gaps = dossier['requirements'], dossier['critical_gaps']
    if (type(requirements) is not list or not 1 <= len(requirements) <= 128
            or type(gaps) is not list or len(gaps) > 128):
        raise InvalidDossier('INVENTORY_LIMIT')
    gap_ids = [_identifier(gap) for gap in gaps]
    if len(set(gap_ids)) != len(gap_ids):
        raise InvalidDossier('DUPLICATE_GAP')

    blockers = ['CRITICAL_GAP:' + gap for gap in gap_ids]
    unknowns = []
    seen = set()
    applicable_count = 0
    for item in requirements:
        _fields(item, REQUIREMENT_FIELDS)
        ident = _identifier(item['id'])
        if ident in seen:
            raise InvalidDossier('DUPLICATE_REQUIREMENT')
        seen.add(ident)
        _reference(item['applicability_basis'])
        applicability = item['applicability']
        assessment = item['assessment']
        evidence = item['evidence']
        _fields(evidence, EVIDENCE_FIELDS)
        status = evidence['status']
        if applicability not in ('APPLICABLE', 'NOT_APPLICABLE', 'UNKNOWN'):
            raise InvalidDossier('INVALID_APPLICABILITY')
        if assessment not in ('SUPPORTED', 'UNSUPPORTED', 'UNKNOWN', 'NOT_APPLICABLE'):
            raise InvalidDossier('INVALID_ASSESSMENT')
        if status not in ('CURRENT', 'STALE', 'MISSING', 'UNKNOWN', 'NOT_APPLICABLE'):
            raise InvalidDossier('INVALID_EVIDENCE_STATUS')
        if status == 'NOT_APPLICABLE':
            if evidence['snapshot_id'] is not None or evidence['reference'] is not None:
                raise InvalidDossier('INCOHERENT_EVIDENCE')
        else:
            if evidence['snapshot_id'] is not None:
                _identifier(evidence['snapshot_id'])
            if evidence['reference'] is not None:
                _reference(evidence['reference'])
        if status == 'CURRENT' and (evidence['snapshot_id'] is None
                                    or evidence['reference'] is None):
            raise InvalidDossier('INCOHERENT_CURRENT_EVIDENCE')

        if applicability == 'NOT_APPLICABLE':
            if assessment != 'NOT_APPLICABLE' or status != 'NOT_APPLICABLE':
                raise InvalidDossier('INCOHERENT_EXCLUSION')
            continue
        if applicability == 'UNKNOWN':
            unknowns.append('APPLICABILITY_UNKNOWN:' + ident)
            continue
        if assessment == 'NOT_APPLICABLE' or status == 'NOT_APPLICABLE':
            raise InvalidDossier('INCOHERENT_APPLICABLE_REQUIREMENT')
        applicable_count += 1
        if assessment == 'UNSUPPORTED':
            blockers.append('UNSUPPORTED:' + ident)
        elif assessment == 'UNKNOWN':
            unknowns.append('ASSESSMENT_UNKNOWN:' + ident)
        if status in ('STALE', 'MISSING'):
            blockers.append('EVIDENCE_' + status + ':' + ident)
        elif status == 'UNKNOWN':
            unknowns.append('EVIDENCE_UNKNOWN:' + ident)
        elif evidence['snapshot_id'] != snapshot:
            blockers.append('SNAPSHOT_MISMATCH:' + ident)

    if dossier['inventory_status'] == 'UNKNOWN':
        unknowns.append('INVENTORY_COMPLETENESS_UNKNOWN')
    if not applicable_count:
        unknowns.append('NO_APPLICABLE_REQUIREMENTS')
    model_status = ('NOT_ELIGIBLE' if blockers else
                    'INCONCLUSIVE' if unknowns else 'MODEL_ELIGIBLE')
    return {'production_ready': {
                'meaning': 'ELIGIBLE_FOR_DOCUMENTARY_REVIEW_ONLY',
                'model_status': model_status},
            'snapshot_id': snapshot, 'applicable_count': applicable_count,
            'declared_count': len(requirements), 'blockers': blockers,
            'unknowns': unknowns, 'authority_verification': 'NOT_PERFORMED',
            'deployment_authorized': False,
            'scope': 'DECLARED_INVENTORY_STRUCTURAL_CHECK_ONLY'}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidDossier('DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def main(argv=None):
    arguments = sys.argv[1:] if argv is None else argv
    try:
        if len(arguments) != 1:
            raise InvalidDossier('EXPECTED_DOSSIER_PATH')
        path = Path(arguments[0]).absolute()
        raw = read_regular(path.parent, path.name, MAX_BYTES)
        preflight_json(raw, max_depth=32, max_bytes=MAX_BYTES)
        dossier = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                             parse_constant=lambda _: (_ for _ in ()).throw(
                                 InvalidDossier('NONFINITE_NUMBER')))
        result = evaluate_dossier(dossier)
        result['input_sha256'] = hashlib.sha256(raw).hexdigest()
        print(json.dumps(result, sort_keys=True))
        return 0
    except (InvalidDossier, ValueError, OSError, UnicodeError, RecursionError) as error:
        if isinstance(error, OSError):
            detail = 'FILE_READ_ERROR'
        elif isinstance(error, UnicodeError):
            detail = 'INVALID_UTF8'
        elif isinstance(error, json.JSONDecodeError):
            detail = 'INVALID_JSON'
        elif isinstance(error, RecursionError):
            detail = 'INVALID_DEPTH'
        else:
            detail = str(error)
        print(json.dumps({'error': {'code': 'INVALID_INPUT', 'message': detail}}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
