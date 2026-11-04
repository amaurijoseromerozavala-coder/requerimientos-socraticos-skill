#!/usr/bin/env python3
"""Render proposed gap questions as inert, read-only HTML on stdout."""

import argparse
from html import escape
import hashlib
import json
from pathlib import Path
import re
import sys

from gap_glossary import QUESTION_TEXT
from json_preflight import preflight_json
from safe_io import read_regular


MAX_INPUT_BYTES = 1024 * 1024
NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]{0,63}$')
HEX64 = re.compile(r'^[0-9a-f]{64}$')


def _text(value, maximum):
    if (type(value) is not str or not value or len(value.encode('utf-8')) > maximum
            or any(ord(char) < 32 for char in value)):
        raise ValueError('INVALID_VIEW_TEXT')
    return value


def _validate(packet):
    if (type(packet) is not dict or packet.get('status') != 'PROPOSED_UNVERIFIED'
            or packet.get('authority') != 'NOT_GRANTED'
            or packet.get('source_authenticity') != 'NOT_ESTABLISHED'
            or type(packet.get('questions')) is not list
            or not 1 <= len(packet['questions']) <= 16):
        raise ValueError('INVALID_VIEW_PACKET')
    for question in packet['questions']:
        if (type(question) is not dict or question.get('text') != QUESTION_TEXT
                or question.get('text_origin') != 'SYSTEM_TEMPLATE'
                or question.get('scenario_clauses_origin') != 'UNTRUSTED_GLOSSARY_DATA'
                or question.get('semantic_status') != 'PROPOSED_UNVERIFIED'
                or type(question.get('model_sha256')) is not str
                or not HEX64.fullmatch(question['model_sha256'])):
            raise ValueError('INVALID_VIEW_QUESTION')
        clauses = question.get('scenario_clauses')
        assignment = question.get('input_assignment')
        sources = question.get('sources')
        if (type(clauses) is not list or not 1 <= len(clauses) <= 32
                or type(assignment) is not dict or type(sources) is not dict):
            raise ValueError('INVALID_VIEW_CLAUSES')
        seen = set()
        for clause in clauses:
            if type(clause) is not dict or set(clause) != {
                    'variable', 'value', 'proposed_phrase', 'source_ref'}:
                raise ValueError('INVALID_VIEW_CLAUSE')
            name = clause['variable']
            if (type(name) is not str or not NAME.fullmatch(name)
                    or name in seen or type(clause['value']) is not bool
                    or name not in assignment or assignment[name] is not clause['value']
                    or name not in sources or type(sources[name]) is not dict
                    or sources[name].get('source_ref') != clause['source_ref']):
                raise ValueError('INCONSISTENT_VIEW_CLAUSE')
            _text(clause['proposed_phrase'], 512)
            _text(clause['source_ref'], 512)
            source = sources[name]
            source_text = _text(source.get('source_text'), 2048)
            source_digest = source.get('source_sha256')
            if (type(source_digest) is not str
                    or not HEX64.fullmatch(source_digest)
                    or hashlib.sha256(source_text.encode('utf-8')).hexdigest()
                    != source_digest):
                raise ValueError('INCONSISTENT_VIEW_SOURCE')
            seen.add(name)
        if seen != set(assignment) or seen != set(sources):
            raise ValueError('INCOMPLETE_VIEW_CLAUSES')


def render_document(packet):
    """Return HTML only after validating every question; never capture a choice."""
    _validate(packet)
    parts = [
        '<!doctype html><html lang="es"><head><meta charset="utf-8">',
        '<meta http-equiv="Content-Security-Policy" '
        'content="default-src \'none\'; base-uri \'none\'; form-action \'none\'">',
        '<title>Escenarios propuestos</title></head><body><main>',
        '<h1>Escenarios propuestos</h1>',
        '<p>Las descripciones siguientes son datos propuestos; revise su '
        'significado antes de decidir. Esta vista no confirma decisiones.</p>',
    ]
    for question in packet['questions']:
        parts.extend(('<section><h2>Escenario booleano</h2><ul>',))
        for clause in question['scenario_clauses']:
            parts.extend(('<li><strong>', escape(clause['variable']),
                          ' = ', 'verdadero' if clause['value'] else 'falso',
                          '</strong>: ', escape(clause['proposed_phrase']),
                          ' (fuente propuesta: ', escape(clause['source_ref']),
                          ')</li>'))
        parts.extend(('</ul><p>', escape(QUESTION_TEXT), '</p></section>'))
    parts.append('</main></body></html>\n')
    return ''.join(parts)


def _unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError('DUPLICATE_JSON_KEY')
        result[name] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='bounded JSON gap_questions packet')
    args = parser.parse_args()
    try:
        path = Path(args.input).absolute()
        raw = read_regular(path.parent, path.name, MAX_INPUT_BYTES)
        preflight_json(raw, max_depth=32, max_bytes=MAX_INPUT_BYTES)
        packet = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                ValueError('NONFINITE_JSON_NUMBER')))
        document = render_document(packet)
    except MemoryError:
        print('INFRA_FAILURE', file=sys.stderr)
        return 3
    except (ValueError, OSError, UnicodeError, RecursionError):
        print('INVALID_INPUT', file=sys.stderr)
        return 2
    sys.stdout.write(document)
    return 0


if __name__ == '__main__':
    sys.exit(main())
