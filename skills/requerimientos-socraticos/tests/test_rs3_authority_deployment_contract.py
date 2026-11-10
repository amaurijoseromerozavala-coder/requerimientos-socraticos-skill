"""Negative contract checks for portable, non-authorizing D05 deployment."""

import copy
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'assets' / 'rs3-authority-deployment.json'
REFERENCE = ROOT / 'references' / 'authority-deployment.md'
SKILL = ROOT / 'SKILL.md'

CORE_GATES = {
    'DISTINCT_GUARDIAN_UID', 'AGENT_CANNOT_READ_OR_WRITE_GUARDIAN_STORE',
    'AGENT_CANNOT_ELEVATE_OR_CONTROL_GUARDIAN',
    'TRUSTED_HUMAN_UI_ORIGIN', 'EXACT_DECISION_BINDING',
    'ONE_TIME_CODE_CONSUMPTION', 'INDEPENDENT_GUARDIAN_RECEIPT',
    'PRIVATE_GIT_WRITER_BOUNDARY', 'REVOCATION_AND_RECOVERY',
    'TRUSTED_CLOCK_AND_EXPIRY', 'NONCE_REPLAY_GUARD',
    'GUARDIAN_RECOMPUTES_CHALLENGE', 'AGENT_CANNOT_CONTROL_HUMAN_UI_OR_SESSION',
    'AGENT_CANNOT_ACCESS_RECEIPT_KEY',
}
RUNTIME_GATES = {
    'SOURCE_COMMIT_VERIFIED', 'PYTHON_ABI_AND_ARCH_COMPATIBLE',
    'TRANSITIVE_DEPENDENCIES_HASH_LOCKED', 'TOOL_VERSIONS_VERIFIED',
    'CLEAN_RUNTIME_RECONSTRUCTED', 'HOST_RESOURCE_ADMISSION',
    'HOST_SECURITY_BOUNDARY_RECHECK',
}


def assert_fail_closed(testcase, doc):
    testcase.assertEqual(doc['schema'], 'rs3-authority-deployment/v1')
    testcase.assertEqual(doc['selected_target'], 'POSIX_SPLIT_UID_LINUX_WSL')
    testcase.assertEqual(doc['runtime_enforcement'], 'NOT_IMPLEMENTED')
    testcase.assertEqual(doc['authority_verification'], 'NOT_ESTABLISHED')
    testcase.assertIs(doc['execution_authorized'], False)
    testcase.assertEqual(set(doc['profiles']), {
        'POSIX_SPLIT_UID_LINUX_WSL', 'SINGLE_UID', 'MANAGED_CLOUD',
        'WINDOWS_ACL', 'UNKNOWN'})
    for profile in doc['profiles'].values():
        testcase.assertIs(profile['execution_authorized'], False)
        testcase.assertNotIn(profile['status'], ('READY', 'HUMAN_CONFIRMED'))
    posix = doc['profiles']['POSIX_SPLIT_UID_LINUX_WSL']
    testcase.assertEqual(posix['status'], 'TARGET_UNVERIFIED')
    testcase.assertTrue(CORE_GATES.issubset(set(posix['required_evidence'])))
    testcase.assertTrue({'WSL_INTEROP_NEGATIVE_TEST',
                         'WINDOWS_HOST_CONTROL_ASSESSMENT'}.issubset(
                             set(posix['wsl_additional_evidence'])))
    for key in ('SINGLE_UID', 'UNKNOWN'):
        testcase.assertEqual(doc['profiles'][key]['status'], 'BLOCKED')
    testcase.assertEqual(doc['profiles']['MANAGED_CLOUD']['status'],
                         'TARGET_UNVERIFIED')
    testcase.assertEqual(doc['observed_current_cloud']['status'], 'BLOCKED')
    runtime = doc['runtime_replication']
    testcase.assertEqual(runtime['status'], 'NOT_ESTABLISHED')
    testcase.assertTrue(RUNTIME_GATES.issubset(set(runtime['required_evidence'])))


class AuthorityDeploymentContractTests(unittest.TestCase):
    def test_contract_is_fail_closed_and_portable(self):
        doc = json.loads(CONTRACT.read_text(encoding='utf-8'))
        assert_fail_closed(self, doc)

    def test_mutations_that_launder_authority_are_rejected(self):
        doc = json.loads(CONTRACT.read_text(encoding='utf-8'))
        changes = [
            ('global_authority', lambda p: p.update(execution_authorized=True)),
            ('single_uid_ready', lambda p: p['profiles']['SINGLE_UID'].update(status='READY')),
            ('missing_wsl_falsifier', lambda p: p['profiles']['POSIX_SPLIT_UID_LINUX_WSL']
             ['wsl_additional_evidence'].remove('WSL_INTEROP_NEGATIVE_TEST')),
            ('missing_receipt', lambda p: p['profiles']['POSIX_SPLIT_UID_LINUX_WSL']
             ['required_evidence'].remove('INDEPENDENT_GUARDIAN_RECEIPT')),
            ('missing_clock', lambda p: p['profiles']['POSIX_SPLIT_UID_LINUX_WSL']
             ['required_evidence'].remove('TRUSTED_CLOCK_AND_EXPIRY')),
            ('missing_ui_control', lambda p: p['profiles']['POSIX_SPLIT_UID_LINUX_WSL']
             ['required_evidence'].remove('AGENT_CANNOT_CONTROL_HUMAN_UI_OR_SESSION')),
            ('runtime_ready', lambda p: p['runtime_replication'].update(status='READY')),
        ]
        for name, mutation in changes:
            with self.subTest(name=name):
                forged = copy.deepcopy(doc)
                mutation(forged)
                with self.assertRaises(AssertionError):
                    assert_fail_closed(self, forged)

    def test_skill_links_deployment_and_distinguishes_activation(self):
        skill = SKILL.read_text(encoding='utf-8')
        reference = REFERENCE.read_text(encoding='utf-8')
        self.assertIn('references/authority-deployment.md', skill)
        self.assertIn('requirements activate', reference)
        self.assertIn('no establece D05', reference)
        self.assertIn('Git', reference)
        self.assertIn('UI', reference)


if __name__ == '__main__':
    unittest.main()
