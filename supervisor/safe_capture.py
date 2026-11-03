"""Bounded redaction for bytes owned by the local durable capture journal.

Ambiguous sensitive markers reject the capture. This does not control files
written independently by child processes or external review tools.
"""
import json
import re

_VALUE = rb'[A-Za-z0-9._~+/=-]{8,256}'
_CLI = re.compile(rb'--token(?:=|[ \t]+)(' + _VALUE + rb')(?=$|[\s",}\]])', re.I)
_MARKER = re.compile(rb'--token\b', re.I)
_JSON_KEY = re.compile(rb'"(?:token|access[-_]token|api[-_]key|secret|password)"\s*:', re.I)
_JSON_STRING = re.compile(rb'"(?:\\.|[^"\\])*"')
_KEYS = {'token', 'access_token', 'api_key', 'secret', 'password'}
_REDACTED = b'[REDACTED]'


class _ObjectPairs(list):
    """Keep every JSON member until sensitive values have been collected."""


def _collect(raw):
    if _JSON_KEY.search(raw) and not raw.lstrip().startswith((b'{', b'[')):
        raise ValueError('UNSCOPED_JSON_SECRET_MARKER')
    matches = list(_CLI.finditer(raw))
    if len(matches) != len(list(_MARKER.finditer(raw))):
        raise ValueError('AMBIGUOUS_CAPTURE_MARKER')
    values = {match.group(1) for match in matches}
    document = None
    if raw.lstrip().startswith((b'{', b'[')):
        try:
            document = json.loads(raw.decode('utf-8'), object_pairs_hook=_ObjectPairs)
        except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
            lowered = raw.lower()
            if values or b'\\u' in lowered or _JSON_KEY.search(raw):
                raise ValueError('INVALID_CAPTURE_STRUCTURE') from error
            return values, None
        try:
            pending = [(document, 0)]
            visited = 0
            while pending:
                item, depth = pending.pop()
                visited += 1
                if visited > 8192 or depth > 32:
                    raise ValueError('CAPTURE_STRUCTURE_LIMIT')
                if isinstance(item, _ObjectPairs):
                    named_secret = any(
                        key == 'name' and isinstance(value, str)
                        and value.lower().replace('-', '_') in _KEYS
                        for key, value in item)
                    for key, value in item:
                        normalized = str(key).lower().replace('-', '_')
                        if normalized in _KEYS or (normalized == 'value' and named_secret):
                            if not isinstance(value, str) or not re.fullmatch(_VALUE, value.encode('utf-8')):
                                raise ValueError('AMBIGUOUS_CAPTURE_VALUE')
                            values.add(value.encode('utf-8'))
                        pending.append((value, depth + 1))
                elif isinstance(item, list):
                    pending.extend((value, depth + 1) for value in item)
                elif isinstance(item, str):
                    encoded = item.encode('utf-8')
                    decoded_matches = list(_CLI.finditer(encoded))
                    if len(decoded_matches) != len(list(_MARKER.finditer(encoded))):
                        raise ValueError('AMBIGUOUS_CAPTURE_MARKER')
                    values.update(match.group(1) for match in decoded_matches)
        except (UnicodeError, RecursionError) as error:
            raise ValueError('INVALID_CAPTURE_STRUCTURE') from error
    return values, document


def redact_pair(stdout, stderr):
    if not isinstance(stdout, bytes) or not isinstance(stderr, bytes):
        raise ValueError('CAPTURE_BYTES_REQUIRED')
    first, first_doc = _collect(stdout)
    second, second_doc = _collect(stderr)
    values = first | second
    if not values:
        return stdout, stderr
    strings = [value.decode('ascii') for value in sorted(values, key=lambda item: (-len(item), item))]

    def replace_text(value):
        for sensitive in strings:
            value = value.replace(sensitive, '[REDACTED]')
        return value

    result = []
    for stream, document in ((stdout, first_doc), (stderr, second_doc)):
        if document is not None:
            parts = []
            end = 0
            for match in _JSON_STRING.finditer(stream):
                original = match.group()
                decoded = json.loads(original.decode('utf-8'))
                replacement = replace_text(decoded)
                if replacement != decoded:
                    parts.extend((stream[end:match.start()],
                                  json.dumps(replacement, ensure_ascii=False).encode('utf-8')))
                    end = match.end()
            if parts:
                parts.append(stream[end:])
                stream = b''.join(parts)
        else:
            for value in sorted(values, key=lambda item: (-len(item), item)):
                stream = stream.replace(value, _REDACTED)
        result.append(stream)
    if any(value in stream for value in values for stream in result):
        raise ValueError('UNREDACTED_CAPTURE_VALUE')
    return tuple(result)
