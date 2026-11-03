"""Closed RS3 query templates over explicitly supplied Boolean models."""
from pathlib import Path
import sys
import unittest

import z3

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from formal_queries import QueryContext, QueryKind


V = lambda name: {'var': name}
OP = lambda op, *args: {'op': op, 'args': list(args)}


def solve(formula):
    solver = z3.Solver()
    solver.add(formula)
    return str(solver.check()).upper()


class ClosedQueryFactoryTests(unittest.TestCase):
    def test_no_output_counterexample_and_wrong_mutant(self):
        model = {'inputs': ['A', 'B'], 'outputs': ['P'], 'domain': True,
                 'rules': [{'id': 'r', 'guard': True,
                            'response': OP('implies', V('A'), V('B'))}],
                 'properties': []}
        context = QueryContext(model, z3)
        query = context.formula(QueryKind.NO_OUTPUT)
        self.assertEqual(solve(query), 'SAT')
        self.assertEqual(solve(z3.And(query, z3.Bool('A'), z3.Not(z3.Bool('B')))), 'SAT')
        self.assertEqual(solve(z3.And(context.obligations, query)), 'UNSAT')

    def test_all_declared_outputs_are_quantified(self):
        model = {'inputs': [], 'outputs': ['P', 'Q'], 'domain': True,
                 'rules': [{'id': 'r', 'guard': True,
                            'response': OP('and', V('P'), V('Q'))}],
                 'properties': []}
        context = QueryContext(model, z3)
        self.assertEqual(solve(context.formula(QueryKind.NO_OUTPUT)), 'UNSAT')
        wrong_partial = z3.Not(z3.Exists([context.variables['P']], context.obligations))
        self.assertEqual(solve(wrong_partial), 'SAT')

    def test_gap_and_rule_consistency_remain_separate(self):
        model = {'inputs': ['A'], 'outputs': ['P'], 'domain': True,
                 'rules': [{'id': 'r', 'guard': False, 'response': V('P')}],
                 'properties': []}
        context = QueryContext(model, z3)
        self.assertEqual(solve(context.formula(QueryKind.GAP)), 'SAT')
        self.assertEqual(solve(context.formula(QueryKind.NO_OUTPUT)), 'UNSAT')
        self.assertEqual(solve(context.formula(QueryKind.RULE_CONSISTENCY)), 'SAT')

    def test_only_closed_typed_operations_are_accepted(self):
        model = {'inputs': [], 'outputs': [], 'domain': True,
                 'rules': [], 'properties': []}
        context = QueryContext(model, z3)
        self.assertEqual(solve(context.formula(QueryKind.DOMAIN)), 'SAT')
        with self.assertRaises(ValueError):
            context.formula('no_output')
        with self.assertRaises(TypeError):
            context.formula(QueryKind.NO_OUTPUT, ['untrusted_override'])


if __name__ == '__main__':
    unittest.main()
