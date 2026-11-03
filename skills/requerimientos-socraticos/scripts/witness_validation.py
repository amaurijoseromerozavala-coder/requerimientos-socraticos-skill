"""Recheck a bounded Boolean witness; no claim about physical observations."""
import time


def verify_assignment(formula, witness, expected_names, variables, z3, deadline):
    if (type(witness) is not dict or set(witness) != set(expected_names)
            or any(type(value) is not bool for value in witness.values())
            or any(name not in variables for name in expected_names)):
        return 'INVALID'
    remaining = deadline - time.monotonic()
    if remaining < .001:
        return 'UNKNOWN'
    solver = z3.Solver()
    solver.set(timeout=max(1, min(1000, int(remaining * 1000))))
    solver.add(formula)
    solver.add(*[variables[name] == witness[name] for name in expected_names])
    answer = solver.check()
    if time.monotonic() >= deadline:
        return 'UNKNOWN'
    if answer == z3.sat:
        return 'VERIFIED'
    if answer == z3.unsat:
        return 'REFUTED'
    return 'UNKNOWN'
