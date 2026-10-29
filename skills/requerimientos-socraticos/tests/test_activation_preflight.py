"""Activation role viability and structured public preflight outcomes."""
import importlib.util
import json
from pathlib import Path
import resource
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('activation_preflight', SCRIPTS/'activation_preflight.py')
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)
MIB = preflight.MIB


class ActivationPreflightTests(unittest.TestCase):
    def evaluate(self, headroom=2048*MIB, hard=resource.RLIM_INFINITY, soft=resource.RLIM_INFINITY,
                 baseline=32*MIB, **kwargs):
        with patch.object(preflight.memory_budget, '_visible_headroom', return_value=(headroom, {}, {})), \
             patch.object(preflight.memory_budget.resource, 'getrlimit', return_value=(soft, hard)), \
             patch.object(preflight.memory_budget, 'observe_process_memory', return_value={'virtual_bytes': baseline}):
            return preflight.evaluate('/tmp', **kwargs)

    def test_selects_headroom_profile_and_reports_controls_pending(self):
        report = self.evaluate(headroom=900*MIB, workload='logic', caller_scope='EXTERNAL_CALLER')
        self.assertEqual(report['policy']['selected_profile_mib'], 448)
        self.assertEqual(report['policy']['calibration'], 'NOT_CALIBRATED')
        self.assertFalse(report['execution']['authorized'])
        self.assertEqual(report['execution']['gate'], 'LIVE_ADMISSION_REQUIRED')
        self.assertEqual(report['execution']['control_state'], 'PENDING')
        self.assertEqual(report['execution']['enforced'], [])

    def test_hard_limit_is_checked_per_role(self):
        git = self.evaluate(hard=128*MIB, workload='git', caller_scope='EXTERNAL_CALLER')
        self.assertEqual(git['status'], 'READY_FOR_LIVE_ADMISSION')
        self.assertEqual(git['policy']['selected_profile_mib'], 256)
        self.assertEqual(git['policy']['role_limits_mib']['coordinator'], 128)
        logic = self.evaluate(hard=128*MIB, workload='logic', caller_scope='EXTERNAL_CALLER')
        self.assertEqual(logic['status'], 'INCONCLUSIVE')
        self.assertEqual(logic['error']['code'], 'RESOURCE_HARD_LIMIT_INSUFFICIENT')
        logic384 = self.evaluate(hard=384*MIB, workload='logic', caller_scope='EXTERNAL_CALLER')
        self.assertEqual(logic384['policy']['selected_profile_mib'], 432)
        self.assertEqual(logic384['policy']['role_limits_mib']['solver'], 378)
        all384 = self.evaluate(hard=384*MIB, workload='all', caller_scope='EXTERNAL_CALLER')
        self.assertEqual(all384['policy']['selected_profile_mib'], 432)
        self.assertLessEqual(all384['policy']['role_limits_mib']['coordinator'], 384)

    def test_owned_cli_baseline_blocks_but_external_api_baseline_is_not_caller_gate(self):
        owned = self.evaluate(baseline=100*MIB, workload='logic', caller_scope='OWNED_CLI')
        self.assertEqual(owned['status'], 'INCONCLUSIVE')
        self.assertEqual(owned['error']['code'], 'RESOURCE_BASELINE_EXCEEDS_ROLE_BUDGET')
        external = self.evaluate(baseline=100*MIB, workload='logic', caller_scope='EXTERNAL_CALLER')
        self.assertEqual(external['status'], 'READY_FOR_LIVE_ADMISSION')
        self.assertIsNone(external['evidence']['caller_baseline_bytes'])
        self.assertEqual(external['evidence']['caller_baseline_status'], 'NOT_APPLICABLE')

    def test_explicit_profile_must_fit_roles_and_headroom(self):
        fixed = self.evaluate(hard=384*MIB, workload='logic', caller_scope='EXTERNAL_CALLER', requested_mib=512)
        self.assertEqual(fixed['status'], 'INCONCLUSIVE')
        self.assertEqual(fixed['error']['code'], 'RESOURCE_PROFILE_EXCEEDS_ADMITTED')
        low = self.evaluate(headroom=512*MIB, workload='logic', caller_scope='EXTERNAL_CALLER')
        self.assertEqual(low['policy']['selected_profile_mib'], 256)

    def test_unknown_inherited_hard_and_cli_baseline_block(self):
        unknown_hard = self.evaluate(hard=None, workload='logic', caller_scope='EXTERNAL_CALLER')
        self.assertEqual(unknown_hard['status'], 'INCONCLUSIVE')
        self.assertEqual(unknown_hard['error']['code'], 'RESOURCE_HARD_LIMIT_UNKNOWN')
        self.assertEqual(unknown_hard['capabilities']['workers'], 'UNKNOWN')
        self.assertIsNone(unknown_hard['execution']['effective_profile_mib'])
        unknown_baseline = self.evaluate(baseline=None, workload='logic', caller_scope='OWNED_CLI')
        self.assertEqual(unknown_baseline['status'], 'INCONCLUSIVE')
        self.assertEqual(unknown_baseline['error']['code'], 'RESOURCE_BASELINE_UNKNOWN')
        self.assertEqual(unknown_baseline['capabilities']['workers'], 'UNKNOWN')

    def test_unknown_hard_does_not_claim_soft_unlimited(self):
        with patch.object(preflight.memory_budget.resource, 'getrlimit', side_effect=OSError('unknown')):
            report = preflight.evaluate('/tmp', workload='logic', caller_scope='EXTERNAL_CALLER')
        self.assertEqual(report['policy']['inherited_as_hard_status'], 'UNKNOWN')
        self.assertIsNone(report['evidence']['inherited_as_soft_unlimited'])
        self.assertEqual(report['evidence']['inherited_as_soft_status'], 'UNKNOWN')

    def test_unknown_headroom_is_structured_and_blocks_workers(self):
        with patch.object(preflight.memory_budget, '_visible_headroom',
                          side_effect=preflight.memory_budget.ResourceBudgetError('RESOURCE_HEADROOM_UNKNOWN')):
            report = preflight.evaluate('/tmp', workload='logic', caller_scope='EXTERNAL_CALLER')
        self.assertEqual(report['status'], 'INCONCLUSIVE')
        self.assertEqual(report['execution']['workers'], 'BLOCKED')
        self.assertEqual(report['capabilities']['workers'], 'UNKNOWN')
        self.assertEqual(report['error']['code'], 'RESOURCE_HEADROOM_UNKNOWN')

    def test_cli_invalid_profiles_return_json_without_traceback(self):
        script = SCRIPTS/'activation_preflight.py'
        for value in ('0', '520'):
            run = subprocess.run([sys.executable, '-B', str(script), '--memory-budget-mib', value],
                                 capture_output=True, text=True, timeout=5)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(run.stderr, '')
            report = json.loads(run.stdout)
            self.assertEqual(report['status'], 'INCONCLUSIVE')
            self.assertIn(report['error']['code'], ('INVALID_MEMORY_BUDGET', 'RESOURCE_PROFILE_EXCEEDS_ADMITTED'))




if __name__ == '__main__':
    unittest.main()
