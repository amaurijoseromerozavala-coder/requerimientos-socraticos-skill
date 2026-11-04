"""Negative contract checks for the proposed portable authority boundary."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / 'docs/design/rs3/authority-portability-contract.json'
DECISION = ROOT / 'docs/design/rs3/authority-boundary-decision.json'


class PortableAuthorityContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
        self.decision = json.loads(DECISION.read_text(encoding='utf-8'))

    def test_binding_is_exact_and_unknown_fails_closed(self):
        self.assertEqual(self.contract['status'], 'PROPOSED_DESIGN_NOT_ENFORCED')
        self.assertEqual(set(self.contract['challenge_binding']), {
            'protocol_version', 'confirmation_kind', 'proposal_sha256',
            'snapshot_sha256', 'canonical_decision_sha256', 'nonce',
            'audience', 'policy_sha256', 'expiry',
        })
        self.assertEqual(self.contract['unknown_or_incomplete'], 'BLOCK')
        self.assertEqual(self.contract['replay'], 'BLOCK')
        self.assertEqual(self.contract['agent_supplied_proof'], 'BLOCK')

    def test_no_profile_promotes_to_authority(self):
        self.assertEqual(self.contract['runtime_enforcement'], 'NOT_IMPLEMENTED')
        self.assertEqual(self.contract['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(self.contract['execution_authorized'], False)
        self.assertEqual(self.contract['promotion_rule'],
                         'INDEPENDENT_BOUNDARY_AND_RECEIPT_REQUIRED')
        self.assertEqual(self.contract['operation_gate'], 'SEPARATE')

    def test_ratified_local_profile_and_alternatives_are_distinct(self):
        self.assertEqual(self.decision['choice'], 'SEPARATE_LOCAL_ACCOUNT')
        self.assertEqual(self.decision['d03']['choice'], 'EVERY_CONFIRMATION')
        profiles = self.contract['profiles']
        self.assertEqual(profiles['LOCAL_PBKDF2']['decision_status'],
                         'RATIFIED_DESIGN_TARGET_UNVERIFIED')
        self.assertEqual(profiles['LOCAL_PBKDF2']['required_boundary'],
                         'SEPARATE_LOCAL_ACCOUNT')
        for name in ('TOTP', 'PRINTED_COORDINATES', 'PLATFORM_AUTHENTICATOR'):
            self.assertEqual(profiles[name]['decision_status'], 'OPTION_NOT_ADOPTED')
            self.assertEqual(profiles[name]['runtime_enforcement'], 'NOT_IMPLEMENTED')

    def test_portability_requires_per_environment_evidence(self):
        self.assertEqual(self.contract['target_hardware_verification'], 'NOT_RUN')
        self.assertEqual(self.contract['environment_preflight'],
                         'PROFILE_SPECIFIC_REQUIRED')
        self.assertEqual(self.contract['unsupported_environment'], 'BLOCK')
        self.assertEqual(self.contract['receipt_verification'],
                         'INDEPENDENT_OF_AGENT_REQUIRED')


if __name__ == '__main__':
    unittest.main()
