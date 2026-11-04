"""Synthetic adversarial corpus for the weak-model proposal admission gate."""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from weak_model_gate import admit_response


def base_proposal():
    return {'schema_version': '0.1-proposed', 'id': 'RS3-WEAK-1',
            'source_ref': 'synthetic/weak-model/1',
            'source_text': 'P solo si Q', 'status': 'PROPOSED',
            'kind': 'NECESSARY_CONDITION', 'modality': 'MUST',
            'subject': 'P', 'condition': 'Q',
            'direction': 'SUBJECT_IMPLIES_CONDITION',
            'assumptions': [], 'exceptions': [], 'human_confirmation': 'PENDING'}


class WeakModelGateTests(unittest.TestCase):
    def test_versioned_synthetic_corpus_is_fail_closed(self):
        corpus = json.loads((ROOT / 'assets/rs3-weak-model-cases.json').read_text())
        self.assertEqual(corpus['schema'], 'rs3-weak-model-cases/v1')
        self.assertEqual(corpus['scope'], 'SYNTHETIC_LOCAL_NO_PROVIDER')
        self.assertEqual(len(corpus['cases']), 14)
        for case in corpus['cases']:
            with self.subTest(case=case['id']):
                if 'raw' in case:
                    raw = case['raw'].encode('utf-8')
                else:
                    item = base_proposal()
                    item.update(case['overrides'])
                    raw = json.dumps(item, ensure_ascii=False).encode('utf-8')
                result = admit_response(raw)
                self.assertEqual(result['admission'], case['expected'])
                self.assertEqual(result['authority_verification'], 'NOT_ESTABLISHED')
                self.assertIs(result['execution_authorized'], False)
                self.assertNotIn('source_text', result)
                if case['expected'] != 'PROPOSED_FOR_REVIEW':
                    self.assertIsNone(result['ast'])

    def test_oversize_depth_invalid_utf8_and_duplicate_key_reject(self):
        base = json.dumps(base_proposal(), separators=(',', ':')).encode('utf-8')
        duplicate = base[:-1] + b',"status":"PROPOSED"}'
        inputs = ((b' ' * 16385, 'JSON_SIZE_LIMIT'),
                  (b'[' * 9 + b'0' + b']' * 9, 'JSON_DEPTH_LIMIT'),
                  (b'\xff', 'INVALID_UTF8'),
                  (duplicate, 'DUPLICATE_JSON_KEY'))
        for raw, reason in inputs:
            with self.subTest(reason=reason):
                result = admit_response(raw)
                self.assertEqual(result['admission'], 'REJECT_INPUT')
                self.assertEqual(result['reason_code'], reason)
                self.assertIsNone(result['ast'])

    def test_resource_failure_cannot_become_proposal(self):
        with patch('weak_model_gate.preflight_json', side_effect=MemoryError):
            result = admit_response(b'{}')
        self.assertEqual(result['admission'], 'INFRA_FAILURE')
        self.assertIsNone(result['ast'])
        self.assertIs(result['execution_authorized'], False)

    def test_missing_provider_payload_is_rejected_without_inference(self):
        result = admit_response(None)
        self.assertEqual(result['admission'], 'REJECT_INPUT')
        self.assertEqual(result['reason_code'], 'BYTES_REQUIRED')
        self.assertIsNone(result['ast'])


if __name__ == '__main__':
    unittest.main()
