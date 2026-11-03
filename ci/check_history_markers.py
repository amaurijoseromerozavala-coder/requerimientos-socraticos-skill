"""Reject unredacted review authorization markers in reachable Git blobs.

This bounded gate reports only counts. It does not assess whether any prior
authorization was usable or whether external copies still exist.
"""
from pathlib import Path
import re
import subprocess
import sys

MARKER = re.compile(rb'--token=[0-9a-fA-F]{64}(?![0-9a-fA-F])')
MAX_BLOBS = 5000
MAX_BLOB_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024


def _git(root, *args, input=None):
    return subprocess.run(['git', *args], cwd=root, input=input,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=True, timeout=20).stdout


def scan_history(root):
    checked = flagged = unknown = 0
    try:
        root = Path(root)
        objects = [row.split(b' ', 1)[0] for row in
                   _git(root, 'rev-list', '--objects', 'HEAD').splitlines()]
        if len(objects) > MAX_BLOBS * 3:
            raise ValueError('OBJECT_COUNT_LIMIT')
        metadata = _git(root, 'cat-file',
                        '--batch-check=%(objectname) %(objecttype) %(objectsize)',
                        input=b'\n'.join(objects) + b'\n').splitlines()
        if len(metadata) != len(objects):
            raise ValueError('OBJECT_METADATA_MISMATCH')
        total = 0
        for row in metadata:
            oid, kind, size = row.split()
            if kind != b'blob':
                continue
            checked += 1
            length = int(size)
            total += length
            if checked > MAX_BLOBS or length > MAX_BLOB_BYTES or total > MAX_TOTAL_BYTES:
                raise ValueError('HISTORY_SCAN_LIMIT')
            data = _git(root, 'cat-file', 'blob', oid.decode('ascii'))
            if len(data) != length:
                raise ValueError('BLOB_LENGTH_MISMATCH')
            flagged += bool(MARKER.search(data))
    except (OSError, ValueError, UnicodeError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired):
        unknown = 1
    print(f'HISTORY_MARKER_GATE checked={checked} flagged={flagged} unknown={unknown}')
    return 0 if flagged == unknown == 0 else 2


if __name__ == '__main__':
    sys.exit(scan_history(Path.cwd()))
