"""Ground formal gap samples in a self-declared, unratified source glossary."""

import hashlib
import re


HEX64 = re.compile(r'^[0-9a-f]{64}$')
FIELDS = {'when_true', 'when_false', 'source_ref', 'source_text', 'source_sha256'}


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
                        glossary_sha256=None):
    if glossary is None:
        state = 'NEEDS_GLOSSARY'
    else:
        state = glossary_state(glossary, inputs, model_sha256)
    result = {'status': state, 'questions': [], 'authority': 'NOT_GRANTED',
              'source_authenticity': 'NOT_ESTABLISHED'}
    if state != 'READY_PROPOSED':
        return result
    for packet in packets:
        if packet.get('status') != 'NEEDS_HUMAN_INTERPRETATION':
            continue
        assignment = packet.get('input_assignment')
        if (type(assignment) is not dict or set(assignment) != set(inputs)
                or any(type(value) is not bool for value in assignment.values())
                or packet.get('model_sha256') != model_sha256):
            return {**result, 'status': 'INCONCLUSIVE', 'questions': []}
        phrases = []
        sources = {}
        for name in inputs:
            entry = glossary['variables'][name]
            phrases.append(entry['when_true'] if assignment[name]
                           else entry['when_false'])
            sources[name] = {'source_ref': entry['source_ref'],
                             'source_text': entry['source_text'],
                             'source_sha256': entry['source_sha256']}
        result['questions'].append({
            'text': ('Según el glosario propuesto: ' + '; '.join(phrases) +
                     '. En este escenario no se activa ninguna regla. '
                     '¿Es un requisito faltante, excepción válida, caso fuera '
                     'de alcance, comportamiento prohibido o error del modelo?'),
            'input_assignment': assignment, 'sources': sources,
            'model_sha256': model_sha256,
            'semantic_status': 'PROPOSED_UNVERIFIED'})
    result['status'] = 'PROPOSED_UNVERIFIED' if result['questions'] else 'NO_CANDIDATE'
    result['glossary_sha256'] = glossary_sha256
    return result
