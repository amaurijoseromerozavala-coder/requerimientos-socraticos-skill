"""Bounded public-evidence redaction and pre-publication capability check.

This checks stored bytes, not whether a previously published value is still
valid. It never sends, executes, or prints the value it finds.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

MAX_INPUT = 16 * 1024 * 1024
REDACTED = b'[REDACTED]'
VALUE = rb'([A-Za-z0-9._~+/=-]{8,256})'
END = rb'(?=$|[\s",}\]]|\\+["\\])'
CLI_NAME = rb'--(?:token|api-key|secret|password)\b'
CLI_MARKER = re.compile(CLI_NAME, re.I)
CLI_VALUE = re.compile(CLI_NAME + rb'(?:=|[ \t]+)' + VALUE + END, re.I)
CLI_REDACTED = re.compile(CLI_NAME + rb'(?:=|[ \t]+)\[REDACTED\]' + END, re.I)
TEXT_NAME = rb'\b(?:access[_-]?token|api[_-]?key|secret|password)\s*[:=]'
TEXT_MARKER = re.compile(TEXT_NAME, re.I)
TEXT_KEY_VALUE = re.compile(TEXT_NAME + rb'[ \t]*' + VALUE + END, re.I)
TEXT_REDACTED = re.compile(TEXT_NAME + rb'[ \t]*\[REDACTED\]' + END, re.I)
SENSITIVE_KEYS = {'token', 'access_token', 'api_key', 'secret', 'password'}
JSON_STRING = re.compile(rb'"(?:\\.|[^"\\])*"')
REVIEW_ARGUMENT_NAMES = {
    'agent', 'base-ref', 'consent', 'contract', 'cwd', 'execute',
    'expected-revision', 'expected-untracked-inventory', 'intended-untracked',
    'lens', 'lenses', 'lenses-reason', 'lineage', 'next-transition', 'order',
    'projection', 'repository-context', 'request-context', 'request-hash',
    'subject-hash', 'target', 'target-evidence', 'untracked-scope',
    'workspace-overlay',
}

class _ObjectPairs(list):
    """Preserve duplicate JSON members until every value has been inspected."""


def _json_candidates(node):
    found = set()
    if isinstance(node, _ObjectPairs):
        names = [value for key, value in node if key == 'name' and isinstance(value, str)]
        argument_name = names[0] if len(names) == 1 and sum(key == 'value' for key, _ in node) == 1 else None
        named_secret = any(key == 'name' and isinstance(value, str)
                           and value.lower().replace('-', '_') in SENSITIVE_KEYS
                           for key, value in node)
        for key, value in node:
            normalized = str(key).lower().replace('-', '_')
            if (normalized == 'token' and argument_name in REVIEW_ARGUMENT_NAMES
                    and isinstance(value, str)
                    and (value == '--' + argument_name
                         or value.startswith('--' + argument_name + '='))):
                pass  # Recognized argument metadata; CLI_MARKER checks sensitive options.
            elif normalized in SENSITIVE_KEYS or (normalized == 'value' and named_secret):
                if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9._~+/=-]{8,256}', value):
                    found.add(value.encode())
                elif value != REDACTED.decode():
                    raise ValueError('AMBIGUOUS_EVIDENCE_VALUE')
            found.update(_json_candidates(value))
    elif isinstance(node, list):
        for value in node:
            found.update(_json_candidates(value))
    return found


def exposed_values(raw, *, suffix):
    """Return sensitive literals internally; callers must not print this set."""
    if len(raw) > MAX_INPUT or b'\x00' in raw:
        raise ValueError('UNSUPPORTED_EVIDENCE_BYTES')
    cli_matches = list(CLI_VALUE.finditer(raw))
    if len(list(CLI_MARKER.finditer(raw))) != len(cli_matches) + len(list(CLI_REDACTED.finditer(raw))):
        raise ValueError('AMBIGUOUS_EVIDENCE_MARKER')
    text_matches = list(TEXT_KEY_VALUE.finditer(raw))
    if len(list(TEXT_MARKER.finditer(raw))) != len(text_matches) + len(list(TEXT_REDACTED.finditer(raw))):
        raise ValueError('AMBIGUOUS_EVIDENCE_MARKER')
    result = {match.group(1) for match in cli_matches} | {match.group(1) for match in text_matches}
    if suffix.lower() == '.json':
        try:
            doc = json.loads(raw.decode('utf-8'), object_pairs_hook=_ObjectPairs)
            result.update(_json_candidates(doc))
        except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
            if result or b'\\u' in raw.lower() or re.search(
                    rb'"(?:token|access[-_]token|api[-_]key|secret|password)"\s*:', raw, re.I) or re.search(
                    rb'"name"\s*:\s*"(?:token|access[-_]token|api[-_]key|secret|password)"', raw, re.I):
                raise ValueError('INVALID_EVIDENCE_JSON') from error
    return {value for value in result if value != REDACTED}


def sanitize_bytes(raw, *, suffix):
    values = exposed_values(raw, suffix=suffix)
    output = raw
    if suffix.lower() == '.json' and values and b'\\' in output:
        decoded_values = [value.decode('ascii') for value in sorted(values, key=lambda item: (-len(item), item))]

        def redact_escaped_string(match):
            encoded = match.group()
            if b'\\' not in encoded:
                return encoded
            decoded = json.loads(encoded.decode('utf-8'))
            replaced = decoded
            for value in decoded_values:
                replaced = replaced.replace(value, REDACTED.decode())
            if replaced == decoded:
                return encoded
            return json.dumps(replaced, ensure_ascii=False).encode('utf-8')

        output = JSON_STRING.sub(redact_escaped_string, output)
    for value in sorted(values, key=lambda item: (-len(item), item)):
        output = output.replace(value, REDACTED)
    if len(output) > MAX_INPUT:
        raise ValueError('REDACTION_SIZE_LIMIT')
    if exposed_values(output, suffix=suffix):
        raise ValueError('REDACTION_INCOMPLETE')
    return output


def check_tree():
    names = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z']).split(b'\0')
    checked = 0
    flagged = 0
    errors = 0
    for entry in names:
        if not entry:
            continue
        path = Path(entry.decode('utf-8'))
        if path.parts[:2] != ('docs', 'skill-audit') and path.parts[:1] != ('exports',):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        if path.stat().st_size > MAX_INPUT:
            errors += 1
            continue
        try:
            flagged += bool(exposed_values(path.read_bytes(), suffix=path.suffix))
            checked += 1
        except ValueError:
            errors += 1
    print(f'EVIDENCE_CHECK checked={checked} flagged={flagged} unknown={errors}')
    return 0 if flagged == errors == 0 else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('check',))
    args = parser.parse_args()
    sys.exit(check_tree())
