"""Negative controls for the journal-owned durable capture path."""
import json
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from supervisor.journal import Journal, JournalBlocked
from supervisor.process_core import Limits, ProcessSupervisor

SECRET = 'SYNTHETIC_SECRET_DO_NOT_USE_001'
IDENTITY = {'run_id': 'capture-test', 'boot_id': 'test-boot',
            'pid_namespace_identity': 'test-namespace', 'owner_uid': os.getuid(),
            'checker_manifest_digest': 'a' * 64, 'policy_digest': 'b' * 64}


class SafeCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='safe-capture-test-')
        self.root = Path(self.temp.name) / 'journal'
        Journal.initialize(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def terminal(self, journal):
        journal.reserve(IDENTITY)
        journal.record_active(123, 'start-123')
        journal.record_terminated(123, 'start-123')

    def captured(self, journal):
        row = journal.accounting()['runs'][0]
        slot = self.root / 'runs' / row['slot']
        return slot, (slot / 'stdout.bin').read_bytes(), (slot / 'stderr.bin').read_bytes(), json.loads((slot / 'receipt.json').read_text())

    def test_assignment_separated_and_cross_channel_copy(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            raw = b'ordinary --token=' + SECRET.encode() + b' end'
            retained = journal.store_capture(123, 'start-123', 0, raw,
                                             b'copy=' + SECRET.encode(), True)
            _, stdout, stderr, receipt = self.captured(journal)
            self.assertFalse(SECRET.encode() in stdout + stderr)
            self.assertFalse(SECRET.encode() in b''.join(retained))
            self.assertIn(b'ordinary', stdout)
            self.assertEqual(receipt['stdout_bytes'], len(stdout))
            self.assertEqual(receipt['stderr_bytes'], len(stderr))
            self.assertEqual(receipt['stdout_sha256'], hashlib.sha256(stdout).hexdigest())
            self.assertEqual(receipt['stderr_sha256'], hashlib.sha256(stderr).hexdigest())

    def test_separated_argument(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            journal.store_capture(123, 'start-123', 0,
                                  b'run --token ' + SECRET.encode(), b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertFalse(SECRET.encode() in stdout)

    def test_nested_json_and_stderr_are_sanitized_before_write(self):
        nested = {'command': 'tool --token=' + SECRET,
                  'arguments': [{'name': 'token', 'value': SECRET}],
                  'copy': {'value': SECRET}, 'ordinary': 'keep'}
        with Journal(self.root) as journal:
            self.terminal(journal)
            journal.store_capture(123, 'start-123', 0, json.dumps(nested).encode(),
                                  ('notice --token=' + SECRET).encode(), True)
            _, stdout, stderr, receipt = self.captured(journal)
            self.assertFalse(SECRET.encode() in stdout + stderr)
            self.assertEqual(json.loads(stdout)['ordinary'], 'keep')
            self.assertEqual(receipt['schema_version'], 'process-receipt/v1')

    def test_direct_json_key_and_ambiguous_marker_fail_closed(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            with self.assertRaises(JournalBlocked):
                journal.store_capture(123, 'start-123', 0, b'--token="unquoted"', b'', True)
            self.assertEqual(list((self.root / 'runs').iterdir()), [])
            journal.store_capture(123, 'start-123', 0,
                                  json.dumps({'token': SECRET, 'ordinary': 7}).encode(), b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertFalse(SECRET.encode() in stdout)
            self.assertEqual(json.loads(stdout)['ordinary'], 7)

    def test_escaped_json_value_and_escaped_copy_are_not_retained(self):
        escaped = SECRET.replace('S', '\\u0053', 1)
        raw = ('{"token":"' + escaped + '","copy":"' + escaped + '","keep":7}').encode()
        with Journal(self.root) as journal:
            self.terminal(journal)
            journal.store_capture(123, 'start-123', 0, raw, b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertFalse(SECRET.encode() in stdout)
            self.assertFalse(escaped.encode() in stdout)
            self.assertEqual(json.loads(stdout)['token'], '[REDACTED]')
            self.assertEqual(json.loads(stdout)['copy'], '[REDACTED]')
            self.assertEqual(json.loads(stdout)['keep'], 7)

    def test_escaped_json_command_marker_is_sanitized(self):
        raw = ('{"command":"\\u002d\\u002dtoken=' + SECRET + '","keep":7}').encode()
        with Journal(self.root) as journal:
            self.terminal(journal)
            journal.store_capture(123, 'start-123', 0, raw, b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertFalse(SECRET.encode() in stdout)
            self.assertEqual(json.loads(stdout)['keep'], 7)

    def test_redacted_expansion_above_limit_blocks_before_slot(self):
        short = b'SHORTVAL'
        with Journal(self.root) as journal:
            self.terminal(journal)
            raw = short * (262144 // len(short))
            with self.assertRaises(JournalBlocked):
                journal.store_capture(123, 'start-123', 0, raw,
                                      b'--token=' + short, True)
            self.assertEqual(list((self.root / 'runs').iterdir()), [])

    def test_unsupported_token_suffix_blocks_before_slot(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            with self.assertRaises(JournalBlocked):
                journal.store_capture(123, 'start-123', 0,
                                      b'--token=abcdefgh@remainder', b'', True)
            self.assertEqual(list((self.root / 'runs').iterdir()), [])

    def test_sanitizer_failure_has_no_capture_slot(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            with patch('supervisor.journal.redact_pair', side_effect=ValueError('controlled')):
                with self.assertRaises(JournalBlocked):
                    journal.store_capture(123, 'start-123', 0, b'--token=' + SECRET.encode(), b'', True)
            self.assertEqual(list((self.root / 'runs').iterdir()), [])
            self.assertEqual(journal.inspect()['state'], 'CONFIRMED_TERMINATED')

    def test_write_failure_leaves_only_sanitized_partial_bytes(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            original = os.open

            def fail_stderr(name, *args, **kwargs):
                if name == 'stderr.bin':
                    raise OSError('controlled write failure')
                return original(name, *args, **kwargs)

            with patch('supervisor.journal.os.open', side_effect=fail_stderr):
                with self.assertRaises(OSError):
                    journal.store_capture(123, 'start-123', 0,
                                          b'--token=' + SECRET.encode(), b'ordinary', True)
            slot = next((self.root / 'runs').iterdir())
            self.assertFalse(SECRET.encode() in (slot / 'stdout.bin').read_bytes())
            self.assertEqual(journal.inspect()['state'], 'CONFIRMED_TERMINATED')

    def test_ordinary_bytes_preserved_and_real_process_return_sanitized(self):
        with Journal(self.root) as journal:
            result = ProcessSupervisor(
                (sys.executable, '-B', '-c',
                 'import sys; print("ok --token=' + SECRET + '"); sys.stderr.write("ordinary\\n")'),
                Limits(wall_seconds=1, grace_seconds=.1, cleanup_seconds=.2),
                journal=journal, journal_identity=IDENTITY).run()
            _, stdout, stderr, _ = self.captured(journal)
            self.assertFalse(SECRET.encode() in stdout + result['stdout'])
            self.assertEqual(result['stdout'], stdout)
            self.assertEqual(result['stderr'], stderr)
            self.assertEqual(stderr, b'ordinary\n')

    def test_ordinary_prefix_that_is_not_json_is_preserved(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            ordinary = b'{progress without a JSON document\n'
            journal.store_capture(123, 'start-123', 0, ordinary, b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertEqual(stdout, ordinary)

    def test_unrelated_json_stream_preserves_numeric_lexeme(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            ordinary = b'{"count":1e400}'
            journal.store_capture(123, 'start-123', 0,
                                  b'--token=abcdefgh', ordinary, True)
            _, _, stderr, _ = self.captured(journal)
            self.assertEqual(stderr, ordinary)

    def test_sensitive_json_preserves_numeric_lexeme(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            raw = b'{"token":"abcdefgh","count":0.12345678901234567890}'
            journal.store_capture(123, 'start-123', 0, raw, b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertIn(b'0.12345678901234567890', stdout)
            self.assertFalse(b'abcdefgh' in stdout)

    def test_duplicate_json_keys_do_not_hide_first_value(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            journal.store_capture(123, 'start-123', 0,
                                  b'{"token":"abcdefgh","token":"ijklmnop"}', b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertFalse(b'abcdefgh' in stdout)
            self.assertFalse(b'ijklmnop' in stdout)

    def test_non_utf8_ordinary_bracket_log_is_preserved(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            ordinary = b'[INFO] ordinary \xe9 message\n'
            journal.store_capture(123, 'start-123', 0, ordinary, b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertEqual(stdout, ordinary)

    def test_bracket_prefixed_ordinary_log_is_preserved(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            ordinary = b'[INFO] secretary connected\n'
            journal.store_capture(123, 'start-123', 0, ordinary, b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertEqual(stdout, ordinary)

    def test_uncertain_journal_cleanup_never_returns_raw_capture(self):
        with Journal(self.root) as journal:
            supervisor = ProcessSupervisor(
                (sys.executable, '-B', '-c',
                 'import time; print("--token=' + SECRET + '",flush=True); time.sleep(2)'),
                Limits(wall_seconds=.2, grace_seconds=.1, cleanup_seconds=.2),
                journal=journal, journal_identity=IDENTITY)
            with patch.object(journal, 'record_stopping', side_effect=JournalBlocked('controlled')):
                result = supervisor.run()
            self.assertEqual(result['status'], 'INFRA_LOCK')
            self.assertFalse(SECRET.encode() in result['stdout'] + result['stderr'])

    def test_overlapping_values_have_stable_replacement(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            journal.store_capture(123, 'start-123', 0,
                                  b'--token=abcdefgh --token=abcdefghijkl', b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertEqual(stdout, b'--token=[REDACTED] --token=[REDACTED]')

    def test_sensitive_json_with_large_number_preserves_lexeme(self):
        with Journal(self.root) as journal:
            self.terminal(journal)
            journal.store_capture(123, 'start-123', 0,
                                  b'{"token":"abcdefgh","count":1e400}', b'', True)
            _, stdout, _, _ = self.captured(journal)
            self.assertIn(b'"count":1e400', stdout)
            self.assertFalse(b'abcdefgh' in stdout)


if __name__ == '__main__':
    unittest.main()
