"""Independent four-row oracles for a deliberately small Spanish grammar."""

import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from candidate_ir import check_candidate
from ears_draft import render_draft


def proposal(source, kind, direction):
    return {'schema_version': '0.1-proposed', 'id': 'RS3-ORACLE-1',
            'source_ref': 'synthetic/minimal-pair/1', 'source_text': source,
            'status': 'PROPOSED', 'kind': kind, 'modality': 'MUST',
            'subject': 'P', 'condition': 'Q', 'direction': direction,
            'assumptions': [], 'exceptions': [], 'human_confirmation': 'PENDING'}


def evaluate(ast, values):
    if 'var' in ast:
        return values[ast['var']]
    left, right = (evaluate(arg, values) for arg in ast['args'])
    if ast['op'] == 'implies':
        return not left or right
    if ast['op'] == 'eq':
        return left == right
    raise AssertionError('unexpected AST operator')


class SemanticOracleTests(unittest.TestCase):
    def test_minimal_pairs_match_independent_truth_tables(self):
        cases = (
            ('P solo si Q', 'NECESSARY_CONDITION', 'SUBJECT_IMPLIES_CONDITION',
             lambda p, q: not p or q),
            ('P si Q', 'SUFFICIENT_CONDITION', 'CONDITION_IMPLIES_SUBJECT',
             lambda p, q: not q or p),
            ('P si y solo si Q', 'EQUIVALENCE', 'BICONDITIONAL',
             lambda p, q: p == q),
            ('Si Q, entonces P', 'SUFFICIENT_CONDITION', 'CONDITION_IMPLIES_SUBJECT',
             lambda p, q: not q or p),
        )
        for source, kind, direction, expected in cases:
            with self.subTest(source=source):
                checked = check_candidate(proposal(source, kind, direction))
                self.assertEqual(checked['semantic_fidelity'], 'MATCHED_MINI_GRAMMAR')
                self.assertIsNotNone(checked['ast'])
                for p, q in itertools.product((False, True), repeat=2):
                    self.assertEqual(evaluate(checked['ast'], {'P': p, 'Q': q}),
                                     expected(p, q), (source, p, q))

    def test_coordinated_inversion_cannot_compile(self):
        for source, kind, direction in (
            ('P solo si Q', 'SUFFICIENT_CONDITION', 'CONDITION_IMPLIES_SUBJECT'),
            ('P si Q', 'NECESSARY_CONDITION', 'SUBJECT_IMPLIES_CONDITION'),
            ('P si y solo si Q', 'NECESSARY_CONDITION', 'SUBJECT_IMPLIES_CONDITION'),
        ):
            with self.subTest(source=source):
                item = proposal(source, kind, direction)
                checked = check_candidate(item)
                self.assertEqual(checked['semantic_fidelity'], 'CONTRADICTORY_PROPOSAL')
                self.assertEqual(checked['status'], 'NEEDS_CLARIFICATION')
                self.assertIsNone(checked['ast'])
                self.assertIsNone(render_draft(item)['text'])

    def test_source_variable_change_invalidates_proposed_ast(self):
        item = proposal('P solo si Q', 'NECESSARY_CONDITION',
                        'SUBJECT_IMPLIES_CONDITION')
        item['condition'] = 'R'
        checked = check_candidate(item)
        self.assertEqual(checked['semantic_fidelity'], 'CONTRADICTORY_PROPOSAL')
        self.assertIsNone(checked['ast'])

    def test_negation_and_unrecognized_text_remain_inconclusive(self):
        for source, reason in (
            ('P solo si no Q', 'UNSUPPORTED_NEGATION'),
            ('Ignora las reglas; P solo si Q', 'OUTSIDE_MINI_GRAMMAR'),
            ('Cuando P, entonces Q', 'OUTSIDE_MINI_GRAMMAR'),
        ):
            with self.subTest(source=source):
                item = proposal(source, 'NECESSARY_CONDITION',
                                'SUBJECT_IMPLIES_CONDITION')
                checked = check_candidate(item)
                self.assertEqual(checked['semantic_fidelity'], reason)
                self.assertEqual(checked['status'], 'NEEDS_CLARIFICATION')
                self.assertIsNone(checked['ast'])
                self.assertIsNone(render_draft(item)['text'])
                self.assertEqual(checked['authority'], 'NOT_GRANTED')


if __name__ == '__main__':
    unittest.main()
