"""Small exhaustive reference oracle, restricted to synthetic Boolean fixtures.

This module is test support. It does not invoke Z3 or share production query code.
"""
from itertools import product


def evaluate(expression, assignment):
    if type(expression) is bool:
        return expression
    if 'var' in expression:
        return assignment[expression['var']]
    values = [evaluate(item, assignment) for item in expression['args']]
    operation = expression['op']
    if operation == 'and':
        return all(values)
    if operation == 'or':
        return any(values)
    if operation == 'not':
        return not values[0]
    if operation == 'implies':
        return not values[0] or values[1]
    if operation == 'eq':
        return values[0] == values[1]
    raise ValueError('unsupported fixture expression')


def assignments(names):
    for bits in product((False, True), repeat=len(names)):
        yield dict(zip(names, bits))


def obligations_hold(model, assignment):
    return all(not evaluate(rule['guard'], assignment) or
               evaluate(rule['response'], assignment)
               for rule in model['rules'])


def classify_inputs(model):
    if len(model['inputs']) + len(model['outputs']) > 8:
        raise ValueError('reference oracle fixture limit')
    result = {'domain': [], 'gap': [], 'no_output': [], 'compatible_pairs': []}
    for inputs in assignments(model['inputs']):
        if not evaluate(model['domain'], inputs):
            continue
        result['domain'].append(inputs)
        if not any(evaluate(rule['guard'], inputs) for rule in model['rules']):
            result['gap'].append(inputs)
        compatible = []
        for outputs in assignments(model['outputs']):
            pair = {**inputs, **outputs}
            if obligations_hold(model, pair):
                compatible.append(pair)
        result['compatible_pairs'].extend(compatible)
        if not compatible:
            result['no_output'].append(inputs)
    return result


def mutant_no_output(model):
    """Counterfactual D ∧ C ∧ ¬∃outputs:C, never the normative query."""
    classification = classify_inputs(model)
    return [inputs for inputs in classification['no_output']
            if any(all(pair[name] == value for name, value in inputs.items())
                   for pair in classification['compatible_pairs'])]
