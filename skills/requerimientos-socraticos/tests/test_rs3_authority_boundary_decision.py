"""D05 may specify a future boundary without asserting that it already exists."""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
DECISION = ROOT / 'docs/design/rs3/authority-boundary-decision.json'
ADR = ROOT / 'docs/design/rs3/ADR-001-local-authority.md'


class AuthorityBoundaryDecisionTests(unittest.TestCase):
    def test_separate_account_is_design_choice_not_runtime_claim(self):
        decision = json.loads(DECISION.read_text(encoding='utf-8'))
        self.assertEqual(decision['decision_id'], 'RS3-D05')
        self.assertEqual(decision['choice'], 'SEPARATE_LOCAL_ACCOUNT')
        self.assertEqual(decision['decision_status'], 'HUMAN_DECIDED_DESIGN')
        self.assertEqual(decision['runtime_enforcement'], 'NOT_IMPLEMENTED')
        self.assertEqual(decision['real_authority_gate'], 'SECURITY_BOUNDARY_UNMET')
        self.assertIs(decision['human_confirmation_enabled'], False)
        self.assertEqual(decision['target_hardware_verification'], 'NOT_RUN')

    def test_agent_cannot_be_granted_private_authority_by_record(self):
        decision = json.loads(DECISION.read_text(encoding='utf-8'))
        permissions = decision['agent_permissions']
        self.assertEqual(set(permissions),
                         {'submit_proposal', 'verify_public_receipt',
                          'read_signing_key', 'write_authority_store',
                          'issue_human_confirmation', 'run_as_authority_account'})
        self.assertIs(permissions['submit_proposal'], True)
        self.assertIs(permissions['verify_public_receipt'], True)
        for forbidden in ('read_signing_key', 'write_authority_store',
                          'issue_human_confirmation', 'run_as_authority_account'):
            self.assertIs(permissions[forbidden], False)

    def test_unverified_isolation_cannot_be_described_as_deployed(self):
        decision = json.loads(DECISION.read_text(encoding='utf-8'))
        checks = set(decision['required_target_checks'])
        self.assertTrue({'DISTINCT_UID', 'NO_AGENT_PRIVILEGE_ESCALATION',
                         'KEY_OWNERSHIP_AND_ACCESS', 'STORE_WRITE_ISOLATION',
                         'RECOVERY_AND_REVOCATION'} <= checks)
        adr = ADR.read_text(encoding='utf-8')
        self.assertIn('SECURITY_BOUNDARY_UNMET', adr)
        self.assertIn('D04', adr)
        self.assertIn('D03', adr)


if __name__ == '__main__':
    unittest.main()
