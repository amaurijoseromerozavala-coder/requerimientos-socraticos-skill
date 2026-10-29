"""Bounded local transport for verified documentation bytes, never executable code.

Frame: 4-byte magic, 4-byte big-endian JSON header length, header, raw blobs.
No files are created. Both endpoints are installed, trusted local components.
"""
import hashlib
import json
from pathlib import PurePosixPath
import re
from json_preflight import preflight_json

MAGIC = b'RGB1'
MAX_HEADER = 2 * 1024 * 1024
MAX_FILE = 8 * 1024 * 1024
MAX_TOTAL = 32 * 1024 * 1024
MAX_ENTRIES = 4096


def canonical_path(name):
    if not isinstance(name, str) or not name or '\\' in name or '\0' in name:
        raise ValueError('UNSAFE_TREE_PATH')
    path = PurePosixPath(name)
    if path.is_absolute() or str(path) != name or any(x in ('.', '..', '.git') for x in path.parts) or len(path.parts) > 64:
        raise ValueError('UNSAFE_TREE_PATH')
    return name


def blob_oid(raw):
    return hashlib.sha256(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def _metadata(header):
    if not isinstance(header, dict) or set(header) != {'version', 'prd', 'files'} or type(header['version']) is not int or header['version'] != 1:
        raise ValueError('INVALID_BUNDLE_HEADER')
    canonical_path(header['prd'])
    rows = header['files']
    if not isinstance(rows, list) or len(rows) > MAX_ENTRIES:
        raise ValueError('ENTRY_LIMIT')
    seen = set()
    total = 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'path', 'oid', 'size'}:
            raise ValueError('INVALID_BUNDLE_HEADER')
        name = canonical_path(row['path'])
        if name in seen:
            raise ValueError('DUPLICATE_BUNDLE_PATH')
        seen.add(name)
        if not isinstance(row['oid'], str) or not re.fullmatch('[0-9a-f]{64}', row['oid']):
            raise ValueError('SHA256_REQUIRED')
        if type(row['size']) is not int or not 0 <= row['size'] <= MAX_FILE:
            raise ValueError('FILE_SIZE_LIMIT')
        total += row['size']
        if total > MAX_TOTAL:
            raise ValueError('BYTE_LIMIT')
    if header['prd'] not in seen:
        raise ValueError('PRD_MISSING')
    return rows


def encode_bundle(prd, files, oids):
    if set(files) != set(oids):
        raise ValueError('BLOB_OID_MISSING')
    rows = []
    for name in sorted(files):
        raw = files[name]
        if type(raw) is not bytes:
            raise ValueError('BUNDLE_BYTES_REQUIRED')
        rows.append({'path': name, 'oid': oids[name], 'size': len(raw)})
    header = {'version': 1, 'prd': prd, 'files': rows}
    _metadata(header)
    for name, raw in files.items():
        if blob_oid(raw) != oids[name]:
            raise ValueError('BLOB_OID_MISMATCH')
    raw_header = json.dumps(header, ensure_ascii=True, separators=(',', ':')).encode()
    if len(raw_header) > MAX_HEADER:
        raise ValueError('BUNDLE_HEADER_LIMIT')
    return b''.join([MAGIC, len(raw_header).to_bytes(4, 'big'), raw_header] + [files[row['path']] for row in rows])


def _exact(stream, size):
    chunks = []
    remaining = size
    while remaining:
        chunk = stream.read(min(65536, remaining))
        if not chunk:
            raise ValueError('TRUNCATED_BUNDLE')
        chunks.append(chunk)
        remaining -= len(chunk)
    return b''.join(chunks)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('DUPLICATE_BUNDLE_KEY')
        result[key] = value
    return result


def read_bundle(stream):
    if _exact(stream, 4) != MAGIC:
        raise ValueError('INVALID_BUNDLE_MAGIC')
    size = int.from_bytes(_exact(stream, 4), 'big')
    if not 0 < size <= MAX_HEADER:
        raise ValueError('BUNDLE_HEADER_LIMIT')
    raw = _exact(stream, size)
    preflight_json(raw, max_bytes=MAX_HEADER)
    header = json.loads(raw, object_pairs_hook=_unique_pairs)
    rows = _metadata(header)
    files, oids = {}, {}
    for row in rows:
        data = _exact(stream, row['size'])
        if blob_oid(data) != row['oid']:
            raise ValueError('BLOB_OID_MISMATCH')
        files[row['path']], oids[row['path']] = data, row['oid']
    if stream.read(1):
        raise ValueError('TRAILING_BUNDLE_DATA')
    return header['prd'], files, oids
