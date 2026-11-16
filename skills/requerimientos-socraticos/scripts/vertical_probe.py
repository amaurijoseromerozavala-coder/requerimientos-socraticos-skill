"""Bounded synthetic RS3 vertical probe, never an authority or general parser.

The caller supplies domain, rules and glossary independently of model output.
Only a checked CandidateIR AST becomes a formal *property*. It is never
silently turned into a guard, domain restriction or permission.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory

from analyze_to_view import question_handoff
from ears_draft import render_draft
from gap_glossary import glossary_state
from gap_scenario import _evaluate
from logic_engine import validate
from process_supervision import run_supervised
from source_snapshot import SourceSnapshot
from weak_model_gate import admit_response


ANALYZER = Path(__file__).with_name('analyze_logic.py')
CLEANUP_CONFIRMED = 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED'
HEX64 = re.compile(r'^[0-9a-f]{64}$')


def _closed(status, reason):
    return {'status': status, 'reason_code': reason,
            'authority_verification': 'NOT_ESTABLISHED',
            'execution_authorized': False}


def _admit(raw, source):
    admitted = admit_response(raw, source_snapshot=source)
    if admitted['admission'] != 'PROPOSED_FOR_REVIEW':
        return admitted, None, None
    if admitted['source_binding'] != 'MATCHED_CALLER_SNAPSHOT':
        return admitted, None, None
    try:
        candidate = json.loads(raw.decode('utf-8'))
        ears = render_draft(candidate)
    except (UnicodeError, ValueError, TypeError, KeyError, MemoryError):
        return admitted, None, None
    if (ears['status'] != 'PROPOSED' or ears['ast'] != admitted['ast']
            or ears['proposal_sha256'] != admitted['proposal_sha256']):
        return admitted, None, None
    return admitted, candidate, ears


def verify_property_witness(model, ast, witness):
    """Reevaluate one formal property counterexample with plain Boolean logic."""
    try:
        names = model['inputs'] + model['outputs']
        if (type(witness) is not dict or set(witness) != set(names)
                or any(type(value) is not bool for value in witness.values())
                or not _evaluate(model['domain'], witness)
                or _evaluate(ast, witness)):
            return False
        return all(not _evaluate(rule['guard'], witness)
                   or _evaluate(rule['response'], witness)
                   for rule in model['rules'])
    except (KeyError, TypeError, ValueError):
        return False


def run_first(first_raw, source, model_base, glossary_entries):
    """Return a question only after independent proposal and witness checks."""
    if type(source) is not SourceSnapshot:
        return _closed('BLOCKED', 'CALLER_SOURCE_REQUIRED')
    admitted, candidate, ears = _admit(first_raw, source)
    if candidate is None:
        status = admitted['admission'] if admitted['admission'] == 'REJECT_INPUT' else 'BLOCKED'
        return _closed(status, admitted['reason_code'])
    if (type(model_base) is not dict
            or set(model_base) != {'inputs', 'outputs', 'domain', 'rules', 'properties'}
            or model_base['properties'] != []
            or type(model_base['inputs']) is not list
            or not {candidate['subject'], candidate['condition']} <= set(
                name for name in model_base['inputs'] if type(name) is str)):
        return _closed('BLOCKED', 'INDEPENDENT_MODEL_REQUIRED')
    try:
        model = deepcopy(model_base)
        model['properties'] = [{'id': 'checked_proposal', 'expression': ears['ast']}]
        validate(model)
        model_raw = json.dumps(model, ensure_ascii=False, sort_keys=True,
                               separators=(',', ':'), allow_nan=False).encode('utf-8')
        model_sha = hashlib.sha256(model_raw).hexdigest()
        glossary = {'schema_version': 'rs3-gap-glossary/v1',
                    'model_sha256': model_sha,
                    'variables': deepcopy(glossary_entries)}
        if glossary_state(glossary, model['inputs'], model_sha) != 'READY_PROPOSED':
            return _closed('BLOCKED', 'GLOSSARY_NOT_READY')
        glossary_raw = json.dumps(glossary, ensure_ascii=False, sort_keys=True,
                                  separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, KeyError, MemoryError, RecursionError):
        return _closed('BLOCKED', 'MODEL_OR_GLOSSARY_INVALID')
    if len(model_raw) > 262144 or len(glossary_raw) > 65536:
        return _closed('BLOCKED', 'SYNTHETIC_INPUT_LIMIT')

    try:
        with TemporaryDirectory(prefix='rs3-vertical-') as temp:
            model_path = Path(temp) / 'model.json'
            glossary_path = Path(temp) / 'glossary.json'
            model_path.write_bytes(model_raw)
            glossary_path.write_bytes(glossary_raw)
            observed = run_supervised(
                [sys.executable, '-B', str(ANALYZER), str(model_path),
                 '--glossary', str(glossary_path), '--gap-samples', '1',
                 '--timeout', '6'], 9, output_limit_bytes=1024 * 1024)
        if type(observed) is not dict or observed.get('cleanup_status') != CLEANUP_CONFIRMED:
            return _closed('BLOCKED', 'ANALYZER_CLEANUP_UNCONFIRMED')
        if (observed.get('output_limit') is not False
                or observed.get('timed_out') is not False
                or observed.get('returncode') != 0
                or type(observed.get('stdout_bytes')) is not bytes):
            return _closed('BLOCKED', 'ANALYZER_INCONCLUSIVE')
        report = json.loads(observed['stdout_bytes'].decode('utf-8'))
        props = report['properties']
        if (type(props) is not list or len(props) != 1
                or type(props[0]) is not dict
                or props[0].get('id') != 'checked_proposal'
                or report['provenance']['model_sha256'] != model_sha
                or props[0].get('consequence') != 'NOT_ENTAILED'):
            return _closed('BLOCKED', 'PROPERTY_NOT_FALSIFIED_IN_SYNTHETIC_CASE')
        counterexample = props[0]['counterexample']
        if type(counterexample) is not dict:
            return _closed('BLOCKED', 'PROPERTY_WITNESS_INVALID')
        witness = counterexample.get('witness')
        if (counterexample.get('status') != 'SAT'
                or counterexample.get('witness_check') != 'VERIFIED'
                or not verify_property_witness(model, ears['ast'], witness)):
            return _closed('BLOCKED', 'PROPERTY_WITNESS_INVALID')
        question = json.loads(question_handoff(report))
        if (question['model_sha256'] != model_sha
                or question['status'] != 'PROPOSED_FOR_INTERROGATION'
                or question['source_authenticity'] != 'NOT_ESTABLISHED'):
            return _closed('BLOCKED', 'QUESTION_BINDING_INVALID')
        return {'status': 'QUESTION_PROPOSED', 'reason_code': 'SYNTHETIC_ONLY',
                'source_binding': admitted['source_binding'],
                'source_authenticity': 'NOT_ESTABLISHED',
                'proposal_sha256': ears['proposal_sha256'], 'ears': ears,
                'formal': {'model_sha256': model_sha,
                           'property_ast': ears['ast'],
                           'property_consequence': props[0]['consequence'],
                           'property_counterexample': witness,
                           'guard_gap_status': report['queries']['gap']['status'],
                           'no_output_status': report['queries']['no_output']['status'],
                           'scope': 'INDEPENDENT_SYNTHETIC_MODEL_ONLY'},
                'question': question,
                'authority_verification': 'NOT_ESTABLISHED',
                'execution_authorized': False}
    except (OSError, ValueError, TypeError, KeyError, UnicodeError,
            MemoryError, RecursionError):
        return _closed('BLOCKED', 'VERTICAL_PROBE_INCONCLUSIVE')


def run_followup(first_result, followup_raw, followup_source):
    """Admit a linked synthetic next proposal; never consume a real code."""
    try:
        if (type(first_result) is not dict
                or first_result.get('status') != 'QUESTION_PROPOSED'
                or first_result.get('execution_authorized') is not False
                or type(first_result.get('question')) is not dict
                or type(followup_source) is not SourceSnapshot):
            return _closed('BLOCKED', 'QUESTION_REQUIRED')
        question_sha = first_result['question']['question_sha256']
        handoff = first_result['question']
        binding = {name: handoff[name]
                   for name in ('model_sha256', 'glossary_sha256', 'question')}
        encoded = json.dumps(binding, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode('utf-8')
        expected_sha = hashlib.sha256(b'rs3-question-handoff/v1\n' + encoded).hexdigest()
        if (type(question_sha) is not str or not HEX64.fullmatch(question_sha)
                or question_sha != expected_sha
                or handoff.get('status') != 'PROPOSED_FOR_INTERROGATION'
                or handoff.get('authority') != 'NOT_GRANTED'
                or handoff.get('source_authenticity') != 'NOT_ESTABLISHED'
                or handoff.get('question_count') != 1
                or handoff.get('question_index') != 0
                or handoff['model_sha256'] != first_result['formal']['model_sha256']
                or followup_source.source_ref != 'synthetic/question/' + question_sha):
            return _closed('BLOCKED', 'QUESTION_LINK_MISMATCH')
        admitted, candidate, ears = _admit(followup_raw, followup_source)
        if candidate is None:
            return _closed('BLOCKED', admitted['reason_code'])
        return {'status': 'PROPOSED_NEXT_ITERATION',
                'question_sha256': question_sha,
                'proposal_sha256': ears['proposal_sha256'], 'ears': ears,
                'source_binding': admitted['source_binding'],
                'source_authenticity': 'NOT_ESTABLISHED',
                'card_code_consumption': False, 'authority_git_write': False,
                'authority_verification': 'NOT_ESTABLISHED',
                'execution_authorized': False}
    except (KeyError, TypeError, ValueError, MemoryError):
        return _closed('BLOCKED', 'FOLLOWUP_INCONCLUSIVE')
