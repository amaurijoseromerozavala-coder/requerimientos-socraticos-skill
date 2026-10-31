"""Bounded consistency checking of QA records, not execution or authentication."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

SKILL = Path(__file__).resolve().parents[1]
SHARED = SKILL.parent / 'requerimientos-socraticos' / 'scripts'
if not SHARED.is_dir():
    raise SystemExit('REQUIREMENTS_SKILL_UNAVAILABLE')
sys.path.insert(0, str(SHARED))
from json_preflight import preflight_json
from safe_io import read_regular
from jsonschema import Draft202012Validator

MAX_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024

class InvalidReport(ValueError):
    pass

def need(condition, code):
    if not condition:
        raise InvalidReport(code)

def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, 'DUPLICATE_JSON_KEY')
        result[key] = value
    return result

def decode(raw):
    preflight_json(raw, max_depth=32, max_bytes=MAX_BYTES)
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(InvalidReport('NONFINITE_JSON')))

def index_unique(records, key='id'):
    out = {}
    for row in records:
        need(row[key] not in out, 'DUPLICATE_ID')
        out[row[key]] = row
    return out

def inputs_digest(doc):
    """Bind a judgment to canonical JSON input records, not to external truth."""
    fields = ('schema_version', 'assessment_id', 'mode', 'context', 'delegation',
              'inventory', 'evidence', 'limitations')
    raw = json.dumps({k: doc[k] for k in fields}, sort_keys=True,
                     separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def validate_report(doc, evidence_root):
    schema = decode((SKILL / 'assets/report.schema.json').read_bytes())
    need(not list(Draft202012Validator(schema).iter_errors(doc)), 'SCHEMA_INVALID')
    obligations = index_unique(doc['inventory'])
    cases = index_unique([c for o in obligations.values() for c in o['cases']])
    need(len(cases) <= 128, 'TOTAL_CASE_LIMIT')
    evidence = index_unique(doc['evidence'])
    need(not (set(obligations) & set(cases) or set(obligations) & set(evidence)
              or set(cases) & set(evidence)), 'CROSS_COLLECTION_ID_COLLISION')
    used_evidence = []
    total = 0
    cache = {}

    def verify_ref(ref):
        nonlocal total
        key = (ref['path'], ref['sha256'])
        if key not in cache:
            raw = read_regular(evidence_root, ref['path'], limit=MAX_BYTES)
            total += len(raw)
            need(total <= MAX_TOTAL_BYTES, 'EVIDENCE_BYTES_LIMIT')
            need(hashlib.sha256(raw).hexdigest() == ref['sha256'], 'ARTIFACT_HASH_MISMATCH')
            cache[key] = True

    verify_ref(doc['delegation']['source'])
    for o in obligations.values():
        for source in o['source_refs']:
            verify_ref(source)
        for c in o['cases']:
            verify_ref(c['oracle'])
            eid = c['evidence_id']
            if c['status'] in ('PASS', 'FAIL'):
                need(eid in evidence, 'MISSING_EVIDENCE')
            if eid is not None:
                need(eid in evidence, 'DANGLING_EVIDENCE')
                e = evidence[eid]
                need(e['case_id'] == c['id'], 'CASE_EVIDENCE_MISMATCH')
                need(e['kind'] == c['kind'], 'EVIDENCE_KIND_MISMATCH')
                need(c['status'] not in ('NOT_RUN', 'UNKNOWN'), 'RESULT_WITHOUT_OBSERVATION')
                need(c['status'] == 'STALE' or e['outcome'] == c['status'], 'CONTRADICTORY_RESULT')
                used_evidence.append(eid)
                verify_ref(e['artifact'])
    need(len(used_evidence) == len(set(used_evidence)), 'REUSED_EVIDENCE_ID')
    need(set(used_evidence) == set(evidence), 'ORPHAN_EVIDENCE')

    required = []
    gaps = []
    failures = []
    successes = []
    for o in obligations.values():
        # Only explicit, non-material and non-applicable records may be excluded.
        if o['applicability'] == 'NOT_APPLICABLE' and o['materiality'] == 'OPTIONAL':
            need(not o['cases'], 'EXCLUDED_OBLIGATION_HAS_CASES')
            continue
        if o['materiality'] == 'OPTIONAL' and o['applicability'] == 'APPLICABLE':
            # Optional records still have their references checked above.
            continue
        required.append(o['id'])
        unresolved = o['applicability'] != 'APPLICABLE' or o['materiality'] != 'REQUIRED'
        states = []
        for c in o['cases']:
            e = evidence.get(c['evidence_id'])
            current = (e is not None and e['context'] == doc['context']
                       and e['observed_sequence'] > c['oracle_sequence'])
            states.append(c['status'] if current else 'UNKNOWN')
            if current and c['status'] == 'FAIL' and not unresolved:
                failures.append(c['id'])
        if unresolved or not states or any(s != 'PASS' for s in states):
            # A FAIL is distinct from an unverified obligation; keep other gaps.
            if unresolved or not states or any(s not in ('PASS', 'FAIL') for s in states):
                gaps.append(o['id'])
        if not unresolved and states and all(s == 'PASS' for s in states):
            successes.append(o['id'])

    j = doc['judgment']
    delegation_current = (doc['delegation']['status'] == 'CONFIRMED'
                          and not doc['delegation']['exceptions_pending']
                          and j['context'] == doc['context']
                          and j['assessment_id'] == doc['assessment_id']
                          and j['inputs_sha256'] == inputs_digest(doc)
                          and j['criteria_sequence'] < j['judgment_sequence'])
    scope_supported = j['scope'] == j['materiality'] == j['sufficiency'] == 'SUPPORTED'
    all_success = bool(required) and set(required) == set(successes)
    gap_reasons = []
    if gaps: gap_reasons.append('REQUIRED_OBLIGATIONS_PENDING')
    if not required: gap_reasons.append('NO_REQUIRED_OBLIGATIONS')
    if not delegation_current: gap_reasons.append('JUDGMENT_OR_DELEGATION_NOT_CURRENT')
    if not scope_supported: gap_reasons.append('SCOPE_MATERIALITY_OR_SUFFICIENCY_PENDING')
    has_gap = bool(gap_reasons)
    if failures:
        event, verdict = 'RECORD_CURRENT_FAILURE', 'FAIL_WITHIN_DECLARED_EVIDENCE'
    elif has_gap or not all_success or not delegation_current or not scope_supported:
        event, verdict = 'RECORD_GAP_OR_STALE', 'INCONCLUSIVE'
    else:
        event, verdict = 'RECORD_CURRENT_SUCCESS', 'SUPPORTED_WITHIN_DECLARED_EVIDENCE'
    return {'execution_status': 'COMPLETED', 'document_validation': 'VALID', 'proposed_event': event,
            'verdict': verdict, 'required_obligations': required, 'gaps': gaps,
            'failure_cases': failures, 'material_gap': has_gap,
            'gap_reasons': gap_reasons,
            'delegation_current': delegation_current, 'scope_supported': scope_supported,
            'all_success': all_success, 'verified_artifact_bytes': total,
            'authority_verification': 'NOT_PERFORMED',
            'execution_authorized': False,
            'execution_performed': False,
            'limits': ['Checks record consistency and current artifact bytes only.',
                       'Does not authenticate human authority or prove semantic truth.',
                       'Does not establish whole-system completeness or hardware behavior.',
                       'Mutable local files are lint, not a sealed Git candidate.']}

def observe_failure_declarations(doc):
    """Inspect only a bounded prefix of decoded evidence records; no file reads.

    Counts are declarations in the scanned prefix, not authenticated failures.
    A partial scan with zero matches cannot establish absence of declarations.
    """
    observation = {'status': 'NOT_ASSESSED', 'scan_status': 'NOT_ASSESSED',
                   'declared_failure_count': None, 'scanned_records': 0,
                   'evidence_verification': 'NOT_ESTABLISHED'}
    if not isinstance(doc, dict) or not isinstance(doc.get('evidence'), list):
        return observation
    records = doc['evidence']
    count = 0
    complete = len(records) <= 128
    scanned = 0
    for record in records[:128]:
        scanned += 1
        if not isinstance(record, dict) or not isinstance(record.get('outcome'), str):
            complete = False
            continue
        outcome = record['outcome']
        if outcome == 'FAIL':
            count += 1
        elif outcome != 'PASS':
            complete = False
    observation.update(
        status=('UNVERIFIED_DECLARATIONS_FOUND' if count else
                'NO_DECLARATIONS_FOUND' if complete else 'NOT_ASSESSED'),
        scan_status='COMPLETE' if complete else 'PARTIAL',
        declared_failure_count=count, scanned_records=scanned)
    return observation

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', required=True)
    p.add_argument('--evidence-root', required=True)
    args = p.parse_args(argv)
    observation = observe_failure_declarations(None)
    try:
        path = Path(args.report)
        doc = decode(read_regular(path.parent, path.name, limit=MAX_BYTES))
        observation = observe_failure_declarations(doc)
        result = validate_report(doc, args.evidence_root)
        result['failure_observation'] = observation
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, RecursionError, MemoryError) as error:
        # No semantic transition can be inferred from an unavailable evaluation.
        # Best effort only: abrupt termination/output failure requires an observer.
        print(json.dumps({'execution_status': 'INFRA_FAILURE',
                          'document_validation': 'NOT_ASSESSED',
                          'proposed_event': None, 'verdict': None,
                          'diagnostic': {'exception_type': type(error).__name__,
                                         'errno': getattr(error, 'errno', None),
                                         'cause': 'NOT_DETERMINED'},
                          'failure_observation': observation,
                          'authority_verification': 'NOT_PERFORMED',
                          'execution_authorized': False,
                          'execution_performed': False}, ensure_ascii=False))
        return 3
    except ValueError as error:
        print(json.dumps({'execution_status': 'COMPLETED',
                          'document_validation': 'INVALID', 'proposed_event': 'REJECT_INPUT',
                          'error': type(error).__name__ + ': ' + str(error),
                          'failure_observation': observation,
                          'authority_verification': 'NOT_PERFORMED',
                          'execution_authorized': False,
                          'execution_performed': False}, ensure_ascii=False))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
