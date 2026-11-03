"""Synthetic, bounded controls for the CI suite capture boundary."""
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from ci.safe_suite_capture import run_capture

SECRET = 'SYNTHETIC_SECRET_DO_NOT_USE_001'


class SafeSuiteCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ci-capture-test-')
        self.out = Path(self.temp.name) / 'suite.stdout'
        self.err = Path(self.temp.name) / 'suite.stderr'

    def tearDown(self):
        self.temp.cleanup()

    def run_child(self, script, *, timeout=2):
        return run_capture((sys.executable, '-B', '-c', script), self.out, self.err,
                           timeout=timeout)

    def test_split_stdout_and_separated_stderr_are_sanitized(self):
        script = ('import os,time; os.write(1,b"--tok"); time.sleep(.02); '
                  'os.write(1,b"en=' + SECRET + '"); '
                  'os.write(2,b"--token ' + SECRET + '")')
        self.assertEqual(self.run_child(script), 0)
        self.assertFalse(SECRET.encode() in self.out.read_bytes() + self.err.read_bytes())

    def test_numeric_copy_across_channels_rejects_capture(self):
        script = ('import os; os.write(1,b"--token=12345678"); '
                  'os.write(2,b\'{"copy":12345678}\')')
        self.assertEqual(self.run_child(script), 3)
        self.assertFalse(self.out.exists() or self.err.exists())

    def test_prefixed_json_secret_marker_rejects_capture(self):
        for key in (b'token', b'api-key'):
            with self.subTest(key=key):
                payload = b'INFO {"' + key + b'":"' + SECRET.encode() + b'"}'
                self.assertEqual(self.run_child('import os; os.write(1,' + repr(payload) + ')'), 3)
                self.assertFalse(self.out.exists() or self.err.exists())

    def test_ordinary_bytes_and_failure_code_are_preserved(self):
        script = 'import os,sys; os.write(1,b"ordinary\\n"); os.write(2,b"warning\\n"); sys.exit(7)'
        self.assertEqual(self.run_child(script), 7)
        self.assertEqual(self.out.read_bytes(), b'ordinary\n')
        self.assertEqual(self.err.read_bytes(), b'warning\n')

    def test_sanitizer_failure_never_creates_output_files(self):
        with patch('ci.safe_suite_capture.redact_pair', side_effect=ValueError('controlled')):
            self.assertEqual(self.run_child('print("--token=' + SECRET + '")'), 3)
        self.assertFalse(self.out.exists() or self.err.exists())

    def test_write_failure_never_persists_raw_bytes(self):
        with patch('ci.safe_suite_capture.write_sanitized', side_effect=OSError('controlled')):
            self.assertEqual(self.run_child('print("--token=' + SECRET + '")'), 3)
        self.assertFalse(self.out.exists() or self.err.exists())

    def test_second_file_write_failure_removes_first_sanitized_file(self):
        original = os.open

        def fail_second(path, *args, **kwargs):
            if Path(path) == self.err:
                raise OSError('controlled')
            return original(path, *args, **kwargs)

        with patch('ci.safe_suite_capture.os.open', side_effect=fail_second):
            self.assertEqual(self.run_child('print("--token=' + SECRET + '")'), 3)
        self.assertFalse(self.out.exists() or self.err.exists())

    def test_memory_failure_during_write_removes_partial_files(self):
        with patch('ci.safe_suite_capture.os.fsync', side_effect=MemoryError('controlled')):
            self.assertEqual(self.run_child('print("--token=' + SECRET + '")'), 3)
        self.assertFalse(self.out.exists() or self.err.exists())

    def test_timeout_and_ambiguous_marker_fail_closed(self):
        self.assertEqual(self.run_child('import time; print("--token=' + SECRET + '"); time.sleep(2)',
                                        timeout=.1), 124)
        self.assertFalse(self.out.exists() or self.err.exists())
        self.assertEqual(self.run_child('print("--token=abcdefgh@unknown")'), 3)
        self.assertFalse(self.out.exists() or self.err.exists())

    def test_output_limit_fails_without_files(self):
        with patch('ci.safe_suite_capture.LIMIT', 32):
            self.assertEqual(self.run_child('print("x"*100)'), 3)
        self.assertFalse(self.out.exists() or self.err.exists())


if __name__ == '__main__':
    unittest.main()
