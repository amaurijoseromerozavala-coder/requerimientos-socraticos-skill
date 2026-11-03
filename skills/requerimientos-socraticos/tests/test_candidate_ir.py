"""RS3 proposed IR: syntactic compilation never grants human authority."""
import copy
from pathlib import Path
import sys
import unittest
import json
from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from candidate_ir import CandidateError, check_candidate


def proposal():
    return {'schema_version': '0.1-proposed', 'id': 'RS3-EXAMPLE-1',
            'source_ref': 'interview/question-1/revision-1',
            'source_text': 'P solo si Q', 'status': 'PROPOSED',
            'kind': 'NECESSARY_CONDITION', 'modality': 'MUST',
            'subject': 'P', 'condition': 'Q',
            'direction': 'SUBJECT_IMPLIES_CONDITION',
            'assumptions': [], 'exceptions': [],
            'human_confirmation': 'PENDING'}


class CandidateIRTests(unittest.TestCase):
    def test_necessary_direction_is_not_inverted(self):
        result = check_candidate(proposal())
        self.assertEqual(result['ast'], {'op': 'implies',
                                         'args': [{'var': 'P'}, {'var': 'Q'}]})
        self.assertEqual(result['status'], 'PROPOSED')
        self.assertEqual(result['authority'], 'NOT_GRANTED')
        self.assertNotIn('HUMAN_CONFIRMED', str(result))

    def test_sufficient_and_equivalence_directions(self):
        item = proposal()
        item.update(kind='SUFFICIENT_CONDITION', direction='CONDITION_IMPLIES_SUBJECT',
                    source_text='Si Q, entonces P')
        self.assertEqual(check_candidate(item)['ast'],
                         {'op': 'implies', 'args': [{'var': 'Q'}, {'var': 'P'}]})
        item.update(kind='EQUIVALENCE', direction='BICONDITIONAL',
                    source_text='P si y solo si Q')
        self.assertEqual(check_candidate(item)['ast'],
                         {'op': 'eq', 'args': [{'var': 'P'}, {'var': 'Q'}]})

    def test_mismatched_direction_is_rejected(self):
        item = proposal()
        item['direction'] = 'CONDITION_IMPLIES_SUBJECT'
        with self.assertRaisesRegex(CandidateError, 'DIRECTION_MISMATCH'):
            check_candidate(item)

    def test_modalities_and_unmodelled_context_do_not_compile(self):
        for change in ({'modality': 'MAY'}, {'modality': 'SHOULD'},
                       {'modality': 'UNDETERMINED'},
                       {'exceptions': ['except when E']},
                       {'assumptions': ['only in region X']},
                       {'status': 'NEEDS_CLARIFICATION'}):
            with self.subTest(change=change):
                item = proposal()
                item.update(change)
                result = check_candidate(item)
                self.assertIsNone(result['ast'])
                self.assertEqual(result['status'], 'NEEDS_CLARIFICATION')
                self.assertEqual(result['authority'], 'NOT_GRANTED')

    def test_claimed_authority_and_unknown_fields_are_rejected(self):
        for change in ({'human_confirmation': 'HUMAN_CONFIRMED'},
                       {'execution_authorized': True},
                       {'status': 'HUMAN_CONFIRMED'},
                       {'subject': False},
                       {'source_text': ''},
                       {'condition': 'invalid-role!'}):
            with self.subTest(change=change):
                item = proposal()
                item.update(change)
                with self.assertRaises(CandidateError):
                    check_candidate(item)

    def test_input_is_not_mutated_and_source_is_bound_to_digest(self):
        item = proposal()
        previous = copy.deepcopy(item)
        result = check_candidate(item)
        self.assertEqual(item, previous)
        self.assertEqual(len(result['source_sha256']), 64)
        item['source_text'] = 'P solo si R'
        self.assertNotEqual(check_candidate(item)['source_sha256'], result['source_sha256'])

    def test_unhashable_and_oversized_fields_reject_with_typed_error(self):
        for change in ({'kind': []}, {'modality': {}},
                       {'source_text': 'A' * 4097},
                       {'assumptions': ['A'] * 17}):
            with self.subTest(change=str(change)[:40]):
                item = proposal()
                item.update(change)
                with self.assertRaises(CandidateError):
                    check_candidate(item)

    def test_published_schema_and_helper_admit_same_basic_proposal(self):
        schema_path = Path(__file__).resolve().parents[1] / 'assets' / 'candidate-ir-proposed.schema.json'
        schema = json.loads(schema_path.read_text(encoding='utf-8'))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        self.assertFalse(list(validator.iter_errors(proposal())))
        invalid = proposal()
        invalid['human_confirmation'] = 'HUMAN_CONFIRMED'
        self.assertTrue(list(validator.iter_errors(invalid)))

    def test_unpaired_unicode_surrogates_have_typed_rejection(self):
        surrogate = chr(0xd800)
        for field, value in (('source_text', 'P ' + surrogate + ' Q'),
                             ('source_ref', 'source/' + surrogate),
                             ('assumptions', [surrogate]),
                             ('exceptions', [surrogate])):
            with self.subTest(field=field):
                item = proposal()
                item[field] = value
                with self.assertRaises(CandidateError):
                    check_candidate(item)


if __name__ == '__main__':
    unittest.main()
