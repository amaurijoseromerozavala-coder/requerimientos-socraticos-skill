"""Bounded, caller-owned source identity for local provider proposals.

This value records exact caller-supplied text and reference. It does not
authenticate the caller, a human, or the origin of either string.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceSnapshot:
    source_ref: str
    source_text: str

    def __post_init__(self):
        for value, limit in ((self.source_ref, 256), (self.source_text, 4096)):
            if type(value) is not str or not value.strip():
                raise ValueError('INVALID_CALLER_SOURCE')
            try:
                size = len(value.encode('utf-8'))
            except UnicodeError as error:
                raise ValueError('INVALID_CALLER_SOURCE') from error
            if size > limit:
                raise ValueError('CALLER_SOURCE_SIZE_LIMIT')
