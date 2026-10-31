"""Controlled exceptions exercise classification without exhausting resources."""
import contextlib
import errno
import io
import json
import unittest
from unittest.mock import patch
from test_report import qa

class InfrastructureChecks(unittest.TestCase):
    def invoke(self, error):
        output = io.StringIO()
        with patch.object(qa, 'read_regular', side_effect=error), contextlib.redirect_stdout(output):
            code = qa.main(['--report', 'fixture.json', '--evidence-root', '.'])
        return code, json.loads(output.getvalue())

    def check_infra(self, error):
        code, result = self.invoke(error)
        self.assertEqual(code, 3)
        self.assertEqual(result['execution_status'], 'INFRA_FAILURE')
        self.assertEqual(result['document_validation'], 'NOT_ASSESSED')
        self.assertIsNone(result['proposed_event'])
        self.assertIsNone(result['verdict'])
        self.assertFalse(result['execution_performed'])
        self.assertEqual(result['diagnostic']['exception_type'], type(error).__name__)

    def test_memory_failure(self): self.check_infra(MemoryError('controlled'))
    def test_io_failure(self): self.check_infra(OSError(errno.EIO, 'controlled'))
    def test_permission_failure(self): self.check_infra(PermissionError(errno.EACCES, 'controlled'))
    def test_missing_artifact(self): self.check_infra(FileNotFoundError(errno.ENOENT, 'controlled'))
    def test_recursion_resource_failure(self): self.check_infra(RecursionError('controlled'))

    def test_invalid_data_stays_rejected(self):
        code, result = self.invoke(ValueError('INVALID_INPUT'))
        self.assertEqual(code, 2)
        self.assertEqual(result['proposed_event'], 'REJECT_INPUT')
        self.assertEqual(result['execution_status'], 'COMPLETED')

    def test_no_oom_claim_from_io_error(self):
        _, result = self.invoke(OSError(errno.EIO, 'controlled'))
        self.assertEqual(result['diagnostic']['errno'], errno.EIO)
        self.assertEqual(result['diagnostic']['cause'], 'NOT_DETERMINED')
