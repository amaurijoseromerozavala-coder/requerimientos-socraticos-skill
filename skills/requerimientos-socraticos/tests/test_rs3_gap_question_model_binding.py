"""A model-consistent question requires a real guard gap, not a forged packet."""

import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from gap_glossary import build_gap_questions


MODEL_SHA = 'a' * 64
MODEL = {
    'inputs': ['A', 'B'], 'outputs': ['P'],
    'domain': {'op': 'or', 'args': [{'var': 'A'}, {'var': 'B'}]},
    'rules': [{'id': 'A_active', 'guard': {'var': 'A'},
               'response': {'var': 'P'}}], 'properties': [],
}


def glossary():
    def entry(name):
        source = 'Declaración ' + name
        return {'when_true': name + ' presente', 'when_false': name + ' ausente',
                'source_ref': 'synthetic/' + name, 'source_text': source,
                'source_sha256': hashlib.sha256(source.encode()).hexdigest()}
    return {'schema_version': 'rs3-gap-glossary/v1',
            'model_sha256': MODEL_SHA,
            'variables': {'A': entry('A'), 'B': entry('B')}}


def packet(a, b):
    return {'status': 'NEEDS_HUMAN_INTERPRETATION',
            'input_assignment': {'A': a, 'B': b},
            'model_sha256': MODEL_SHA,
            'formal_query': 'SAT(D AND NOT OR(GUARDS))',
            'inactive_rule_ids': ['A_active'],
            'witness_recheck': 'VERIFIED_BY_Z3_AND_BOOLEAN_EVALUATOR'}


class GapQuestionModelBindingTests(unittest.TestCase):
    def test_forged_gap_outside_domain_or_with_active_guard_is_blocked(self):
        for values in ((False, False), (True, False)):
            with self.subTest(values=values):
                result = build_gap_questions([packet(*values)], glossary(),
                                             MODEL['inputs'], MODEL_SHA,
                                             model=MODEL)
                self.assertEqual(result['status'], 'INCONCLUSIVE')
                self.assertEqual(result['questions'], [])

    def test_real_gap_uses_exact_boolean_phrase_and_remains_proposed(self):
        result = build_gap_questions([packet(False, True)], glossary(),
                                     MODEL['inputs'], MODEL_SHA, model=MODEL)
        self.assertEqual(result['status'], 'PROPOSED_UNVERIFIED')
        self.assertEqual(result['authority'], 'NOT_GRANTED')
        self.assertEqual(result['source_authenticity'], 'NOT_ESTABLISHED')
        self.assertEqual([(item['variable'], item['value'], item['proposed_phrase'])
                          for item in result['questions'][0]['scenario_clauses']],
                         [('A', False, 'A ausente'),
                          ('B', True, 'B presente')])

    def test_missing_model_cannot_prove_question_consistency(self):
        result = build_gap_questions([packet(False, True)], glossary(),
                                     MODEL['inputs'], MODEL_SHA)
        self.assertEqual(result['status'], 'NEEDS_MODEL_RECHECK')
        self.assertEqual(result['questions'], [])

    def test_altered_recheck_claims_are_not_admitted(self):
        for field, altered in (('formal_query', 'SAT(D)'),
                               ('witness_recheck', 'UNVERIFIED'),
                               ('inactive_rule_ids', [])):
            with self.subTest(field=field):
                claim = packet(False, True)
                claim[field] = altered
                result = build_gap_questions([claim], glossary(),
                                             MODEL['inputs'], MODEL_SHA,
                                             model=MODEL)
                self.assertEqual(result['status'], 'INCONCLUSIVE')
                self.assertEqual(result['questions'], [])


if __name__ == '__main__':
    unittest.main()
