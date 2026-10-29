"""Small deterministic tests of virtual limits and cooperative admission."""
import copy
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import memory_budget as budget


class MemoryBudgetTests(unittest.TestCase):
    def assert_code(self, code, function, *args):
        with self.assertRaises(budget.ResourceBudgetError) as caught:
            function(*args)
        self.assertEqual(caught.exception.code, code)

    def test_policy_roles_and_validation(self):
        profile = budget.memory_policy()
        self.assertEqual(profile['roles_mib'], {'caller': 64, 'coordinator': 256, 'consumer': 128, 'git': 64})
        self.assertEqual(sum(profile['roles_bytes'].values()), profile['total_bytes'])
        self.assertFalse(profile['hardware_capacity_calibrated'])
        for total in (256, 264, 1024):
            self.assertEqual(sum(budget.memory_policy(total)['roles_mib'].values()), total)
        for total in (True, 255, 257, 1032, 512.0, '512', None):
            self.assert_code('RESOURCE_POLICY_INVALID', budget.memory_policy, total)

    def test_git_policy_contract_243_is_unchanged(self):
        self.assertEqual(budget.memory_policy(), {
            'total_mib': 512, 'total_bytes': 512 * budget.MIB,
            'roles_mib': {'caller': 64, 'coordinator': 256, 'consumer': 128, 'git': 64},
            'roles_bytes': {'caller': 64 * budget.MIB, 'coordinator': 256 * budget.MIB,
                            'consumer': 128 * budget.MIB, 'git': 64 * budget.MIB},
            'kind': 'PROVISIONAL_ENGINEERING_POLICY', 'hardware_capacity_calibrated': False,
            'aggregate_kernel_quota': False})

    def test_absolute_file_import_does_not_mutate_module_search_paths(self):
        source = '''import importlib.util, sys
before = list(sys.path)
assert 'probe_environment' not in sys.modules
spec = importlib.util.spec_from_file_location('isolated_budget', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert sys.path == before
assert 'probe_environment' not in sys.modules
assert 'requirements_probe_environment' not in sys.modules
assert module.logic_memory_policy()['roles_mib']['solver'] == 448
print('ISOLATED_IMPORT_OK')
'''
        completed = subprocess.run([sys.executable, '-I', '-B', '-c', source, str(SCRIPTS/'memory_budget.py')],
                                   capture_output=True, text=True, timeout=3)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), 'ISOLATED_IMPORT_OK')

    def test_logic_policy_roles_flags_and_validation(self):
        self.assertEqual(budget.logic_memory_policy(), {
            'total_mib': 512, 'total_bytes': 512 * budget.MIB,
            'roles_mib': {'caller': 64, 'solver': 448},
            'roles_bytes': {'caller': 64 * budget.MIB, 'solver': 448 * budget.MIB},
            'kind': 'PROVISIONAL_ENGINEERING_POLICY', 'hardware_capacity_calibrated': False,
            'aggregate_kernel_quota': False, 'workload': 'BOOLEAN_ANALYSIS'})
        with patch.object(budget.resource, 'setrlimit') as setter:
            for total in (256, 264, 512, 1024):
                profile = budget.logic_memory_policy(total)
                self.assertEqual(profile['roles_mib'], {'caller': total // 8, 'solver': total * 7 // 8})
                self.assertEqual(sum(profile['roles_bytes'].values()), profile['total_bytes'])
            setter.assert_not_called()
        for total in (True, False, 0, 255, 257, 1025, 1032, 512.0, '512', None):
            self.assert_code('RESOURCE_POLICY_INVALID', budget.logic_memory_policy, total)

    def test_logic_and_git_share_one_account_lease(self):
        profiles = (budget.memory_policy(), budget.logic_memory_policy())
        with tempfile.TemporaryDirectory() as root, patch.object(budget, '_admission_directory', return_value=Path(root)/'admission'), self.headroom():
            for first, second in (profiles, profiles[::-1]):
                with budget.admission(first):
                    with self.assertRaisesRegex(budget.ResourceBudgetError, 'RESOURCE_BUSY'):
                        with budget.admission(second):
                            self.fail('workload bypassed shared lease')
                with budget.admission(second) as (fd, observation):
                    self.assertFalse(os.get_inheritable(fd))
                    self.assertEqual(observation['required_headroom_bytes'], 2 * second['total_bytes'])
                    self.assertFalse(observation['physical_reservation'])

    def test_logic_headroom_uses_twice_total_at_exact_boundary(self):
        profile = budget.logic_memory_policy(264)
        required = 2 * profile['total_bytes']
        for available, remaining, admitted in ((required, required, True),
                                                (required - 1, required, False),
                                                (required, required - 1, False)):
            with tempfile.TemporaryDirectory() as root, patch.object(budget, '_admission_directory', return_value=Path(root)/'admission'), self.headroom(available, remaining):
                if admitted:
                    with budget.admission(profile) as (_, observed):
                        self.assertEqual(observed['required_headroom_bytes'], required)
                else:
                    with self.assertRaisesRegex(budget.ResourceBudgetError, 'RESOURCE_HEADROOM_INSUFFICIENT'):
                        with budget.admission(profile):
                            self.fail('insufficient headroom')

    def test_admission_rejects_changed_or_type_coerced_profiles(self):
        self.assert_changed_profiles_rejected(budget.memory_policy)

    def test_logic_admission_rejects_changed_or_type_coerced_profiles(self):
        self.assert_changed_profiles_rejected(budget.logic_memory_policy)

    def assert_changed_profiles_rejected(self, factory):
        mutations = (
            lambda p: p.update(total_bytes=1),
            lambda p: p.update(total_bytes=float(p['total_bytes'])),
            lambda p: p.update(total_mib=float(p['total_mib'])),
            lambda p: p.update(hardware_capacity_calibrated=0),
            lambda p: p.update(aggregate_kernel_quota=0),
            lambda p: p.update(kind='MEASURED_CAPACITY'),
            lambda p: p.update(workload='UNKNOWN'),
            lambda p: p.update(extra='unrecognized'),
            lambda p: p['roles_mib'].update(caller=1),
            lambda p: p['roles_bytes'].update(caller=float(p['roles_bytes']['caller'])),
            lambda p: p['roles_mib'].update(solver=1),
        )
        for mutate in mutations:
            profile = factory()
            mutate(profile)
            with self.subTest(factory=factory.__name__, profile=profile), patch.object(budget, '_admission_directory') as directory:
                with self.assertRaisesRegex(budget.ResourceBudgetError, 'RESOURCE_POLICY_INVALID'):
                    with budget.admission(profile):
                        self.fail('modified profile admitted')
                directory.assert_not_called()
        marked_git = {**budget.memory_policy(), 'workload': 'BOOLEAN_ANALYSIS'}
        unmarked = {key: value for key, value in factory().items() if key != 'workload'}
        malformed = (None, [], {}, {'total_mib': 512}, marked_git)
        if 'solver' in unmarked['roles_mib']:
            malformed += (unmarked,)
        for profile in malformed:
            with self.subTest(profile=profile):
                with self.assertRaisesRegex(budget.ResourceBudgetError, 'RESOURCE_POLICY_INVALID'):
                    with budget.admission(profile):
                        self.fail('unknown profile admitted')

    def test_admission_uses_canonical_snapshot_after_validation(self):
        for factory in (budget.memory_policy, budget.logic_memory_policy):
            profile = factory()
            pristine = copy.deepcopy(profile)

            def changed_after_validation():
                profile['total_bytes'] = 1
                return 1, {}, {}

            with tempfile.TemporaryDirectory() as root, patch.object(budget, '_admission_directory', return_value=Path(root)/'admission'), patch.object(budget, '_visible_headroom', side_effect=changed_after_validation):
                with self.assertRaisesRegex(budget.ResourceBudgetError, 'RESOURCE_HEADROOM_INSUFFICIENT'):
                    with budget.admission(profile):
                        self.fail('mutable policy bypassed canonical headroom')
            self.assertEqual(pristine, factory())

    def test_limit_validation_never_raises_inherited_hard(self):
        with patch.object(budget.resource, 'getrlimit', return_value=(80, 200)), patch.object(budget.resource, 'setrlimit') as setter:
            self.assertEqual(budget.enforce_address_space(80), (80, 200))
            setter.assert_called_once_with(budget.resource.RLIMIT_AS, (80, 200))
            for values in ((1, 201), (201, None), (True, 100), (0, 100), (100, 90), (1.0, 100)):
                self.assert_code('RESOURCE_LIMIT_INVALID', budget.enforce_address_space, *values)
            setter.assert_called_once_with(budget.resource.RLIMIT_AS, (80, 200))

    def test_kernel_refusal_is_explicit_and_ordinary_helpers_do_not_set_limits(self):
        with patch.object(budget.resource, 'setrlimit', side_effect=OSError('refused')):
            self.assert_code('RESOURCE_LIMIT_FAILED', budget.enforce_address_space, 1)
        with patch.object(budget.resource, 'setrlimit') as setter:
            budget.memory_policy()
            budget.observe_process_memory()
            setter.assert_not_called()

    def test_unsupported_is_explicit(self):
        with patch.object(budget.sys, 'platform', 'win32'):
            self.assert_code('RESOURCE_CONTROL_UNSUPPORTED', budget.enforce_address_space, 1024)

    def test_process_observation_distinguishes_virtual_rss_and_high_water(self):
        with patch.object(budget, 'read_small', return_value='100 20 0 0 0 0 0\n'), patch.object(budget.os, 'sysconf', return_value=4096), patch.object(budget.resource, 'getrusage') as usage, patch.object(budget.resource, 'getrlimit', return_value=(123, 456)):
            usage.return_value.ru_maxrss = 25
            observed = budget.observe_process_memory()
        self.assertEqual(observed['virtual_bytes'], 409600)
        self.assertEqual(observed['rss_bytes'], 81920)
        self.assertEqual(observed['peak_rss_bytes'], 25600)
        self.assertEqual((observed['as_soft_bytes'], observed['as_hard_bytes']), (123, 456))
        self.assertFalse(observed['rss_quota_enforced'])

    def headroom(self, available=2**31, remaining=2**31):
        return patch.multiple(budget.probe_environment,
            memory_observation=lambda: {'status': 'OBSERVED', 'available_bytes': available},
            cgroup_observation=lambda: {'status': 'OBSERVED_VISIBLE_SCOPE', 'memory_limits': [{'limit_bytes': 3*2**30, 'current_bytes': 3*2**30-remaining if remaining is not None else None, 'sampled_headroom_bytes': remaining}], 'limit_states': [{'memory': 'FINITE'}]})

    def test_admission_private_nonblocking_and_release(self):
        with tempfile.TemporaryDirectory() as root, patch.object(budget, '_admission_directory', return_value=Path(root)/'admission'), self.headroom():
            with budget.admission(budget.memory_policy()) as (fd, observation):
                self.assertFalse(os.get_inheritable(fd))
                self.assertEqual(os.stat(Path(root)/'admission').st_mode & 0o777, 0o700)
                self.assertEqual(os.fstat(fd).st_mode & 0o777, 0o600)
                self.assertEqual(observation['required_headroom_bytes'], 1024*1024*1024)
                self.assertEqual(observation['headroom_observed_bytes'], 2**31)
                self.assertEqual(observation['scope'], 'VISIBLE_KERNEL_AND_CGROUP_PARTIAL')
                with self.assertRaisesRegex(budget.ResourceBudgetError, 'RESOURCE_BUSY'):
                    with budget.admission(budget.memory_policy()):
                        self.fail('second admission')
            with budget.admission(budget.memory_policy()):
                pass

    def test_unknown_or_low_headroom_blocks(self):
        for available, remaining, expected in ((None, 2**31, 'RESOURCE_HEADROOM_UNKNOWN'), (2**31, None, 'RESOURCE_HEADROOM_UNKNOWN'), (2**31, 10, 'RESOURCE_HEADROOM_INSUFFICIENT')):
            with tempfile.TemporaryDirectory() as root, patch.object(budget, '_admission_directory', return_value=Path(root)/'admission'), self.headroom(available, remaining):
                with self.assertRaisesRegex(budget.ResourceBudgetError, expected):
                    with budget.admission(budget.memory_policy()):
                        self.fail('unadmitted')

    def test_inherited_descriptor_holds_lease_until_child_exits(self):
        child = None
        with tempfile.TemporaryDirectory() as root, patch.object(budget, '_admission_directory', return_value=Path(root)/'admission'), self.headroom():
            try:
                with budget.admission(budget.memory_policy()) as (fd, _):
                    source = "import os,sys; os.fstat(int(sys.argv[1])); print('READY',flush=True); sys.stdin.read(1)"
                    child = subprocess.Popen([sys.executable, '-B', '-c', source, str(fd)],
                                             pass_fds=(fd,), stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    self.assertTrue(select.select([child.stdout], [], [], 2)[0], 'child readiness timeout')
                    self.assertEqual(child.stdout.readline().strip(), 'READY')
                with self.assertRaisesRegex(budget.ResourceBudgetError, 'RESOURCE_BUSY'):
                    with budget.admission(budget.memory_policy()):
                        self.fail('inherited lease released too soon')
                child.communicate('x', timeout=3)
                self.assertEqual(child.returncode, 0)
                with budget.admission(budget.memory_policy()):
                    pass
            finally:
                if child is not None:
                    if child.poll() is None:
                        child.kill()
                    child.communicate(timeout=3)

    def test_partial_cgroup_rows_block_and_unlimited_visible_scope_is_distinct(self):
        with tempfile.TemporaryDirectory() as root, patch.object(budget, '_admission_directory', return_value=Path(root)/'admission'), self.headroom():
            for state in ('UNKNOWN', 'MALFORMED', 'FINITE'):
                with patch.object(budget.probe_environment, 'cgroup_observation', return_value={
                        'status': 'OBSERVED_VISIBLE_SCOPE', 'memory_limits': [], 'limit_states': [{'memory': state}]}):
                    with self.assertRaisesRegex(budget.ResourceBudgetError, 'RESOURCE_HEADROOM_UNKNOWN'):
                        with budget.admission(budget.memory_policy()):
                            self.fail('incomplete cgroup observation')
            with patch.object(budget.probe_environment, 'cgroup_observation', return_value={
                    'status': 'OBSERVED_VISIBLE_SCOPE', 'memory_limits': [], 'limit_states': [{'memory': 'UNLIMITED_VISIBLE_SCOPE'}]}):
                with budget.admission(budget.memory_policy()) as (_, observation):
                    self.assertEqual(observation['headroom_observed_bytes'], 2**31)

    def test_unsafe_lock_and_directory_are_rejected(self):
        for unsafe in ('directory_mode', 'lock_symlink', 'lock_hardlink', 'lock_mode'):
            with tempfile.TemporaryDirectory() as root, patch.object(budget, '_admission_directory', return_value=Path(root)/'admission'), self.headroom():
                directory = Path(root)/'admission'
                directory.mkdir(mode=0o700)
                lock = directory/'active.lock'
                if unsafe == 'directory_mode':
                    directory.chmod(0o755)
                elif unsafe == 'lock_symlink':
                    lock.symlink_to(Path(root)/'target')
                else:
                    lock.touch(mode=0o600)
                    if unsafe == 'lock_hardlink':
                        os.link(lock, directory/'alias')
                    else:
                        lock.chmod(0o644)
                with self.assertRaisesRegex(budget.ResourceBudgetError, 'RESOURCE_ADMISSION_UNSAFE'):
                    with budget.admission(budget.memory_policy()):
                        self.fail('unsafe admission')

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux RLIMIT_AS')
    def test_small_real_limit_in_child_only(self):
        source = '''import os, sys
sys.path.insert(0, sys.argv[1])
from memory_budget import enforce_address_space
with open('/proc/self/statm') as stream:
    virtual = int(stream.read().split()[0]) * os.sysconf('SC_PAGE_SIZE')
enforce_address_space(virtual + 4*1024*1024)
try:
    bytearray(8*1024*1024)
except MemoryError:
    print('BOUNDED_ALLOCATION_REJECTED')
else:
    raise SystemExit(1)
'''
        completed = subprocess.run([sys.executable, '-B', '-c', source, str(SCRIPTS)], capture_output=True, text=True, timeout=3)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), 'BOUNDED_ALLOCATION_REJECTED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
