#!/usr/bin/env python3
"""Build a bounded, non-authoritative interrogation record on stdout."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from json_preflight import preflight_json
from render_gap_questions import (_unique_object, _validate, HEX64,
                                  MAX_INPUT_BYTES)
from safe_io import read_regular


MAX_RESPONSE_BYTES = 8192
HANDOFF_KEYS = {'schema_version', 'status', 'authority',
                'source_authenticity', 'question_count', 'question_index',
                'question_sha256', 'model_sha256', 'glossary_sha256', 'question'}
HISTORY_KEYS = {'schema_version', 'state', 'authority_verification',
                'execution_authorized', 'events'}
QUESTION_KEYS = {'text', 'text_origin', 'scenario_clauses',
                 'scenario_clauses_origin', 'input_assignment', 'sources',
                 'model_sha256', 'semantic_status'}
SOURCE_KEYS = {'source_ref', 'source_text', 'source_sha256'}


def validate_handoff(handoff):
    """Check structure and self-consistency, never human or source authenticity."""
    if (type(handoff) is not dict or set(handoff) != HANDOFF_KEYS
            or handoff['schema_version'] != 'rs3-question-handoff/v1'
            or handoff['status'] != 'PROPOSED_FOR_INTERROGATION'
            or handoff['authority'] != 'NOT_GRANTED'
            or handoff['source_authenticity'] != 'NOT_ESTABLISHED'
            or type(handoff['question_count']) is not int
            or not 1 <= handoff['question_count'] <= 16
            or type(handoff['question_index']) is not int
            or handoff['question_index'] != 0
            or type(handoff['model_sha256']) is not str
            or not HEX64.fullmatch(handoff['model_sha256'])
            or type(handoff['glossary_sha256']) is not str
            or not HEX64.fullmatch(handoff['glossary_sha256'])
            or type(handoff['question_sha256']) is not str
            or not HEX64.fullmatch(handoff['question_sha256'])):
        raise ValueError('INVALID_HANDOFF')
    question = handoff['question']
    if (type(question) is not dict or set(question) != QUESTION_KEYS
            or type(question['sources']) is not dict
            or any(type(source) is not dict or set(source) != SOURCE_KEYS
                   for source in question['sources'].values())):
        raise ValueError('INVALID_HANDOFF_FIELDS')
    _validate({'status': 'PROPOSED_UNVERIFIED', 'authority': 'NOT_GRANTED',
               'source_authenticity': 'NOT_ESTABLISHED', 'questions': [question]})
    if question['model_sha256'] != handoff['model_sha256']:
        raise ValueError('HANDOFF_MODEL_MISMATCH')
    binding = {name: handoff[name] for name in
               ('model_sha256', 'glossary_sha256', 'question')}
    canonical = json.dumps(binding, ensure_ascii=False, sort_keys=True,
                           separators=(',', ':'), allow_nan=False).encode('utf-8')
    expected = hashlib.sha256(b'rs3-question-handoff/v1\n' + canonical).hexdigest()
    if handoff['question_sha256'] != expected:
        raise ValueError('HANDOFF_IDENTITY_MISMATCH')


def start(handoff):
    validate_handoff(handoff)
    return {'schema_version': 'rs3-interrogation-history/v1',
            'state': 'WAITING_USER', 'authority_verification': 'NOT_ESTABLISHED',
            'execution_authorized': False,
            'events': [{'kind': 'QUESTION_PROPOSED',
                        'question_sha256': handoff['question_sha256'],
                        'handoff': handoff}]}


def respond(history, text):
    """Keep literal relayed text for review, with no authority transition."""
    if (type(history) is not dict or set(history) != HISTORY_KEYS
            or history['schema_version'] != 'rs3-interrogation-history/v1'
            or history['state'] != 'WAITING_USER'
            or history['authority_verification'] != 'NOT_ESTABLISHED'
            or history['execution_authorized'] is not False
            or type(history['events']) is not list
            or len(history['events']) != 1):
        raise ValueError('INVALID_HISTORY_STATE')
    event = history['events'][0]
    if (type(event) is not dict or set(event) != {
            'kind', 'question_sha256', 'handoff'}
            or event['kind'] != 'QUESTION_PROPOSED'):
        raise ValueError('INVALID_QUESTION_EVENT')
    validate_handoff(event['handoff'])
    if event['question_sha256'] != event['handoff']['question_sha256']:
        raise ValueError('QUESTION_EVENT_MISMATCH')
    if (type(text) is not str or not text.strip()
            or len(text.encode('utf-8')) > MAX_RESPONSE_BYTES
            or any(ord(char) < 32 and char not in '\n\t\r' for char in text)):
        raise ValueError('INVALID_RESPONSE_TEXT')
    return {**history, 'state': 'INTERPRETATION_REVIEW',
            'events': [event, {'kind': 'RESPONSE_RECEIVED',
                               'question_sha256': event['question_sha256'],
                               'origin': 'UNVERIFIED_RELAY', 'text': text}]}


def _read_json(path):
    if path == '-':
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    else:
        target = Path(path).absolute()
        raw = read_regular(target.parent, target.name, MAX_INPUT_BYTES)
    preflight_json(raw, max_depth=32, max_bytes=MAX_INPUT_BYTES)
    return json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(
                          ValueError('NONFINITE_JSON_NUMBER')))


def _read_response(path):
    if path == '-':
        raw = sys.stdin.buffer.read(MAX_RESPONSE_BYTES + 1)
    else:
        target = Path(path).absolute()
        raw = read_regular(target.parent, target.name, MAX_RESPONSE_BYTES)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError('RESPONSE_SIZE_LIMIT')
    return raw.decode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='mode', required=True)
    modes.add_parser('start').add_argument('handoff')
    response = modes.add_parser('respond')
    response.add_argument('history')
    response.add_argument('--response-file', required=True)
    args = parser.parse_args()
    try:
        if args.mode == 'start':
            record = start(_read_json(args.handoff))
        else:
            if args.history == '-' and args.response_file == '-':
                raise ValueError('AMBIGUOUS_STDIN')
            record = respond(_read_json(args.history),
                             _read_response(args.response_file))
        output = json.dumps(record, ensure_ascii=False, sort_keys=True,
                            separators=(',', ':'), allow_nan=False)
    except (ValueError, OSError, UnicodeError, RecursionError):
        print('INVALID_INPUT', file=sys.stderr)
        return 2
    except MemoryError:
        print('INFRA_FAILURE', file=sys.stderr)
        return 3
    sys.stdout.write(output + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
