"""Synthetic vertical falsifiers; no real model or human authority is inferred."""

import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from source_snapshot import SourceSnapshot
from vertical_probe import run_first, run_followup, verify_property_witness


def proposal(source, *, kind='NECESSARY_CONDITION',
             direction='SUBJECT_IMPLIES_CONDITION'):
    return {'schema_version': '0.1-proposed', 'id': 'RS3-VERTICAL-1',
            'source_ref': source.source_ref, 'source_text': source.source_text,
            'status': 'PROPOSED', 'kind': kind, 'modality': 'MUST',
            'subject': 'P', 'condition': 'Q', 'direction': direction,
            'assumptions': [], 'exceptions': [], 'human_confirmation': 'PENDING'}


def raw(item):
    return json.dumps(item, ensure_ascii=False, sort_keys=True).encode('utf-8')


def fixture():
    source = SourceSnapshot('synthetic/first', 'P solo si Q')
    model = {'inputs': ['P', 'Q'], 'outputs': ['R'], 'domain': True,
             'rules': [{'id': 'guard_P', 'guard': {'var': 'P'},
                        'response': {'var': 'R'}}], 'properties': []}
    entry = {'source_ref': source.source_ref, 'source_text': source.source_text,
             'source_sha256': hashlib.sha256(source.source_text.encode()).hexdigest()}
    glossary = {'P': {**entry, 'when_true': 'P presente',
                      'when_false': 'P ausente'},
                'Q': {**entry, 'when_true': 'Q presente',
                      'when_false': 'Q ausente'}}
    return source, model, glossary


