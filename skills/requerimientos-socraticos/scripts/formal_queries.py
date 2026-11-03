"""Closed Boolean query templates for the existing bounded Z3 analyzer.

The caller validates the model before constructing this context. This module
does not run a solver or accept user-supplied query expressions.
"""
from enum import Enum


class QueryKind(Enum):
    DOMAIN = 'domain'
    GAP = 'gap'
    NO_OUTPUT = 'no_output'
    RULE_CONSISTENCY = 'rule_consistency'


class EquivalenceScope(Enum):
    ABSOLUTE = 'absolute'
    CONTEXTUAL = 'contextual'


class QueryContext:
    def __init__(self, model, z3):
        self.z3 = z3
        self.variables = {name: z3.Bool(name) for name in model['inputs'] + model['outputs']}
        self.domain = self.compile_expr(model['domain'])
        self.rule_ids = {rule['id']: index for index, rule in enumerate(model['rules'])}
        self.guards = [self.compile_expr(rule['guard']) for rule in model['rules']]
        self.rule_clauses = [
            z3.Implies(guard, self.compile_expr(rule['response']))
            for guard, rule in zip(self.guards, model['rules'])]
        self.obligations = z3.And(*self.rule_clauses)
        self.covered = z3.Or(*self.guards)
        outputs = [self.variables[name] for name in model['outputs']]
        self.feasible_output = (z3.Exists(outputs, self.obligations)
                                if outputs else self.obligations)

    def compile_expr(self, expression):
        if type(expression) is bool:
            return self.z3.BoolVal(expression)
        if 'var' in expression:
            return self.variables[expression['var']]
        arguments = [self.compile_expr(child) for child in expression['args']]
        operation = expression['op']
        if operation == 'and':
            return self.z3.And(*arguments)
        if operation == 'or':
            return self.z3.Or(*arguments)
        if operation == 'not':
            return self.z3.Not(arguments[0])
        if operation == 'implies':
            return self.z3.Implies(*arguments)
        if operation == 'eq':
            return arguments[0] == arguments[1]
        raise ValueError('unsupported validated expression')

    def equivalence_formula(self, left_id, right_id, scope):
        """Return a counterexample formula for two validated model rules.

        SAT means a difference in the selected scope; UNSAT means equivalence
        only within that scope. The caller runs and bounds the solver.
        """
        if (type(scope) is not EquivalenceScope or type(left_id) is not str
                or type(right_id) is not str or left_id == right_id
                or left_id not in self.rule_ids or right_id not in self.rule_ids):
            raise ValueError('QUERY_TEMPLATE_MISMATCH')
        left, right = self.rule_ids[left_id], self.rule_ids[right_id]
        difference = self.z3.Xor(self.rule_clauses[left], self.rule_clauses[right])
        if scope is EquivalenceScope.ABSOLUTE:
            return difference
        others = [clause for index, clause in enumerate(self.rule_clauses)
                  if index not in (left, right)]
        return self.z3.And(self.domain, *others, difference)

    def formula(self, kind):
        if type(kind) is not QueryKind:
            raise ValueError('QUERY_TEMPLATE_MISMATCH')
        if kind is QueryKind.DOMAIN:
            return self.domain
        if kind is QueryKind.GAP:
            return self.z3.And(self.domain, self.z3.Not(self.covered))
        if kind is QueryKind.NO_OUTPUT:
            return self.z3.And(self.domain, self.z3.Not(self.feasible_output))
        if kind is QueryKind.RULE_CONSISTENCY:
            return self.z3.And(self.domain, self.obligations)
        raise ValueError('QUERY_TEMPLATE_MISMATCH')
