"""Rebuild the conservative RS3 inventory from the identified proposal ZIP.

This is an evidence index, not a semantic acceptance or coverage calculator.
It never extracts archive members or executes their content.
"""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


ZIP_SHA256 = '83a83c77921f7737e89328b8dae365e7d0e7047f0c3fc7acbf7af2fd8f6c2d7e'
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = 'skills/requerimientos-socraticos/scripts/'
TEST = 'skills/requerimientos-socraticos/tests/'
SUPERVISOR = 'supervisor/'
SUP_TEST = 'supervisor/tests/'

# Each link is a witnessed *partial* implementation, never full acceptance.
LINKS = {
    '003': (SCRIPT+'documentary_eligibility.py', TEST+'test_rs3_documentary_eligibility.py'),
    '008': (SCRIPT+'documentary_eligibility.py', TEST+'test_rs3_documentary_eligibility.py'),
    '024': (SUPERVISOR+'rs3_password_cli.py', SUP_TEST+'test_rs3_password_cli.py'),
    '025': (SUPERVISOR+'rs3_password_auditor.py', SUP_TEST+'test_rs3_password_auditor.py'),
    '026': (SUPERVISOR+'rs3_audit_log.py', SUP_TEST+'test_rs3_password_auditor.py'),
    '029': (SUPERVISOR+'rs3_password_cli.py', SUP_TEST+'test_rs3_password_cli.py'),
    '031': (SUPERVISOR+'rs3_password_auditor.py', SUP_TEST+'test_rs3_password_auditor.py'),
    '033': (SUPERVISOR+'rs3_audit_log.py', SUP_TEST+'test_rs3_audit_log.py'),
    '034': (SUPERVISOR+'rs3_password_auditor.py', SUP_TEST+'test_rs3_authority_uid_guard.py'),
    '036': (SCRIPT+'candidate_ir.py', TEST+'test_candidate_ir.py'),
    '038': (SCRIPT+'candidate_ir.py', TEST+'test_candidate_ir.py'),
    '039': (SCRIPT+'candidate_ir.py', TEST+'test_candidate_ir.py'),
    '040': (SCRIPT+'candidate_ir.py', TEST+'test_candidate_ir.py'),
    '041': (SCRIPT+'ears_draft.py', TEST+'test_ears_draft.py'),
    '042': (SCRIPT+'candidate_ir.py', TEST+'test_candidate_ir.py'),
    '043': (SCRIPT+'candidate_ir.py', TEST+'test_candidate_ir.py'),
    '045': (SCRIPT+'semantic_mini_oracle.py', TEST+'test_rs3_semantic_oracles.py'),
    '047': (SCRIPT+'candidate_ir.py', TEST+'test_candidate_ir.py'),
    '048': (SCRIPT+'candidate_ir.py', TEST+'test_candidate_ir.py'),
    '049': (SCRIPT+'formal_queries.py', TEST+'test_formal_queries.py'),
    '050': (SCRIPT+'logic_engine.py', TEST+'test_logic.py'),
    '051': (SCRIPT+'formal_queries.py', TEST+'test_rs3_query_oracles.py'),
    '053': (SCRIPT+'formal_queries.py', TEST+'test_rs3_query_oracles.py'),
    '055': (SCRIPT+'formal_queries.py', TEST+'test_rs3_formal_equivalence.py'),
    '056': (SCRIPT+'analyze_logic.py', TEST+'test_logic.py'),
    '057': (SCRIPT+'witness_validation.py', TEST+'test_witness_recheck.py'),
    '058': (SCRIPT+'logic_engine.py', TEST+'test_logic.py'),
    '059': (SCRIPT+'memory_budget.py', TEST+'test_logic_memory.py'),
    '061': (SCRIPT+'formal_queries.py', TEST+'test_formal_queries.py'),
    '062': (SCRIPT+'witness_validation.py', TEST+'test_witness_recheck.py'),
    '082': ('ci/check_rdd_record.py', 'ci/tests/test_rdd_record.py'),
    '083': ('ci/run_quality.sh', 'ci/tests/test_workflow.py'),
    '086': ('ci/check_rdd_record.py', 'ci/tests/test_rdd_record.py'),
    '091': (SCRIPT+'documentary_eligibility.py', TEST+'test_rs3_documentary_eligibility.py'),
    '092': (SCRIPT+'activation_preflight.py', TEST+'test_activation_preflight.py'),
    '093': (SUPERVISOR+'process_core.py', SUP_TEST+'test_process_core.py'),
    '095': (SCRIPT+'requirements', TEST+'test_rs3_documentary_cli.py'),
    '098': (SUPERVISOR+'safe_capture.py', SUP_TEST+'test_safe_capture.py'),
    '100': (SUPERVISOR+'qa_adapter.py', SUP_TEST+'test_qa_adapter.py'),
    '101': (SCRIPT+'candidate_ir.py', TEST+'test_candidate_ir.py'),
    '102': ('ci/check_rdd_record.py', 'ci/tests/test_rdd_record.py'),
    '103': (SCRIPT+'requirements', TEST+'test_rs3_documentary_cli.py'),
    '106': (SCRIPT+'candidate_ir.py', TEST+'test_candidate_ir.py'),
}

