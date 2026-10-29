"""Tiny documents and process-local budgets; never exhaust host memory."""
import json
import contextlib
import io
from pathlib import Path
import resource
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'tests'))
import validate_git
import git_document_worker
import git_validation_engine
import process_supervision
import test_sealed


class ValidationBudgetTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_sealed.SealedTests('test_sha256_git_objects')
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.commit = self.fixture.stage()

    def test_library_caller_limits_unchanged_and_data_workers_capped(self):
        previous = resource.getrlimit(resource.RLIMIT_AS)
        result = validate_git.validate_commit(self.fixture.repo, self.commit, 'prd.json', memory_budget_mib=512)
        self.assertEqual(resource.getrlimit(resource.RLIMIT_AS), previous)
        self.assertEqual(result['status'], 'DOCUMENT_VALIDATED_GIT')
        budget = result['memory_budget']
        self.assertEqual(budget['policy']['total_mib'], 512)
        self.assertEqual(budget['coordinator']['as_soft_bytes'], 256*1024*1024)
        self.assertEqual(budget['consumer']['as_soft_bytes'], 128*1024*1024)
        self.assertEqual(budget['caller']['scope'], 'EXTERNAL_CALLER_NOT_LIMITED')
        self.assertGreater(budget['coordinator']['peak_rss_bytes'], 0)
        self.assertGreater(budget['consumer']['peak_rss_bytes'], 0)
        self.assertEqual(result['advance'], 'BLOCKED_GLOBAL_ENFORCEMENT')
        gate = result['memory_budget']['activation_preflight']
        self.assertEqual(gate['execution']['control_state'], 'APPLIED')
        self.assertEqual(gate['execution']['workers'], 'COMPLETED')
        self.assertIn('coordinator role-specific RLIMIT_AS applied before exec', gate['execution']['enforced'])

    def test_public_cli_bounds_owned_caller_and_keeps_byte_identity(self):
        run = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/validate_git.py'),
                              str(self.fixture.repo), '--commit', self.commit, '--prd', 'prd.json',
                              '--memory-budget-mib', '512'], capture_output=True, text=True, timeout=8)
        self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result['memory_budget']['caller']['as_soft_bytes'], 64*1024*1024)
        self.assertEqual(result['document_transport'], 'VERIFIED_BYTES_STDIN')

    def test_invalid_policy_rejected_before_spawning(self):
        with patch.object(validate_git, 'run_supervised', side_effect=AssertionError('must not spawn')) as run:
            for value in [0, 257, True, 2048]:
                with self.subTest(value=value), self.assertRaisesRegex(validate_git.InvalidGit, 'INVALID_MEMORY_BUDGET'):
                    validate_git.validate_commit(self.fixture.repo, self.commit, 'prd.json', memory_budget_mib=value)
        run.assert_not_called()

    def test_live_preflight_rejection_starts_no_validation_worker(self):
        blocked = {'status': 'INCONCLUSIVE', 'error': {'code': 'RESOURCE_HEADROOM_UNKNOWN'}}
        with patch.object(validate_git.activation_preflight, 'evaluate', return_value=blocked), \
                patch.object(validate_git, 'run_supervised', side_effect=AssertionError('worker must not start')) as run:
            with self.assertRaisesRegex(validate_git.InvalidGit, 'RESOURCE_HEADROOM_UNKNOWN'):
                validate_git.validate_commit(self.fixture.repo, self.commit, 'prd.json')
        run.assert_not_called()

    def test_explicit_coordinator_memory_failure_blocks(self):
        response = {'returncode': 1, 'stdout': '{"status":"BLOCKED","error":"MEMORY_BUDGET_EXCEEDED"}',
                    'timed_out': False, 'output_limit': False,
                    'cleanup_status': 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED'}
        with patch.object(validate_git, 'run_supervised', return_value=response):
            with self.assertRaisesRegex(validate_git.InvalidGit, 'MEMORY_BUDGET_EXCEEDED'):
                validate_git.validate_commit(self.fixture.repo, self.commit, 'prd.json', memory_budget_mib=512)

    def test_missing_diagnostic_is_not_reported_as_proven_memory_exhaustion(self):
        response = {'returncode': -9, 'stdout': '', 'timed_out': False, 'output_limit': False,
                    'cleanup_status': 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED'}
        with patch.object(validate_git, 'run_supervised', return_value=response):
            with self.assertRaisesRegex(validate_git.InvalidGit, 'COORDINATOR_FAILED_WITHOUT_STRUCTURED_RESULT'):
                validate_git.validate_commit(self.fixture.repo, self.commit, 'prd.json')

    def test_document_memory_error_returns_fixed_failure_record(self):
        with patch('git_bundle.read_bundle', side_effect=MemoryError), \
                patch.object(git_document_worker.os, 'write') as write:
            code = git_document_worker.main()
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(write.call_args.args[1])['error'], 'MEMORY_BUDGET_EXCEEDED')

    def test_coordinator_memory_error_returns_fixed_failure_record(self):
        arguments = ['engine', str(self.fixture.repo), '--commit', self.commit, '--prd', 'prd.json',
                     '--memory-budget-mib', '512', '--lease-fd', '0']
        with patch.object(sys, 'argv', arguments), \
                patch.object(git_validation_engine, 'observe_process_memory', return_value={'as_soft_bytes': 256*1024*1024}), \
                patch.object(git_validation_engine, 'validate_local', side_effect=MemoryError), \
                patch.object(git_validation_engine.os, 'write') as write:
            code = git_validation_engine.main()
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(write.call_args.args[1])['error'], 'MEMORY_BUDGET_EXCEEDED')

    def test_auto_git_profile_fits_inherited_role_hard_without_changing_caller(self):
        previous = resource.getrlimit(resource.RLIMIT_AS)
        with patch.object(process_supervision.resource, 'getrlimit', return_value=(128*1024*1024,)*2), \
                patch.object(validate_git, 'run_supervised', side_effect=OSError('test stop')) as run:
            with self.assertRaisesRegex(validate_git.InvalidGit, 'RESOURCE_CONTROL_SETUP_FAILED'):
                validate_git.validate_commit(self.fixture.repo, self.commit, 'prd.json')
        self.assertEqual(run.call_args.kwargs['address_space_limit'], (128*1024*1024, 128*1024*1024))
        self.assertEqual(resource.getrlimit(resource.RLIMIT_AS), previous)

    def test_cli_rejects_budget_below_existing_virtual_size_before_changing_limits(self):
        argv = ['validate_git.py', str(self.fixture.repo), '--commit', self.commit, '--prd', 'prd.json']
        output = io.StringIO()
        with patch.object(sys, 'argv', argv), \
                patch.object(validate_git, 'observe_process_memory', return_value={'virtual_bytes': 64*1024*1024+1}), \
                patch.object(validate_git, 'enforce_address_space', side_effect=AssertionError('must not lower limits')) as enforce, \
                patch.object(validate_git, 'validate_commit', side_effect=AssertionError('must not validate')), \
                contextlib.redirect_stdout(output):
            code = validate_git.main()
        enforce.assert_not_called()
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())['error_code'], 'RESOURCE_BASELINE_EXCEEDS_ROLE_BUDGET')

    def test_coordinator_transport_keeps_room_for_existing_complete_manifest(self):
        response = {'returncode': 0, 'stdout': '{"status":"DOCUMENT_VALIDATED_GIT","memory_budget":{}}',
                    'timed_out': False, 'output_limit': False,
                    'cleanup_status': 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED'}
        with patch.object(validate_git, 'run_supervised', return_value=response) as run:
            validate_git.validate_commit(self.fixture.repo, self.commit, 'prd.json')
        self.assertEqual(run.call_args.kwargs['output_limit_bytes'], 8*1024*1024)


if __name__ == '__main__':
    unittest.main()
