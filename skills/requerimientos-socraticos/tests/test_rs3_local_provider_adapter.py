"""Bounded local fake-provider tests; no network or external model is used."""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from local_provider_adapter import LocalProviderAdapter
from source_snapshot import SourceSnapshot


def proposal_bytes():
    item = {'schema_version': '0.1-proposed', 'id': 'RS3-PROVIDER-1',
            'source_ref': 'synthetic/provider/1', 'source_text': 'P solo si Q',
            'status': 'PROPOSED', 'kind': 'NECESSARY_CONDITION',
            'modality': 'MUST', 'subject': 'P', 'condition': 'Q',
            'direction': 'SUBJECT_IMPLIES_CONDITION',
            'assumptions': [], 'exceptions': [], 'human_confirmation': 'PENDING'}
    return json.dumps(item, separators=(',', ':')).encode('utf-8')


def adapter(code, timeout=.5):
    return LocalProviderAdapter((sys.executable, '-I', '-B', '-c', code),
                                SourceSnapshot('synthetic/provider/1', 'P solo si Q'),
                                timeout_seconds=timeout)


class LocalProviderAdapterTests(unittest.TestCase):
    def test_valid_stdout_and_stderr_noise_stay_separate(self):
        payload = proposal_bytes()
        code = (f'import sys;sys.stderr.write("synthetic warning\\n");'
                f'sys.stdout.buffer.write({payload!r})')
        result = adapter(code).invoke()
        self.assertEqual(result['admission'], 'PROPOSED_FOR_REVIEW')
        self.assertTrue(result['stderr_observed'])
        self.assertNotIn('synthetic warning', str(result))
        self.assertIs(result['execution_authorized'], False)
        self.assertEqual(result['authority_verification'], 'NOT_ESTABLISHED')

    def test_timeout_nonzero_signal_and_truncated_stdout_never_admit(self):
        cases = (
            ('import time;time.sleep(2)', .05, 'INFRA_FAILURE', 'PROVIDER_TIMEOUT'),
            ('import sys;sys.exit(7)', .5, 'INFRA_FAILURE', 'PROVIDER_EXIT_NONZERO'),
            ('import os,signal;os.kill(os.getpid(),signal.SIGKILL)',
             .5, 'INFRA_FAILURE', 'PROVIDER_SIGNAL_OBSERVED'),
            ("import sys;sys.stdout.buffer.write(b'{\"schema_version\":')",
             .5, 'REJECT_INPUT', 'INVALID_JSON'),
            ("import os;os.write(1,b'X'*20000)",
             .5, 'REJECT_INPUT', 'PROVIDER_OUTPUT_LIMIT'),
        )
        for code, timeout, admission, reason in cases:
            with self.subTest(reason=reason):
                result = adapter(code, timeout).invoke()
                self.assertEqual((result['admission'], result['reason_code']),
                                 (admission, reason))
                self.assertIsNone(result['ast'])
                self.assertIs(result['execution_authorized'], False)
                self.assertNotIn('OOM', str(result))

    def test_empty_stdout_is_rejected(self):
        result = adapter('pass').invoke()
        self.assertEqual((result['admission'], result['reason_code']),
                         ('REJECT_INPUT', 'PROVIDER_EMPTY_OUTPUT'))

    def test_cleanup_uncertainty_latches_instance(self):
        fake = {'status': 'EXITED', 'cleanup_status': 'INCOMPLETE',
                'returncode': 0, 'stdout_bytes': proposal_bytes(),
                'stderr_bytes': b'', 'timed_out': False, 'output_limit': False}
        instance = adapter('pass')
        with patch('local_provider_adapter.run_supervised', return_value=fake) as run:
            first = instance.invoke()
            second = instance.invoke()
            third = instance.invoke()
        self.assertEqual(first['admission'], 'INFRA_LOCK')
        self.assertEqual(second['admission'], 'INFRA_LOCK')
        self.assertEqual(third['admission'], 'INFRA_LOCK')
        self.assertEqual(run.call_count, 1)

    def test_incomplete_supervisor_record_latches_without_exception(self):
        instance = adapter('pass')
        with patch('local_provider_adapter.run_supervised', return_value={'status': 'EXITED'}):
            result = instance.invoke()
        self.assertEqual(result['admission'], 'INFRA_LOCK')
        self.assertEqual(instance.invoke()['admission'], 'INFRA_LOCK')

    def test_launch_failure_is_infrastructure_not_document_rejection(self):
        instance = adapter('pass')
        with patch('local_provider_adapter.run_supervised', side_effect=OSError):
            result = instance.invoke()
        self.assertEqual(result['admission'], 'INFRA_FAILURE')
        self.assertEqual(result['reason_code'], 'PROVIDER_LAUNCH_OR_RESOURCE_FAILURE')

    def test_bad_configuration_and_alternate_payload_reject_before_launch(self):
        with self.assertRaises(ValueError):
            LocalProviderAdapter(('python3', '-c', 'pass'),
                                 SourceSnapshot('synthetic/provider/1', 'P solo si Q'))
        with self.assertRaises(ValueError):
            adapter('pass', 0)
        instance = adapter('pass')
        with patch('local_provider_adapter.run_supervised') as run:
            with self.assertRaises(TypeError):
                instance.invoke('text')
            with self.assertRaises(TypeError):
                instance.invoke(b'X' * 8193)
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
