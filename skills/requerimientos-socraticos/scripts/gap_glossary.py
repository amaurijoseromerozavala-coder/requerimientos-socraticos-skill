"""Ground formal gap samples in a self-declared, unratified source glossary."""

import hashlib
import re

from gap_scenario import _evaluate


HEX64 = re.compile(r'^[0-9a-f]{64}$')
FIELDS = {'when_true', 'when_false', 'source_ref', 'source_text', 'source_sha256'}
QUESTION_TEXT = ('En el modelo booleano no se activa ninguna regla para este '
                 'escenario. Revise las descripciones propuestas por separado. '
                 '¿Es un requisito faltante, excepción válida, caso fuera de '
                 'alcance, comportamiento prohibido o error del modelo?')


def _text(value, maximum):
    if (type(value) is not str or not value or len(value) > maximum
            or any(ord(char) < 32 for char in value)):
        raise ValueError('INVALID_GLOSSARY_TEXT')
    return value


def glossary_state(glossary, inputs, model_sha256):
    if (type(glossary) is not dict
            or set(glossary) != {'schema_version', 'model_sha256', 'variables'}
            or glossary['schema_version'] != 'rs3-gap-glossary/v1'
            or type(glossary['model_sha256']) is not str
            or not HEX64.fullmatch(glossary['model_sha256'])
            or type(glossary['variables']) is not dict):
        raise ValueError('INVALID_GLOSSARY_STRUCTURE')
    if glossary['model_sha256'] != model_sha256:
        return 'STALE_GLOSSARY'
    variables = glossary['variables']
    if set(variables) - set(inputs):
        raise ValueError('UNKNOWN_GLOSSARY_VARIABLE')
    for name in variables:
        item = variables[name]
        if type(item) is not dict or set(item) != FIELDS:
            raise ValueError('INVALID_GLOSSARY_ENTRY')
        _text(item['when_true'], 512)
        _text(item['when_false'], 512)
        _text(item['source_ref'], 512)
        source = _text(item['source_text'], 2048)
        digest = item['source_sha256']
        if (type(digest) is not str or not HEX64.fullmatch(digest)
                or hashlib.sha256(source.encode('utf-8')).hexdigest() != digest):
            raise ValueError('SOURCE_TEXT_DIGEST_MISMATCH')
    if set(inputs) - set(variables):
        return 'NEEDS_GLOSSARY'
    return 'READY_PROPOSED'


def build_gap_questions(packets, glossary, inputs, model_sha256,
                        glossary_sha256=None, model=None):
    if glossary is None:
        state = 'NEEDS_GLOSSARY'
    else:
        state = glossary_state(glossary, inputs, model_sha256)
    result = {'status': state, 'questions': [], 'authority': 'NOT_GRANTED',
              'source_authenticity': 'NOT_ESTABLISHED'}
    if state != 'READY_PROPOSED':
        return result
    if (type(model) is not dict or model.get('inputs') != inputs
            or type(model.get('rules')) is not list or 'domain' not in model):
        return {**result, 'status': 'NEEDS_MODEL_RECHECK'}
    for packet in packets:
        if packet.get('status') != 'NEEDS_HUMAN_INTERPRETATION':
            continue
        assignment = packet.get('input_assignment')
        if (type(assignment) is not dict or set(assignment) != set(inputs)
                or any(type(value) is not bool for value in assignment.values())
                or packet.get('model_sha256') != model_sha256
                or packet.get('formal_query') != 'SAT(D AND NOT OR(GUARDS))'
                or packet.get('witness_recheck') != 'VERIFIED_BY_Z3_AND_BOOLEAN_EVALUATOR'
                or packet.get('inactive_rule_ids') != [rule['id'] for rule in model['rules']]):
            return {**result, 'status': 'INCONCLUSIVE', 'questions': []}
        try:
            if (not _evaluate(model['domain'], assignment)
                    or any(_evaluate(rule['guard'], assignment)
                           for rule in model['rules'])):
                return {**result, 'status': 'INCONCLUSIVE', 'questions': []}
        except (KeyError, TypeError, ValueError):
            return {**result, 'status': 'INCONCLUSIVE', 'questions': []}
        scenario_clauses = []
        sources = {}
        for name in inputs:
            entry = glossary['variables'][name]
            scenario_clauses.append({
                'variable': name, 'value': assignment[name],
                'proposed_phrase': (entry['when_true'] if assignment[name]
                                    else entry['when_false']),
                'source_ref': entry['source_ref']})
            sources[name] = {'source_ref': entry['source_ref'],
                             'source_text': entry['source_text'],
                             'source_sha256': entry['source_sha256']}
        result['questions'].append({
            'text': QUESTION_TEXT,
            'text_origin': 'SYSTEM_TEMPLATE',
            'scenario_clauses': scenario_clauses,
            'scenario_clauses_origin': 'UNTRUSTED_GLOSSARY_DATA',
            'input_assignment': assignment, 'sources': sources,
            'model_sha256': model_sha256,
            'semantic_status': 'PROPOSED_UNVERIFIED'})
    result['status'] = 'PROPOSED_UNVERIFIED' if result['questions'] else 'NO_CANDIDATE'
    result['glossary_sha256'] = glossary_sha256
    return result
