"""Public RS3 decision must not promote an audit log into authentication."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class D04BoundaryTests(unittest.TestCase):
    def test_clarification_preserves_unimplemented_authority(self):
        doc = json.loads((ROOT / 'docs/design/rs3/authority-boundary-decision.json').read_text())
        self.assertEqual(doc['d04']['decision_status'], 'HUMAN_DECIDED_DESIGN')
        self.assertEqual(doc['d04']['requested_function'], 'PASSWORD_VERIFICATION_BOUND_TO_DECISION')
        self.assertEqual(doc['d04']['credential_source'], 'LOCAL_PBKDF2_VERIFIER')
        self.assertEqual(doc['d04']['authentication'],
                         'MANUAL_TTY_ADAPTER_IMPLEMENTED_BOUNDARY_UNVERIFIED')
        self.assertEqual(doc['real_authority_gate'], 'SECURITY_BOUNDARY_UNMET')
        self.assertIs(doc['human_confirmation_enabled'], False)
        self.assertIn('RS3-D04-TRUSTED_INPUT_CHANNEL_VERIFICATION',
                      doc['pending_decisions'])

    def test_public_text_does_not_call_audit_log_an_authenticator(self):
        for path in ('README.md', 'docs/design/rs3/ADR-001-local-authority.md',
                     'skills/requerimientos-socraticos/SKILL.md'):
            with self.subTest(path=path):
                text = (ROOT / path).read_text()
                self.assertIn('D04', text)
                self.assertIn('contraseña', text)
                self.assertIn('PBKDF2', text)


if __name__ == '__main__':
    unittest.main()
