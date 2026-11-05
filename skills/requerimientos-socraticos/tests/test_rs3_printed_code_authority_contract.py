"""Negative contract tests for the maintainer's printed-code decision."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
DESIGN = ROOT / 'docs/design/rs3'


class PrintedCodeAuthorityContractTests(unittest.TestCase):
    def setUp(self):
        self.boundary = json.loads((DESIGN / 'authority-boundary-decision.json').read_text())
        self.protocol = json.loads((DESIGN / 'authority-portability-contract.json').read_text())
        self.ui = json.loads((DESIGN / 'human-decision-ui-contract.json').read_text())

    def test_ratified_mechanism_does_not_promote_runtime(self):
        self.assertEqual(self.boundary['d03']['choice'], 'EVERY_CONFIRMATION')
        self.assertEqual(self.boundary['d03']['credential_profile'], 'PRINTED_COORDINATES')
        self.assertEqual(self.boundary['d04']['profile_target_status'],
                         'SUPERSEDED_BY_PRINTED_COORDINATES')
        self.assertEqual(self.boundary['choice'], 'SEPARATE_LOCAL_ACCOUNT')
        self.assertEqual(self.protocol['profiles']['PRINTED_COORDINATES']['decision_status'],
                         'RATIFIED_DESIGN_TARGET_UNVERIFIED')
        self.assertEqual(self.protocol['profiles']['LOCAL_PBKDF2']['decision_status'],
                         'SUPERSEDED_NON_AUTHORITATIVE_COMPONENT')
        self.assertEqual(self.boundary['real_authority_gate'], 'SECURITY_BOUNDARY_UNMET')
        self.assertEqual(self.boundary['d03']['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(self.boundary['human_confirmation_enabled'], False)
        self.assertIs(self.protocol['execution_authorized'], False)

    def test_every_confirmation_has_exact_receipt_binding(self):
        self.assertTrue({'selected_option_id', 'selected_option_sha256'} <=
                        set(self.protocol['challenge_binding']))
        fields = set(self.protocol['receipt_binding'])
        self.assertEqual(fields, {
            'protocol_version', 'confirmation_kind', 'proposal_sha256',
            'snapshot_sha256', 'presentation_manifest_sha256',
            'canonical_decision_sha256', 'selected_option_id',
            'selected_option_sha256', 'nonce', 'audience', 'policy_sha256',
            'card_id', 'coordinate', 'expiry', 'challenge_sha256',
        })
        self.assertEqual(self.protocol['selected_option_rule'],
                         'STABLE_ID_AND_TYPED_OPTION_DIGEST; EQUAL_TEXT_DISTINCT_IDS_REMAIN_DISTINCT')
        self.assertEqual(self.protocol['profiles']['PRINTED_COORDINATES']['consumption'],
                         'ATOMIC_ADMISSION_OR_BLOCK')
        self.assertEqual(self.protocol['profiles']['PRINTED_COORDINATES']['replay'], 'BLOCK')
        self.assertEqual(self.protocol['profiles']['PRINTED_COORDINATES']['uncertain_state'],
                         'BLOCK_AND_RECONCILE')

    def test_custom_answer_does_not_spend_code_or_write_authority(self):
        self.assertEqual(self.ui['code_profile'], 'PRINTED_COORDINATES_RATIFIED_NOT_ENABLED')
        self.assertEqual(self.ui['custom_response_authority_receipt'], 'FORBIDDEN')
        for transition in self.ui['transitions']:
            if transition['event'] in ('SUBMIT_CUSTOM', 'SEND_TO_AGENT',
                                       'AGENT_REFORMULATES'):
                self.assertIs(transition['card_code_consumption'], False)
                self.assertIs(transition['authority_git_write'], False)
        self.assertEqual(self.ui['authority_verification'], 'NOT_ESTABLISHED')


if __name__ == '__main__':
    unittest.main()
