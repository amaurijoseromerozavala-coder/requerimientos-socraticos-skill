"""Tiny source-text oracle for synthetic Boolean clauses, not a general parser.

Only an exact match to one of four Spanish patterns can support compilation.
Any other wording remains inconclusive. This checks correspondence between a
source clause and a *proposal*; it cannot authenticate human intent.
"""

import re


_NAME = r'[A-Za-z][A-Za-z0-9_]{0,63}'
_LEFT = rf'(?P<left>{_NAME})'
_RIGHT = rf'(?P<right>{_NAME})'
_PATTERNS = (
    (re.compile(rf'{_LEFT} si y solo si {_RIGHT}', re.IGNORECASE),
     'EQUIVALENCE', 'BICONDITIONAL'),
    (re.compile(rf'{_LEFT} solo si {_RIGHT}', re.IGNORECASE),
     'NECESSARY_CONDITION', 'SUBJECT_IMPLIES_CONDITION'),
    (re.compile(rf'{_LEFT} si {_RIGHT}', re.IGNORECASE),
     'SUFFICIENT_CONDITION', 'CONDITION_IMPLIES_SUBJECT'),
    (re.compile(rf'Si {_RIGHT}, entonces {_LEFT}', re.IGNORECASE),
     'SUFFICIENT_CONDITION', 'CONDITION_IMPLIES_SUBJECT'),
)
_RESERVED = frozenset({'si', 'solo', 'y', 'no', 'entonces'})
_NEGATION = re.compile(r'\bno\b', re.IGNORECASE)


def assess(source, proposal):
    """Return a closed status; never infer missing meaning from model output."""
    if _NEGATION.search(source):
        return 'UNSUPPORTED_NEGATION'
    for pattern, kind, direction in _PATTERNS:
        match = pattern.fullmatch(source.strip())
        if match is None:
            continue
        left, right = match.group('left'), match.group('right')
        if left.lower() in _RESERVED or right.lower() in _RESERVED:
            return 'OUTSIDE_MINI_GRAMMAR'
        if (proposal['subject'], proposal['condition'], proposal['kind'],
                proposal['direction']) == (left, right, kind, direction):
            return 'MATCHED_MINI_GRAMMAR'
        return 'CONTRADICTORY_PROPOSAL'
    return 'OUTSIDE_MINI_GRAMMAR'
