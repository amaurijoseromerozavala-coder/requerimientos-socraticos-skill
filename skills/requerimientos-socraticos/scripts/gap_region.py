"""Bounded, false-first enumeration of uncovered Boolean input assignments."""

import time

from formal_queries import QueryKind
from witness_validation import verify_assignment


def sample_gap_region(model, context, z3, deadline, sample_limit):
    """Return only checked samples; exactness is scoped to the supplied model."""
    if sample_limit == 0:
        return {'status': 'NOT_RUN', 'sample_limit': 0, 'samples': [],
                'remaining': 'NOT_ASSESSED'}
    inputs = model['inputs']
    variables = context.variables
    formula = context.formula(QueryKind.GAP)
    blocked = []
    samples = []

    def check(extra=()):
        remaining = deadline - time.monotonic()
        if remaining < .001:
            return 'UNKNOWN'
        solver = z3.Solver()
        solver.set(timeout=max(1, min(1000, int(remaining * 1000))))
        solver.add(formula, *blocked, *extra)
        answer = solver.check()
        if time.monotonic() >= deadline:
            return 'UNKNOWN'
        return str(answer).upper()

    def inconclusive(reason):
        return {'status': 'INCONCLUSIVE', 'sample_limit': sample_limit,
                'samples': samples, 'remaining': 'UNKNOWN', 'reason': reason}

    for _ in range(sample_limit):
        basis = check()
        if basis == 'UNSAT':
            return {'status': 'EXACT_WITHIN_SUPPLIED_MODEL',
                    'sample_limit': sample_limit, 'samples': samples,
                    'remaining': 'NONE_IN_SUPPLIED_MODEL'}
        if basis != 'SAT':
            return inconclusive('SOLVER_OR_DEADLINE_UNKNOWN')

        prefix = []
        assignment = {}
        for name in inputs:
            false_constraint = z3.Not(variables[name])
            false_status = check((*prefix, false_constraint))
            if false_status == 'SAT':
                value = False
                chosen_constraint = false_constraint
            elif false_status == 'UNSAT':
                true_constraint = variables[name]
                if check((*prefix, true_constraint)) != 'SAT':
                    return inconclusive('SOLVER_OR_DEADLINE_UNKNOWN')
                value = True
                chosen_constraint = true_constraint
            else:
                return inconclusive('SOLVER_OR_DEADLINE_UNKNOWN')
            assignment[name] = value
            prefix.append(chosen_constraint)

        checked = verify_assignment(z3.And(formula, *blocked), assignment,
                                    inputs, variables, z3, deadline)
        if checked != 'VERIFIED':
            return inconclusive('WITNESS_RECHECK_' + checked)
        samples.append({'status': 'SAT', 'witness_check': 'VERIFIED',
                        'witness': assignment})
        blocked.append(z3.Or(*[variables[name] != assignment[name]
                               for name in inputs]))

    remainder = check()
    if remainder == 'UNSAT':
        status, remaining = 'EXACT_WITHIN_SUPPLIED_MODEL', 'NONE_IN_SUPPLIED_MODEL'
    elif remainder == 'SAT':
        status, remaining = 'PARTIAL_LIMIT', 'EXISTS_IN_SUPPLIED_MODEL'
    else:
        return inconclusive('REMAINDER_UNKNOWN')
    return {'status': status, 'sample_limit': sample_limit,
            'samples': samples, 'remaining': remaining}
