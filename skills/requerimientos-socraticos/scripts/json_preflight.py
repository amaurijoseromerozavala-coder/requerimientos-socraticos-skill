"""Bound JSON structure before passing bytes to a JSON decoder.

This is deliberately not a JSON grammar or encoding validator. The caller must
still decode the input with its normal duplicate-key and constant policies.
"""


def preflight_json(raw, max_depth=96, max_bytes=262144):
    """Reject oversized or structurally unbalanced JSON bytes.

    Depth counts open objects and arrays; strings and their escapes are
    skipped. Raises ValueError on invalid limits or structural violations.
    """
    if not isinstance(raw, bytes):
        raise ValueError('raw must be bytes')
    if type(max_depth) is not int or max_depth < 1:
        raise ValueError('max_depth must be a positive integer')
    if type(max_bytes) is not int or max_bytes < 1:
        raise ValueError('max_bytes must be a positive integer')
    if len(raw) > max_bytes:
        raise ValueError('JSON exceeds maximum bytes')

    stack = []
    in_string = False
    escaped = False
    for byte in raw:
        if in_string:
            if escaped:
                escaped = False
            elif byte == 92:  # backslash
                escaped = True
            elif byte == 34:  # quote
                in_string = False
        elif byte == 34:
            in_string = True
        elif byte == 91 or byte == 123:  # [ or {
            if len(stack) >= max_depth:
                raise ValueError('JSON exceeds maximum depth')
            stack.append(byte)
        elif byte == 93 or byte == 125:  # ] or }
            expected = 91 if byte == 93 else 123
            if not stack or stack[-1] != expected:
                raise ValueError('JSON has unmatched or mismatched delimiter')
            stack.pop()
    if in_string:
        raise ValueError('JSON has an unterminated string')
    if stack:
        raise ValueError('JSON has unclosed delimiters')