TASK_LINKS = {
    'T002': 'skills/requerimientos-socraticos/SKILL.md',
    'T003': 'docs/design/rs3/ADR-001-local-authority.md',
    'T005': 'docs/design/rs3/authority-boundary-decision.json',
    'T006': TEST+'test_rs3_query_oracles.py',
    'T007': TEST+'test_rs3_query_oracles.py',
    'T008': TEST+'test_rs3_documentary_eligibility.py',
    'T009': TEST+'test_rs3_formal_equivalence.py',
    'T011': SCRIPT+'witness_validation.py',
    'T013': SCRIPT+'candidate_ir.py',
    'T014': TEST+'test_rs3_variable_roles.py',
    'T015': TEST+'test_candidate_ir.py',
    'T016': SCRIPT+'candidate_ir.py',
    'T017': SCRIPT+'ears_draft.py',
    'T019': SCRIPT+'formal_queries.py',
    'T020': TEST+'test_rs3_query_oracles.py',
    'T021': TEST+'test_rs3_formal_equivalence.py',
    'T022': SCRIPT+'witness_validation.py',
    'T023': SCRIPT+'process_supervision.py',
    'T029': 'docs/design/rs3/ADR-001-local-authority.md',
    'T031': SUPERVISOR+'rs3_audit_log.py',
    'T032': SUPERVISOR+'rs3_password_auditor.py',
    'T033': SUPERVISOR+'rs3_password_cli.py',
}

GROUP_TESTS = {
    'FORMAL': TEST+'test_rs3_query_oracles.py',
    'IR': TEST+'test_candidate_ir.py',
    'AUTH': SUP_TEST+'test_rs3_password_auditor.py',
    'ASSURANCE': 'ci/tests/test_rdd_record.py',
    'OPS': SUP_TEST+'test_process_core.py',
    'INTEGRATION': 'ci/tests/test_workflow.py',
}

PROPOSAL_BINDING_EVENT = {
    'id': 'WU-RS3-PROPOSAL-BINDING-003',
    'commit': 'ec164df5b4c12e8a1b438a389fb5f35e19dc8627',
    'candidate': 'sha256:20b8256e7d37ef50b23247fbd0c3b70dfef731b0b1d3b8940e9439cc332c97b8',
    'lineage': 'review-8d9def7efca963bc',
    'rdd_receipt': 'docs/skill-audit/rs3-proposal-binding/RDD-CIERRE.md',
    'rdd_scope': 'PATCH_INSPECTION_NO_TEST_EXECUTION',
    'acceptance_scope': 'PARTIAL_IMPLEMENTATION_ONLY',
}
PROPOSAL_BINDING_REQUIREMENTS = frozenset({'RS3-REQ-036', 'RS3-REQ-041',
                                            'RS3-REQ-047'})
SEMANTIC_ORACLE_EVENT = {
    'id': 'WU-RS3-SEMANTIC-ORACLES-005',
    'commit': 'a636a4d2c598c22b6d50579763c09b60504fce27',
    'candidate': 'sha256:52698748fd21281bf42502cb72b9494534bb2634024e22b367e7ec5bc9865692',
    'lineage': 'review-e4f2d24d98f89b33',
    'rdd_receipt': 'docs/skill-audit/rs3-semantic-oracles/RDD-CIERRE.md',
    'rdd_scope': 'PATCH_INSPECTION_NO_TEST_EXECUTION',
    'acceptance_scope': 'PARTIAL_IMPLEMENTATION_ONLY',
}
WEAK_MODEL_EVENT = {
    'id': 'WU-RS3-WEAK-MODEL-ADMISSION-006',
    'commit': '40328757dcf7f6b758f8f09df845224f1b656572',
    'candidate': 'sha256:6d0891fdea5ac5ebae50dcee6d65ecea801f221ab0960b2085ec96fba0ac1c45',
    'lineage': 'review-5454144c698d99c4',
    'rdd_receipt': 'docs/skill-audit/rs3-weak-model-admission/RDD-CIERRE.md',
    'rdd_scope': 'PATCH_INSPECTION_NO_TEST_EXECUTION',
    'acceptance_scope': 'PARTIAL_IMPLEMENTATION_ONLY',
}
EVIDENCE_EVENTS = (PROPOSAL_BINDING_EVENT, SEMANTIC_ORACLE_EVENT,
                   WEAK_MODEL_EVENT)
