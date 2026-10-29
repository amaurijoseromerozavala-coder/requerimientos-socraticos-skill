"""Small owned analyzer cases; no memory exhaustion or unowned process signals."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/analyze_logic.py'
MIB = 1024 * 1024
MODEL = {'inputs': [], 'outputs': [], 'domain': True, 'rules': [], 'properties': []}


def load():
    spec = importlib.util.spec_from_file_location('requirements_logic_memory_test', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def lease(policy):
    yield 123, {'status': 'ADMITTED_COOPERATIVE'}


def worker(document=None, code=0):
    return {'timed_out': False, 'returncode': code,
            'stdout': json.dumps(document if document is not None else {'status': 'ANALYZED'}),
            'elapsed_seconds': .01, 'parent_death_policy': 'LINUX_DIRECT_CHILD_PDEATHSIG',
            'cleanup_status': 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED'}


class LogicMemoryTests(unittest.TestCase):
    def invoke(self, module, response=None, own=False, args=(), **patches):
        captured = io.StringIO()
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(sys, 'argv', [str(SCRIPT), 'fixture.json', '--timeout', '2', *args]))
            stack.enter_context(patch.object(module, 'runtime_identity', return_value={}))
            stack.enter_context(patch.object(module, 'admission', side_effect=lease))
            if own:
                baseline = patches.get('observe_process_memory', {}).get('return_value', {}).get(
                    'virtual_bytes', 32*MIB)
                if 'observe_process_memory' not in patches:
                    stack.enter_context(patch.object(module, 'observe_process_memory', return_value={
                        'scope': 'PROCESS_LOCAL_SAMPLES', 'virtual_bytes': baseline,
                        'as_soft_bytes': 64*MIB, 'as_hard_bytes': 448*MIB}))
                stack.enter_context(patch.object(
                    module.activation_preflight.memory_budget, 'observe_process_memory',
                    return_value={'virtual_bytes': baseline}))
            run = stack.enter_context(patch.object(module, 'run_supervised', return_value=response or worker()))
            for name, value in patches.items():
                stack.enter_context(patch.object(module, name, **value))
            stack.enter_context(contextlib.redirect_stdout(captured))
            result = module.main(_own_cli=own)
        return result, json.loads(captured.getvalue()), run

    def test_api_preserves_external_limits_and_sets_worker_limit_and_lease(self):
        module = load()
        before = resource.getrlimit(resource.RLIMIT_AS)
        code, document, run = self.invoke(module)
        self.assertEqual(code, 0)
        self.assertEqual(resource.getrlimit(resource.RLIMIT_AS), before)
        self.assertEqual(run.call_args.kwargs['address_space_limit'], (448*MIB, 448*MIB))
        self.assertEqual(run.call_args.kwargs['pass_fds'], (123,))
        self.assertEqual(document['memory_budget']['policy']['workload'], 'BOOLEAN_ANALYSIS')
        self.assertEqual(document['memory_budget']['caller']['scope'], 'EXTERNAL_CALLER_NOT_LIMITED')
        gate = document['memory_budget']['activation_preflight']
        self.assertEqual(gate['execution']['control_state'], 'APPLIED')
        self.assertEqual(gate['execution']['workers'], 'COMPLETED')
        self.assertIn('role-specific RLIMIT_AS applied before worker exec', gate['execution']['enforced'])

    def test_invalid_policy_is_coded_without_worker(self):
        for value, expected in [('255', 'RESOURCE_POLICY_INVALID'), ('257', 'RESOURCE_POLICY_INVALID'),
                                ('1032', 'RESOURCE_POLICY_INVALID')]:
            with self.subTest(value=value):
                code, result, run = self.invoke(load(), args=('--memory-budget-mib', value))
                self.assertEqual(code, 3)
                self.assertEqual(result['error']['code'], expected)
                run.assert_not_called()

    def test_memory_argument_type_preserves_invalid_input(self):
        code, result, run = self.invoke(load(), args=('--memory-budget-mib', 'bad'))
        self.assertEqual(code, 2)
        self.assertEqual(result['error']['code'], 'INVALID_INPUT')
        run.assert_not_called()

    def test_fresh_preflight_after_activation_conditions_change_blocks_worker(self):
        module = load()
        first = module.activation_preflight.evaluate(
            '/tmp', workload='logic', caller_scope='EXTERNAL_CALLER')
        self.assertIn(first['status'], ('READY_FOR_LIVE_ADMISSION', 'INCONCLUSIVE'))
        changed = {'status': 'INCONCLUSIVE', 'error': {'code': 'RESOURCE_HEADROOM_INSUFFICIENT'}}
        with patch.object(module.activation_preflight, 'evaluate', return_value=changed):
            code, result, run = self.invoke(module)
        self.assertEqual((code, result['error']['code']), (3, 'RESOURCE_HEADROOM_INSUFFICIENT'))
        run.assert_not_called()

    def test_live_preflight_rejection_starts_no_worker(self):
        module = load()
        blocked = {'status': 'INCONCLUSIVE', 'error': {'code': 'RESOURCE_HEADROOM_UNKNOWN'}}
        with patch.object(module.activation_preflight, 'evaluate', return_value=blocked):
            code, result, run = self.invoke(module)
        self.assertEqual((code, result['error']['code']), (3, 'RESOURCE_HEADROOM_UNKNOWN'))
        run.assert_not_called()

    def test_resource_rejection_is_inconclusive(self):
        module = load()
        code, result, run = self.invoke(module, admission={'side_effect': module.ResourceBudgetError('RESOURCE_BUSY')})
        self.assertEqual((code, result['status'], result['error']['code']), (3, 'INCONCLUSIVE', 'RESOURCE_BUSY'))
        run.assert_not_called()

    def test_baseline_checked_before_owned_cli_limit(self):
        module = load()
        with patch.object(module, 'enforce_address_space') as enforce:
            code, result, run = self.invoke(module, own=True, observe_process_memory={'return_value': {'virtual_bytes': 65*MIB}})
        self.assertEqual((code, result['error']['code']), (3, 'RESOURCE_BASELINE_EXCEEDS_ROLE_BUDGET'))
        enforce.assert_not_called()
        run.assert_not_called()

    def test_unknown_baseline_does_not_limit_owned_cli(self):
        module = load()
        with patch.object(module, 'enforce_address_space') as enforce:
            code, result, run = self.invoke(module, own=True, observe_process_memory={'return_value': {'virtual_bytes': None}})
        self.assertEqual((code, result['error']['code']), (3, 'RESOURCE_BASELINE_UNKNOWN'))
        enforce.assert_not_called()
        run.assert_not_called()

    def test_owned_cli_limit_leaves_room_for_worker(self):
        module = load()
        observation = {'as_soft_bytes': 448*MIB, 'as_hard_bytes': 448*MIB}
        with patch.object(module, 'enforce_address_space') as enforce:
            code, result, _ = self.invoke(module, own=True, response=worker({'status': 'ANALYZED', 'memory_observation': observation}))
        self.assertEqual(code, 0)
        enforce.assert_called_once_with(64*MIB, 448*MIB)
        self.assertEqual(result['memory_budget']['caller']['scope'], 'OWNED_CLI_PROCESS')

    def test_setup_exception_is_resource_control_failure(self):
        code, result, _ = self.invoke(load(), run_supervised={'side_effect': subprocess.SubprocessError('preexec setup failed')})
        self.assertEqual((code, result['status'], result['error']['code']), (3, 'INCONCLUSIVE', 'RESOURCE_CONTROL_SETUP_FAILED'))

    def test_explicit_memory_error_removes_approbatory_payload(self):
        response = worker({'error': {'code': 'MEMORY_BUDGET_EXCEEDED'}, 'queries': [True], 'table': [True], 'coverage': 1}, code=2)
        code, result, _ = self.invoke(load(), response=response)
        self.assertEqual((code, result['status'], result['error']['code']), (3, 'INCONCLUSIVE', 'MEMORY_BUDGET_EXCEEDED'))
        for key in ['queries', 'table', 'coverage']:
            self.assertNotIn(key, result)

    def test_signal_without_diagnostic_is_not_called_oom(self):
        response = worker(code=-9)
        response['stdout'] = ''
        code, result, _ = self.invoke(load(), response=response)
        self.assertEqual((code, result['error']['code']), (2, 'WORKER_FAILED'))
        self.assertEqual(result['worker_returncode'], -9)

    def test_ordinary_worker_errors_preserve_contract_without_observation(self):
        for error in ['INVALID_INPUT', 'SOLVER_ERROR', 'SOLVER_UNAVAILABLE']:
            with self.subTest(error=error):
                module = load()
                with patch.object(module, 'enforce_address_space'):
                    code, result, _ = self.invoke(module, own=True, response=worker({'error': {'code': error}}, code=2))
                self.assertEqual((code, result['error']['code']), (2, error))

    def test_owned_cli_success_requires_observed_worker_limits(self):
        for observation in [None, {'as_soft_bytes': 447*MIB, 'as_hard_bytes': 448*MIB}]:
            with self.subTest(observation=observation):
                module = load()
                with patch.object(module, 'enforce_address_space'):
                    code, result, _ = self.invoke(module, own=True, response=worker({'status': 'ANALYZED', 'memory_observation': observation, 'coverage': 1}))
                self.assertEqual((code, result['error']['code']), (3, 'RESOURCE_LIMIT_NOT_OBSERVED'))
                self.assertNotIn('coverage', result)

    def test_admission_elapsed_time_is_subtracted_before_worker(self):
        module = load()
        @contextlib.contextmanager
        def slow_lease(policy):
            time.sleep(.025)
            yield 123, {'status': 'ADMITTED_COOPERATIVE'}
        code, _, run = self.invoke(module, admission={'side_effect': slow_lease})
        self.assertEqual(code, 0)
        self.assertLess(run.call_args.args[1], 1.98)

    def test_expired_admission_starts_no_worker(self):
        @contextlib.contextmanager
        def slow_lease(policy):
            time.sleep(.025)
            yield 123, {'status': 'ADMITTED_COOPERATIVE'}
        code, result, run = self.invoke(load(), args=('--timeout', '.01'), admission={'side_effect': slow_lease})
        self.assertEqual((code, result['error']['code']), (3, 'WALL_CLOCK_LIMIT'))
        run.assert_not_called()

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux RLIMIT_AS contract')
    def test_real_cli_observes_default_and_configured_process_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'model.json'
            source.write_text(json.dumps(MODEL))
            for total, options in [(512, []), (1024, ['--memory-budget-mib', '1024'])]:
                with self.subTest(total=total):
                    result = subprocess.run([sys.executable, '-B', str(SCRIPT), str(source), '--timeout', '3', *options], text=True, capture_output=True, timeout=6)
                    if total > 512:
                        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                        self.assertEqual(json.loads(result.stdout)['error']['code'], 'RESOURCE_PROFILE_EXCEEDS_ADMITTED')
                        continue
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    document = json.loads(result.stdout)
                    budget = document['memory_budget']
                    caller, solver = total//8*MIB, total*7//8*MIB
                    self.assertEqual(budget['policy']['roles_bytes'], {'caller': caller, 'solver': solver})
                    self.assertEqual(budget['admission']['status'], 'ADMITTED_COOPERATIVE')
                    self.assertEqual(budget['caller']['as_soft_bytes'], caller)
                    self.assertEqual(budget['caller']['as_hard_bytes'], solver)
                    self.assertEqual(document['memory_observation']['as_soft_bytes'], solver)
                    self.assertEqual(document['memory_observation']['as_hard_bytes'], solver)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux account admission lease')
    def test_real_cli_shares_git_admission_gate(self):
        spec = importlib.util.spec_from_file_location('requirements_logic_test_budget', ROOT/'scripts/memory_budget.py')
        budgets = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(budgets)
        with budgets.admission(budgets.memory_policy()):
            result = subprocess.run([sys.executable, '-B', str(SCRIPT), 'unused.json', '--timeout', '2'], text=True, capture_output=True, timeout=4)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        document = json.loads(result.stdout)
        self.assertEqual(document['error']['code'], 'RESOURCE_BUSY')
        self.assertEqual(document['status'], 'INCONCLUSIVE')
        self.assertNotIn('coverage', document)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux inherited hard limit')
    def test_cli_never_raises_inherited_hard_limit(self):
        # Dedicated tiny subprocess, never change the unittest runner's limit.
        code = 'import resource,runpy,sys;resource.setrlimit(resource.RLIMIT_AS,(384*1024*1024,)*2);script=sys.argv[1];sys.argv=[script,"unused.json"];runpy.run_path(script,run_name="__main__")'
        result = subprocess.run([sys.executable, '-B', '-c', code, str(SCRIPT)], capture_output=True, text=True, timeout=4)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        document = json.loads(result.stdout)
        self.assertEqual(document['error']['code'], 'INVALID_INPUT')
        self.assertEqual(document['memory_budget']['activation_preflight']['policy']['selected_profile_mib'], 432)


if __name__ == '__main__':
    unittest.main(verbosity=2)
