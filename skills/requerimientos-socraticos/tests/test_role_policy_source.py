"""A policy update must affect preflight admission without a copied fraction table."""
import importlib.util
from pathlib import Path
import resource
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('role_policy_preflight', SCRIPTS / 'activation_preflight.py')
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)
MIB = preflight.MIB


class RolePolicySourceTests(unittest.TestCase):
    def evaluate(self, workload, hard_mib):
        with patch.object(preflight.memory_budget, '_visible_headroom',
                          return_value=(2048 * MIB, {}, {})), \
             patch.object(preflight.memory_budget.resource, 'getrlimit',
                          return_value=(hard_mib * MIB, hard_mib * MIB)):
            return preflight.evaluate('/tmp', requested_mib=512, workload=workload,
                                      caller_scope=preflight.EXTERNAL)

    def test_logic_admission_tracks_changed_policy_roles(self):
        original = preflight.memory_budget.logic_memory_policy

        def balanced(total):
            policy = original(total)
            policy['roles_mib'] = {'caller': total // 2, 'solver': total // 2}
            policy['roles_bytes'] = {key: value * MIB for key, value in policy['roles_mib'].items()}
            return policy

        with patch.object(preflight.memory_budget, 'logic_memory_policy', side_effect=balanced):
            report = self.evaluate('logic', 384)
        self.assertEqual(report['status'], 'READY_FOR_LIVE_ADMISSION')
        self.assertEqual(report['policy']['effective_profile_mib'], 512)
        self.assertEqual(report['policy']['role_limits_mib'], {'caller': 256, 'solver': 256})

    def test_git_admission_tracks_changed_policy_roles(self):
        original = preflight.memory_budget.memory_policy

        def balanced(total):
            policy = original(total)
            unit = total // 8
            policy['roles_mib'] = {'caller': unit, 'coordinator': unit * 3,
                                   'consumer': unit * 3, 'git': unit}
            policy['roles_bytes'] = {key: value * MIB for key, value in policy['roles_mib'].items()}
            return policy

        with patch.object(preflight.memory_budget, 'memory_policy', side_effect=balanced):
            report = self.evaluate('git', 192)
        self.assertEqual(report['status'], 'READY_FOR_LIVE_ADMISSION')
        self.assertEqual(report['policy']['role_limits_mib'],
                         {'caller': 64, 'coordinator': 192, 'consumer': 192, 'git': 64})

    def test_all_uses_largest_shared_role_from_both_policies(self):
        original = preflight.memory_budget.logic_memory_policy

        def larger_caller(total):
            policy = original(total)
            policy['roles_mib'] = {'caller': total // 8 * 6, 'solver': total // 8 * 2}
            policy['roles_bytes'] = {key: value * MIB for key, value in policy['roles_mib'].items()}
            return policy

        with patch.object(preflight.memory_budget, 'logic_memory_policy', side_effect=larger_caller):
            report = self.evaluate('all', 384)
        self.assertEqual(report['status'], 'READY_FOR_LIVE_ADMISSION')
        self.assertEqual(report['policy']['role_limits_mib'],
                         {'caller': 384, 'coordinator': 256, 'consumer': 128, 'git': 64, 'solver': 128})

    def test_actual_512_mib_roles_remain_byte_exact(self):
        self.assertEqual(preflight.memory_budget.logic_memory_policy(512)['roles_bytes'],
                         {'caller': 67108864, 'solver': 469762048})
        self.assertEqual(preflight.memory_budget.memory_policy(512)['roles_bytes'],
                         {'caller': 67108864, 'coordinator': 268435456,
                          'consumer': 134217728, 'git': 67108864})


if __name__ == '__main__':
    unittest.main()