class EndToEndWeakModelTests(unittest.TestCase):
    def first(self):
        source, model, glossary = fixture()
        return run_first(raw(proposal(source)), source, model, glossary)

    def test_synthetic_flow_preserves_distinct_formal_claims_and_no_authority(self):
        first = self.first()
        self.assertEqual(first['status'], 'QUESTION_PROPOSED')
        self.assertEqual(first['source_binding'], 'MATCHED_CALLER_SNAPSHOT')
        self.assertEqual(first['ears']['proposal_sha256'], first['proposal_sha256'])
        self.assertEqual(first['formal']['property_ast'], first['ears']['ast'])
        self.assertEqual(first['formal']['property_consequence'], 'NOT_ENTAILED')
        witness = first['formal']['property_counterexample']
        self.assertIs(witness['P'], True)
        self.assertIs(witness['Q'], False)
        self.assertEqual(first['formal']['guard_gap_status'], 'SAT')
        self.assertEqual(first['formal']['no_output_status'], 'UNSAT')
        question = first['question']
        self.assertEqual(question['status'], 'PROPOSED_FOR_INTERROGATION')
        self.assertEqual(question['model_sha256'], first['formal']['model_sha256'])
        self.assertIs(question['question']['input_assignment']['P'], False)
        self.assertNotEqual(question['question']['input_assignment'], witness)
        self.assertEqual(question['authority'], 'NOT_GRANTED')
        self.assertEqual(first['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(first['execution_authorized'], False)

        next_source = SourceSnapshot('synthetic/question/' + question['question_sha256'],
                                     'P si Q')
        follow = run_followup(first, raw(proposal(
            next_source, kind='SUFFICIENT_CONDITION',
            direction='CONDITION_IMPLIES_SUBJECT')), next_source)
        self.assertEqual(follow['status'], 'PROPOSED_NEXT_ITERATION')
        self.assertNotEqual(follow['proposal_sha256'], first['proposal_sha256'])
        self.assertEqual(follow['ears']['ast']['args'],
                         [{'var': 'Q'}, {'var': 'P'}])
        self.assertIs(follow['card_code_consumption'], False)
        self.assertIs(follow['authority_git_write'], False)
        self.assertIs(follow['execution_authorized'], False)

    def test_bad_proposal_or_independent_model_blocks_before_formal_execution(self):
        source, model, glossary = fixture()
        cases = [(b'{bad', source, model, 'REJECT_INPUT'),
                 (raw(proposal(source)), SourceSnapshot('other', source.source_text),
                  model, 'REJECT_INPUT')]
        reversed_item = proposal(source)
        reversed_item['direction'] = 'CONDITION_IMPLIES_SUBJECT'
        cases.append((raw(reversed_item), source, model, 'REJECT_INPUT'))
        injected = {**model, 'properties': [{'id': 'forged', 'expression': True}]}
        cases.append((raw(proposal(source)), source, injected, 'BLOCKED'))
        with patch('vertical_probe.run_supervised') as runner:
            for response, snapshot, base, expected in cases:
                with self.subTest(expected=expected, response=response[:8]):
                    result = run_first(response, snapshot, base, glossary)
                    self.assertEqual(result['status'], expected)
                    self.assertNotIn('question', result)
                    self.assertIs(result['execution_authorized'], False)
            runner.assert_not_called()

    def test_invalid_glossary_or_uncertain_cleanup_cannot_emit_question(self):
        source, model, glossary = fixture()
        glossary['P']['source_sha256'] = '0' * 64
        result = run_first(raw(proposal(source)), source, model, glossary)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertNotIn('question', result)
        source, model, glossary = fixture()
        with patch('vertical_probe.run_supervised', return_value={
            'cleanup_status': 'INCOMPLETE', 'stdout_bytes': b'{}',
            'returncode': 0, 'output_limit': False, 'timed_out': False}):
            result = run_first(raw(proposal(source)), source, model, glossary)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertNotIn('question', result)
        with patch('vertical_probe.run_supervised', return_value=None):
            result = run_first(raw(proposal(source)), source, model, glossary)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertNotIn('question', result)
        property_ast = {'op': 'implies', 'args': [{'var': 'P'}, {'var': 'Q'}]}
        checked_model = {**model, 'properties': [
            {'id': 'checked_proposal', 'expression': property_ast}]}
        model_bytes = json.dumps(checked_model, ensure_ascii=False,
                                 sort_keys=True, separators=(',', ':')).encode()
        digest = hashlib.sha256(model_bytes).hexdigest()
        bad_reports = ({'properties': [None]},
                       {'properties': [{'id': 'checked_proposal',
                                        'consequence': 'NOT_ENTAILED',
                                        'counterexample': None}],
                        'provenance': {'model_sha256': digest}})
        for report in bad_reports:
            with self.subTest(report=report):
                with patch('vertical_probe.run_supervised', return_value={
                    'cleanup_status': 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED',
                    'stdout_bytes': raw(report), 'returncode': 0,
                    'output_limit': False, 'timed_out': False}):
                    result = run_first(raw(proposal(source)), source, model, glossary)
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertNotIn('question', result)

    def test_property_witness_is_independently_checked(self):
        _, model, _ = fixture()
        ast = {'op': 'implies', 'args': [{'var': 'P'}, {'var': 'Q'}]}
        self.assertTrue(verify_property_witness(model, ast,
                                                {'P': True, 'Q': False, 'R': True}))
        self.assertFalse(verify_property_witness(model, ast,
                                                 {'P': False, 'Q': False, 'R': True}))
        self.assertFalse(verify_property_witness(model, ast,
                                                 {'P': True, 'Q': False}))

    def test_followup_must_link_exact_question_and_remain_unconfirmed(self):
        first = self.first()
        wrong = SourceSnapshot('synthetic/question/' + '0' * 64, 'P si Q')
        result = run_followup(first, raw(proposal(
            wrong, kind='SUFFICIENT_CONDITION',
            direction='CONDITION_IMPLIES_SUBJECT')), wrong)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIs(result['execution_authorized'], False)
        self.assertNotIn('ears', result)
        forged = {**first, 'question': {**first['question'],
                  'question_sha256': '0' * 64}}
        result = run_followup(forged, raw(proposal(
            wrong, kind='SUFFICIENT_CONDITION',
            direction='CONDITION_IMPLIES_SUBJECT')), wrong)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertNotIn('ears', result)


if __name__ == '__main__':
    unittest.main()
