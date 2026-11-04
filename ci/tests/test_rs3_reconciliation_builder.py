"""Source-bound builder checks; package-dependent test is explicit NOT_RUN in CI."""

import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from ci import build_rs3_reconciliation as builder


ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / 'docs/design/rs3/reconciliation-2026-11-03.json'
AUDITED_HEAD = '40328757dcf7f6b758f8f09df845224f1b656572'


class BuilderOracleTests(unittest.TestCase):
    def test_rejects_changed_source_identity_before_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / 'changed.zip'
            package.write_bytes(b'synthetic changed archive; no credential')
            with self.assertRaisesRegex(ValueError, '^PACKAGE_IDENTITY_MISMATCH$'):
                builder.build(package, AUDITED_HEAD)

    def test_identified_source_reproduces_versioned_matrix(self):
        source = os.environ.get('RS3_PROPOSAL_PACKAGE')
        if not source:
            self.skipTest('NOT_RUN: identified external RS3 package unavailable')
        package = Path(source)
        self.assertEqual(hashlib.sha256(package.read_bytes()).hexdigest(),
                         builder.ZIP_SHA256)
        actual = builder.render(builder.build(package, AUDITED_HEAD))
        self.assertEqual(actual.encode('utf-8'), MATRIX.read_bytes())


if __name__ == '__main__':
    unittest.main()
