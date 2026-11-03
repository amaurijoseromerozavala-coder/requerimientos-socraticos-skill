"""Select a Git comparison base for the one known history replacement."""
import argparse
from pathlib import Path
import re
import subprocess
import sys

ORIGINAL_BEFORE = '2363631f9c70727f3136e0491c776b3f5b467070'
REWRITTEN_BASE = 'e168f775744102aa708baf5618aa6efd37f39dd6'


def select_base(root, before, forced, *, previous=ORIGINAL_BEFORE,
                rewritten=REWRITTEN_BASE):
    if not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', before):
        raise ValueError('INVALID_BEFORE')
    if forced not in ('true', 'false'):
        raise ValueError('INVALID_FORCED_FLAG')
    if forced == 'true' and before == previous:
        result = subprocess.run(
            ['git', 'merge-base', '--is-ancestor', rewritten, 'HEAD'],
            cwd=Path(root), stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=5)
        if result.returncode != 0:
            raise ValueError('REWRITTEN_BASE_NOT_ANCESTOR')
        return rewritten
    return before


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', required=True)
    parser.add_argument('--forced', required=True)
    args = parser.parse_args()
    try:
        print(select_base(Path.cwd(), args.before, args.forced))
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print('BASE_SELECTION_BLOCKED', file=sys.stderr)
        sys.exit(2)
