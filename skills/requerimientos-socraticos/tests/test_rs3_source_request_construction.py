"""Synthetic falsifiers for caller-source request construction."""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from local_provider_adapter import LocalProviderAdapter
from source_snapshot import SourceSnapshot


class SourceRequestConstructionTests(unittest.TestCase):
    def test_provider_receives_exact_snapshot_in_versioned_json(self):
        snapshot = SourceSnapshot('synthetic/human/1', 'P solo si Q')
        code = ('import json,sys;'
                'request=json.load(sys.stdin);'
                'assert request["schema_version"]=="rs3-source-request/1";'
                'item={"schema_version":"0.1-proposed","id":"RS3-SOURCE-1",'
                '"source_ref":request["source_ref"],'
                '"source_text":request["source_text"],'
                '"status":"PROPOSED","kind":"NECESSARY_CONDITION",'
                '"modality":"MUST","subject":"P","condition":"Q",'
                '"direction":"SUBJECT_IMPLIES_CONDITION",'
                '"assumptions":[],"exceptions":[],"human_confirmation":"PENDING"};'
                'sys.stdout.write(json.dumps(item))')
        adapter = LocalProviderAdapter((sys.executable, '-I', '-B', '-c', code),
                                       snapshot, timeout_seconds=.5)
        result = adapter.invoke()
        self.assertEqual(result['admission'], 'PROPOSED_FOR_REVIEW')
        self.assertEqual(result['source_binding'], 'MATCHED_CALLER_SNAPSHOT')
        self.assertIs(result['execution_authorized'], False)
        self.assertNotIn(snapshot.source_text, str(result))

    def test_no_alternate_request_bytes_channel(self):
        snapshot = SourceSnapshot('synthetic/human/1', 'P solo si Q')
        adapter = LocalProviderAdapter((sys.executable, '-I', '-B', '-c', 'pass'),
                                       snapshot)
        with self.assertRaises(TypeError):
            adapter.invoke(b'{"source_text":"P si Q"}')

    def test_serialized_request_limit_precedes_launch(self):
        snapshot = SourceSnapshot('synthetic/human/1', '\u0001' * 2000)
        adapter = LocalProviderAdapter((sys.executable, '-I', '-B', '-c', 'pass'),
                                       snapshot)
        with patch('local_provider_adapter.run_supervised') as run:
            result = adapter.invoke()
        self.assertEqual((result['admission'], result['reason_code']),
                         ('REJECT_INPUT', 'REQUEST_SIZE_LIMIT'))
        run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