EVIDENCE_TARGETS = {
    PROPOSAL_BINDING_EVENT['id']: PROPOSAL_BINDING_REQUIREMENTS,
    SEMANTIC_ORACLE_EVENT['id']: frozenset({'RS3-REQ-038', 'RS3-REQ-040',
                                           'RS3-REQ-043', 'RS3-REQ-045'}),
    WEAK_MODEL_EVENT['id']: frozenset({'RS3-REQ-036', 'RS3-REQ-038',
                                      'RS3-REQ-039', 'RS3-REQ-040',
                                      'RS3-REQ-043'}),
}


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _member(archive, suffix):
    names = [name for name in archive.namelist() if name.endswith('/'+suffix)]
    if len(names) != 1:
        raise ValueError('PACKAGE_MEMBER_MISSING_OR_AMBIGUOUS')
    return json.loads(archive.read(names[0]))


def build(package, head):
    for event in EVIDENCE_EVENTS:
        if not (ROOT / event['rdd_receipt']).is_file():
            raise ValueError('EVIDENCE_RECEIPT_MISSING')
    raw = Path(package).read_bytes()
    if _sha(raw) != ZIP_SHA256:
        raise ValueError('PACKAGE_IDENTITY_MISMATCH')
    with zipfile.ZipFile(package) as archive:
        manifest = _member(archive, 'MANIFEST.json')
        prefix = next(name.removesuffix('MANIFEST.json') for name in archive.namelist()
                      if name.endswith('/MANIFEST.json'))
        for item in manifest['files']:
            data = archive.read(prefix+item['path'])
            if len(data) != item['size_bytes'] or _sha(data) != item['sha256']:
                raise ValueError('PACKAGE_MANIFEST_MISMATCH')
        source_req = _member(archive, 'specs/requirements.json')['requirements']
        source_tasks = _member(archive, 'specs/tasks.json')['tasks']
        source_cases = _member(archive, 'specs/adversarial_cases.json')['cases']
        source_trace = _member(archive, 'specs/traceability.json')['rows']
    if (len(source_req), len(source_tasks), len(source_cases), len(source_trace)) != (107, 50, 52, 107):
        raise ValueError('PACKAGE_DENOMINATOR_MISMATCH')
    if manifest['status'] != 'DRAFT_PROPOSED_NOT_RATIFIED':
        raise ValueError('PACKAGE_STATUS_MISMATCH')
    trace = {item['requirement_id']: item for item in source_trace}
    requirements = []
    for index, item in enumerate(source_req, 1):
        req_id = f'RS3-REQ-{index:03d}'
        if (item['id'] != req_id or item['status'] != 'PROPOSED'
                or trace[req_id]['mapped_by'] != 'GROUP_ONLY_PROPOSED_NOT_FINE_GRAINED'):
            raise ValueError('PACKAGE_REQUIREMENT_MISMATCH')
        links = LINKS.get(f'{index:03d}')
        if links and any(not (ROOT/path).is_file() for path in links):
            raise ValueError('OBSERVED_PATH_MISSING')
        evidence_refs = [event['id'] for event in EVIDENCE_EVENTS
                         if req_id in EVIDENCE_TARGETS[event['id']]]
        requirements.append({
            'id': req_id, 'group': item['group'], 'priority': item['priority'],
            'statement_sha256': _sha(item['statement'].encode('utf-8')),
            'package_status': 'PROPOSED', 'adoption_status': 'NOT_RATIFIED_AS_SET',
            'implementation_status': 'CODE_OBSERVED_PARTIAL' if links else 'NOT_ASSESSED',
            'code_paths': [links[0]] if links else [],
            'test_paths': [links[1]] if links else [],
            **({'evidence_refs': evidence_refs} if evidence_refs else {}),
            'acceptance_status': 'NOT_VERIFIED_PER_REQUIREMENT',
            'package_mapping': 'GROUP_ONLY_PROPOSED_NOT_FINE_GRAINED',
        })
    tasks = []
    for index, item in enumerate(source_tasks, 1):
        task_id = f'T{index:03d}'
        if item['id'] != task_id or item['status'] != 'PROPOSED':
            raise ValueError('PACKAGE_TASK_MISMATCH')
        link = TASK_LINKS.get(task_id)
        if link and not (ROOT/link).is_file():
            raise ValueError('OBSERVED_PATH_MISSING')
        state = ('READ_ONLY_COMPLETED' if task_id == 'T001' else
                 'OBSERVED_PARTIAL' if link else 'PENDING')
        tasks.append({'id': task_id, 'phase': item['phase'],
                      'title_sha256': _sha(item['title'].encode('utf-8')),
                      'depends_on': item['depends_on'], 'state': state,
                      'evidence_paths': [link] if link else [],
                      'package_status': 'PROPOSED'})
    cases = []
    for index, item in enumerate(source_cases, 1):
        case_id = f'RS3-AT-{index:03d}'
        if item['id'] != case_id or item['status'] != 'SPECIFIED_NOT_RUN':
            raise ValueError('PACKAGE_CASE_MISMATCH')
        related = GROUP_TESTS.get(item['requirement_group'])
        cases.append({'id': case_id, 'group': item['requirement_group'],
                      'stimulus_sha256': _sha(item['stimulus'].encode('utf-8')),
                      'execution': 'NOT_RUN_AS_PACKAGE_CASE',
                      'related_test_paths': [related] if related else [],
                      'related_test_scope': 'GROUP_ONLY_NOT_EQUIVALENCE'})
    return {
        'schema': 'rs3-reconciliation/v1',
        'source': {'zip_sha256': ZIP_SHA256, 'manifest_files_verified': len(manifest['files']),
                   'package_status': manifest['status'], 'baseline_git_sha': manifest['github_snapshot']},
        'observed_head': head,
        'decisions': {'production_ready': 'DOCUMENTARY_REVIEW_ELIGIBILITY',
                      'd02': 'ALL_APPLICABLE_CURRENT_EVIDENCE_NO_CRITICAL_GAPS',
                      'd04': 'LOCAL_PBKDF2_VERIFIER_BOUNDARY_UNVERIFIED',
                      'd05': 'SEPARATE_LOCAL_ACCOUNT_DESIGN_ONLY',
                      'd05_gate': 'SECURITY_BOUNDARY_UNMET', 'd03': 'PENDING'},
        'formal': {'no_output': 'SAT(D ∧ ¬∃O:C)',
                   'scope': 'BOUNDED_BOOLEAN_MODEL_NOT_PRODUCT_EXECUTION'},
        'plan_status': 'TOPOLOGY_ONLY',
        'duration_status': 'NOT_ESTIMATED',
        'acceptance_scope': 'INVENTORY_ONLY_NO_REQUIREMENT_PROMOTION',
        'evidence_events': list(EVIDENCE_EVENTS),
        'requirements': requirements, 'tasks': tasks, 'cases': cases,
    }


def render(result):
    """Render the inventory deterministically for byte-for-byte source checks."""
    # One item per line keeps the 209-row inventory small and reviewable.
    header = {key: value for key, value in result.items()
              if key not in ('requirements', 'tasks', 'cases')}
    lines = ['{']
    for key, value in header.items():
        lines.append('  '+json.dumps(key)+': '+json.dumps(value, ensure_ascii=False,
                                                     sort_keys=True)+',')
    for index, key in enumerate(('requirements', 'tasks', 'cases')):
        lines.append('  '+json.dumps(key)+': [')
        rows = result[key]
        for row_index, row in enumerate(rows):
            suffix = ',' if row_index+1 < len(rows) else ''
            lines.append('    '+json.dumps(row, ensure_ascii=False, sort_keys=True,
                                            separators=(',', ':'))+suffix)
        lines.append('  ]'+(',' if index < 2 else ''))
    lines.append('}')
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', required=True)
    parser.add_argument('--head', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if len(args.head) != 40 or any(char not in '0123456789abcdef' for char in args.head):
        raise ValueError('INVALID_HEAD')
    result = build(args.package, args.head)
    Path(args.output).write_text(render(result), encoding='utf-8')


if __name__ == '__main__':
    main()
