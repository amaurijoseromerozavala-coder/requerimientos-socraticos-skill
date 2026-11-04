"""Convert a checked Boolean GAP witness into an unratified interview packet.

This module evaluates the validated Boolean AST independently of Z3. It cannot
infer the domain meaning of variable names or authorize a new requirement.
"""


def _evaluate(node, values):
    if type(node) is bool:
        return node
    if type(node) is not dict:
        raise ValueError('INVALID_EXPRESSION')
    if set(node) == {'var'}:
        value = values[node['var']]
        if type(value) is not bool:
            raise ValueError('INVALID_WITNESS_VALUE')
        return value
    if set(node) != {'op', 'args'} or type(node['args']) is not list:
        raise ValueError('INVALID_EXPRESSION')
    op = node['op']
    args = [_evaluate(item, values) for item in node['args']]
    if op == 'and' and len(args) >= 2:
        return all(args)
    if op == 'or' and len(args) >= 2:
        return any(args)
    if op == 'not' and len(args) == 1:
        return not args[0]
    if op == 'implies' and len(args) == 2:
        return not args[0] or args[1]
    if op == 'eq' and len(args) == 2:
        return args[0] == args[1]
    raise ValueError('INVALID_EXPRESSION')


def build_gap_interpretation(model, gap_query, model_sha256):
    """Return an interview candidate only for an independently checked gap."""
    if gap_query.get('status') == 'UNSAT':
        return {'status': 'NO_CANDIDATE', 'scope': 'SUPPLIED_BOOLEAN_MODEL_ONLY'}
    if gap_query.get('status') != 'SAT':
        return {'status': 'INCONCLUSIVE', 'reason': 'GAP_QUERY_NOT_SAT'}
    witness = gap_query.get('witness')
    inputs = model['inputs']
    if (gap_query.get('witness_check') != 'VERIFIED'
            or type(witness) is not dict or set(witness) != set(inputs)
            or any(type(value) is not bool for value in witness.values())):
        return {'status': 'INCONCLUSIVE', 'reason': 'WITNESS_NOT_VERIFIED'}
    try:
        if not _evaluate(model['domain'], witness):
            return {'status': 'INCONCLUSIVE', 'reason': 'DOMAIN_RECHECK_FAILED'}
        if any(_evaluate(rule['guard'], witness) for rule in model['rules']):
            return {'status': 'INCONCLUSIVE', 'reason': 'GUARD_RECHECK_FAILED'}
    except (KeyError, TypeError, ValueError):
        return {'status': 'INCONCLUSIVE', 'reason': 'EXPRESSION_RECHECK_FAILED'}
    assignment = {name: witness[name] for name in inputs}
    valuation = ', '.join(name + '=' + ('verdadero' if assignment[name] else 'falso')
                          for name in inputs)
    return {
        'status': 'NEEDS_HUMAN_INTERPRETATION',
        'formal_query': 'SAT(D AND NOT OR(GUARDS))',
        'scenario_scope': 'SINGLE_WITNESS_NOT_ALL_COMBINATIONS',
        'remaining_gap_space': 'NOT_ENUMERATED',
        'model_sha256': model_sha256,
        'input_assignment': assignment,
        'inactive_rule_ids': [rule['id'] for rule in model['rules']],
        'witness_recheck': 'VERIFIED_BY_Z3_AND_BOOLEAN_EVALUATOR',
        'semantic_status': 'UNINTERPRETED',
        'meaning_source': 'SOURCE_TRACE_AND_GLOSSARY_REQUIRED',
        'authority': 'PROPOSAL_ONLY',
        'hypotheses_for_human': [
            'MISSING_REQUIREMENT', 'VALID_EXCEPTION', 'OUT_OF_SCOPE',
            'FORBIDDEN_BEHAVIOR', 'MODEL_ERROR', 'NEEDS_CLARIFICATION'],
        'neutral_question': ('En el modelo, ' + valuation +
                             ' cumple el dominio y no activa ninguna regla. '
                             '¿Qué significa este escenario en el problema real?'),
        'limitation': ('A guard gap does not imply no compatible output, '
                       'a physical failure, or a missing requirement.'),
    }
