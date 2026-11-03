"""Absolute and contextual rule equivalence have distinct, reproducible scope."""
from pathlib import Path
import sys
import unittest

import z3

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from formal_queries import EquivalenceScope, QueryContext, QueryKind
from logic_engine import validate


def var(name):
    return {'var': name}


def op(kind, *args):
    return {'op': kind, 'args': list(args)}


def model(domain=True, other=False):
    rules = [{'id': 'left', 'guard': True, 'response': var('A')},
             {'id': 'right', 'guard': True, 'response': var('B')}]
    if other:
        rules.append({'id': 'other', 'guard': True,
                      'response': op('eq', var('A'), var('B'))})
    return {'inputs': ['A', 'B'], 'outputs': [], 'domain': domain,
            'rules': rules, 'properties': []}


def answer(formula):
    solver = z3.Solver()
    solver.add(formula)
    return str(solver.check()).upper()


class FormalEquivalenceTests(unittest.TestCase):
    def test_domain_can_hide_absolute_difference(self):
        item = model(op('eq', var('A'), var('B')))
        validate(item)
        context = QueryContext(item, z3)
        self.assertEqual(answer(context.equivalence_formula(
            'left', 'right', EquivalenceScope.ABSOLUTE)), 'SAT')
        self.assertEqual(answer(context.equivalence_formula(
            'left', 'right', EquivalenceScope.CONTEXTUAL)), 'UNSAT')

    def test_compared_rules_are_excluded_from_context(self):
        item = model()
        validate(item)
        context = QueryContext(item, z3)
        self.assertEqual(answer(context.equivalence_formula(
            'left', 'right', EquivalenceScope.CONTEXTUAL)), 'SAT')

    def test_other_rule_can_remove_contextual_difference_only(self):
        item = model(other=True)
        validate(item)
        context = QueryContext(item, z3)
        self.assertEqual(answer(context.equivalence_formula(
            'left', 'right', EquivalenceScope.ABSOLUTE)), 'SAT')
        self.assertEqual(answer(context.equivalence_formula(
            'left', 'right', EquivalenceScope.CONTEXTUAL)), 'UNSAT')

    def test_scope_and_rule_identifiers_are_closed(self):
        item = model()
        validate(item)
        context = QueryContext(item, z3)
        for left, right, scope in (('left', 'right', 'contextual'),
                                   ('missing', 'right', EquivalenceScope.ABSOLUTE),
                                   ('left', 'left', EquivalenceScope.ABSOLUTE)):
            with self.subTest(left=left, right=right, scope=scope):
                with self.assertRaisesRegex(ValueError, 'QUERY_TEMPLATE_MISMATCH'):
                    context.equivalence_formula(left, right, scope)

    def test_true_guard_changes_gap_even_when_obligation_matches(self):
        first = {'inputs': ['A'], 'outputs': ['R'], 'domain': True,
                 'rules': [{'id': 'rule', 'guard': var('A'), 'response': var('R')}],
                 'properties': []}
        second = {'inputs': ['A'], 'outputs': ['R'], 'domain': True,
                  'rules': [{'id': 'rule', 'guard': True,
                             'response': op('implies', var('A'), var('R'))}],
                  'properties': []}
        for item in (first, second):
            validate(item)
        old, new = QueryContext(first, z3), QueryContext(second, z3)
        self.assertEqual(answer(z3.Xor(old.obligations, new.obligations)), 'UNSAT')
        self.assertEqual(answer(old.formula(QueryKind.NO_OUTPUT)), 'UNSAT')
        self.assertEqual(answer(new.formula(QueryKind.NO_OUTPUT)), 'UNSAT')
        self.assertEqual(answer(old.formula(QueryKind.GAP)), 'SAT')
        self.assertEqual(answer(new.formula(QueryKind.GAP)), 'UNSAT')


if __name__ == '__main__':
    unittest.main()
