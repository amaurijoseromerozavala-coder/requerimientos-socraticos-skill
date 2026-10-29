"""Small transport fixtures; no candidate files are executed or materialized."""
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from git_bundle import encode_bundle, read_bundle, MAGIC


def oid(raw):
    return hashlib.sha256(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


class BundleTests(unittest.TestCase):
    def test_binary_round_trip_and_nested_path(self):
        files = {'docs/prd.json': b'{}', 'docs/raw.txt': b'\0\xff\r\n'}
        oids = {p: oid(v) for p, v in files.items()}
        payload = encode_bundle('docs/prd.json', files, oids)
        prd, actual, hashes = read_bundle(io.BytesIO(payload))
        self.assertEqual(prd, 'docs/prd.json')
        self.assertEqual(actual, files)
        self.assertEqual(hashes, oids)

    def test_changed_blob_bytes_rejected(self):
        payload = encode_bundle('prd.json', {'prd.json': b'{}'}, {'prd.json': oid(b'{}')})
        with self.assertRaisesRegex(ValueError, 'BLOB_OID_MISMATCH'):
            read_bundle(io.BytesIO(payload[:-1] + b'x'))

    def test_truncation_and_trailing_data_rejected(self):
        payload = encode_bundle('prd.json', {'prd.json': b'{}'}, {'prd.json': oid(b'{}')})
        for bad in [payload[:-1], payload + b'x']:
            with self.subTest(size=len(bad)), self.assertRaises(ValueError):
                read_bundle(io.BytesIO(bad))

    def test_unsafe_path_and_missing_prd_rejected(self):
        for prd in ['../prd.json', '/prd.json', 'a//prd.json', 'missing.json']:
            with self.subTest(prd=prd), self.assertRaises(ValueError):
                encode_bundle(prd, {'prd.json': b'{}'}, {'prd.json': oid(b'{}')})

    def test_invalid_metadata_rejected_before_body_read(self):
        row = {'path': 'prd.json', 'oid': oid(b'{}'), 'size': 8*1024*1024+1}
        for header in [
            {'version': 1, 'prd': 'prd.json', 'files': [row]},
            {'version': True, 'prd': 'prd.json', 'files': []},
            {'version': 1, 'prd': 'prd.json', 'files': [dict(row, size=0), dict(row, size=0)]},
        ]:
            raw = json.dumps(header).encode()
            with self.assertRaises(ValueError):
                read_bundle(io.BytesIO(MAGIC + len(raw).to_bytes(4, 'big') + raw))


if __name__ == '__main__':
    unittest.main()
