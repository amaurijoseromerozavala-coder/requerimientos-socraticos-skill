"""Negative controls for public review evidence; all values are synthetic."""
import json
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from ci.check_review_evidence import check_tree, sanitize_bytes, exposed_values


SAMPLE = 'a' * 64
SECOND_SAMPLE = 'b' * 64


class ReviewEvidenceTests(unittest.TestCase):
    def test_check_rejects_comparison_base_parameter(self):
        script = Path(__file__).resolve().parents[1] / 'check_review_evidence.py'
        with tempfile.TemporaryDirectory() as root:
            subprocess.run(['git', 'init', '-q', root], check=True, capture_output=True)
            result = subprocess.run(
                [sys.executable, str(script), 'check', '--base', 'not-a-commit'],
                cwd=root, capture_output=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(b'EVIDENCE_CHECK checked=0 flagged=0 unknown=0', result.stdout)

    def test_direct_token_key_is_redacted(self):
        data = {'token': SAMPLE, 'other': 'ordinary'}
        output = sanitize_bytes(json.dumps(data).encode(), suffix='.json')
        self.assertNotIn(SAMPLE.encode(), output)
        self.assertEqual(json.loads(output)['other'], 'ordinary')

    def test_hyphenated_sensitive_key_is_redacted(self):
        data = {'api-key': SAMPLE, 'other': 'ordinary'}
        output = sanitize_bytes(json.dumps(data).encode(), suffix='.json')
        self.assertNotIn(SAMPLE.encode(), output)
        self.assertEqual(json.loads(output)['other'], 'ordinary')

    def test_duplicate_sensitive_keys_are_all_redacted(self):
        raw = ('{"token":"' + SAMPLE + '","token":"' + SECOND_SAMPLE + '"}').encode()
        output = sanitize_bytes(raw, suffix='.json')
        self.assertNotIn(SAMPLE.encode(), output)
        self.assertNotIn(SECOND_SAMPLE.encode(), output)

    def test_independent_token_key_with_dash_prefix_is_redacted(self):
        raw = b'{"token":"--abcdefgh","token":"ijklmnop5678"}'
        output = sanitize_bytes(raw, suffix='.json')
        self.assertNotIn(b'--abcdefgh', output)
        self.assertNotIn(b'ijklmnop5678', output)

    def test_structured_nonsecret_argument_token_is_preserved(self):
        raw = json.dumps({'name': 'target', 'value': 'sha256:' + SAMPLE,
                          'token': '--target=sha256:' + SAMPLE}).encode()
        self.assertEqual(sanitize_bytes(raw, suffix='.json'), raw)

    def test_ambiguous_cli_value_is_rejected(self):
        with self.assertRaises(ValueError):
            sanitize_bytes(b'run --token=abcdefgh@unknown', suffix='.md')

    def test_tree_check_scopes_public_evidence_not_source_fixtures(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root, 'ci/tests/example.py')
            source.parent.mkdir(parents=True)
            source.write_bytes(b'--token=abcdefgh@unknown')
            prior = os.getcwd()
            try:
                os.chdir(root)
                with patch('ci.check_review_evidence.subprocess.check_output',
                           return_value=b'ci/tests/example.py\0'):
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(check_tree(), 0)
            finally:
                os.chdir(prior)

    def test_nested_command_argument_and_duplicate_are_redacted(self):
        data = {'acknowledgement': {
            'command': 'gentle-ai review acknowledge-approved --token=' + SAMPLE,
            'arguments': [{'name': 'token', 'value': SAMPLE,
                           'token': '--token=' + SAMPLE}],
            'other': {'copied': SAMPLE}},
            'unrelated': 'preserve this'}
        output = sanitize_bytes(json.dumps(data).encode(), suffix='.json')
        parsed = json.loads(output)
        self.assertNotIn(SAMPLE.encode(), output)
        self.assertEqual(parsed['unrelated'], 'preserve this')
        self.assertEqual(parsed['acknowledgement']['other']['copied'], '[REDACTED]')
        self.assertFalse(exposed_values(output, suffix='.json'))

    def test_json_escaped_copy_of_sensitive_value_is_redacted(self):
        raw = b'{"token":"abcdefgh","copy":"\\u0061bcdefgh"}'
        output = sanitize_bytes(raw, suffix='.json')
        parsed = json.loads(output)
        self.assertEqual(parsed['token'], '[REDACTED]')
        self.assertEqual(parsed['copy'], '[REDACTED]')

    def test_escaped_command_marker_is_redacted(self):
        raw = ('{"command":"review \\u002d\\u002dtoken=' + SAMPLE + '","keep":7}').encode()
        output = sanitize_bytes(raw, suffix='.json')
        self.assertNotIn(SAMPLE.encode(), output)
        self.assertEqual(json.loads(output)['command'], 'review --token=[REDACTED]')

    def test_ambiguous_escaped_command_marker_is_rejected(self):
        raw = b'{"command":"review \\u002d\\u002dtoken=short"}'
        with self.assertRaises(ValueError):
            sanitize_bytes(raw, suffix='.json')

    def test_text_command_and_structured_secret(self):
        data = ('run --token ' + SAMPLE + '\n' +
                'access_token: ' + SAMPLE + '\n').encode()
        result = sanitize_bytes(data, suffix='.md')
        self.assertNotIn(SAMPLE.encode(), result)
        self.assertFalse(exposed_values(result, suffix='.md'))

    def test_invalid_json_is_rejected_without_output(self):
        with self.assertRaises(ValueError):
            sanitize_bytes(b'{"name":"token","value":"bad"', suffix='.json')

    def test_no_sensitive_value_preserves_bytes(self):
        raw = b'{"target":"sha256:' + (b'b' * 64) + b'"}\n'
        self.assertEqual(sanitize_bytes(raw, suffix='.json'), raw)


if __name__ == '__main__':
    unittest.main()
