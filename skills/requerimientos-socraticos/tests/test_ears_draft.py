"""RS3 EARS drafts preserve typed direction and never grant authority."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from ears_draft import render_draft
from candidate_ir import CandidateError, check_candidate


def candidate():
    return {'schema_version': '0.1-proposed', 'id': 'RS3-EXAMPLE-2',
            'source_ref': 'interview/question-2/revision-1',
            'source_text': 'P solo si Q', 'status': 'PROPOSED',
            'kind': 'NECESSARY_CONDITION', 'modality': 'MUST',
            'subject': 'P', 'condition': 'Q',
            'direction': 'SUBJECT_IMPLIES_CONDITION',
            'assumptions': [], 'exceptions': [], 'human_confirmation': 'PENDING'}


class EarsDraftTests(unittest.TestCase):
    def test_ears_draft_binds_exact_proposal_without_granting_authority(self):
        item = candidate()
        result = render_draft(item)
        self.assertEqual(result['proposal_sha256'], check_candidate(item)['proposal_sha256'])
        self.assertEqual(result['authority'], 'NOT_GRANTED')
        self.assertIs(result['execution_authorized'], False)

    def test_necessary_sufficient_and_equivalence_keep_direction(self):
        item = candidate()
        first = render_draft(item)
        self.assertEqual(first['ast']['args'], [{'var': 'P'}, {'var': 'Q'}])
        self.assertIn('si «P» es verdadero, entonces «Q»', first['text'])
        item.update(kind='SUFFICIENT_CONDITION', direction='CONDITION_IMPLIES_SUBJECT')
        second = render_draft(item)
        self.assertEqual(second['ast']['args'], [{'var': 'Q'}, {'var': 'P'}])
        self.assertIn('si «Q» es verdadero, entonces «P»', second['text'])
        item.update(kind='EQUIVALENCE', direction='BICONDITIONAL')
        third = render_draft(item)
        self.assertEqual(third['ast']['op'], 'eq')
        self.assertIn('mismo valor de verdad', third['text'])

    def test_unmodelled_context_never_emits_normative_sentence(self):
        for change in ({'modality': 'MAY'}, {'modality': 'SHOULD'},
                       {'exceptions': ['excepto E']},
                       {'assumptions': ['solo en X']},
                       {'status': 'NEEDS_CLARIFICATION'}):
            with self.subTest(change=change):
                item = candidate()
                item.update(change)
                result = render_draft(item)
                self.assertEqual(result['status'], 'NEEDS_CLARIFICATION')
                self.assertIsNone(result['text'])
                self.assertIsNone(result['ast'])

    def test_review_eligible_meaning_is_documentary_only(self):
        item = candidate()
        item['subject'] = 'production_ready'
        result = render_draft(item)
        self.assertIn('elegible para revisión documental', result['text'])
        self.assertEqual(result['ast']['args'][0], {'var': 'production_ready'})
        self.assertEqual(result['meaning'], 'REVIEW_ELIGIBLE_DOCUMENTARY_ONLY')
        self.assertEqual(result['authority'], 'NOT_GRANTED')
        self.assertIs(result['execution_authorized'], False)
        self.assertNotIn('despliegue', result['text'].lower())

    def test_unsupported_claimed_confirmation_is_rejected(self):
        item = candidate()
        item['human_confirmation'] = 'HUMAN_CONFIRMED'
        with self.assertRaises(CandidateError):
            render_draft(item)


if __name__ == '__main__':
    unittest.main()
