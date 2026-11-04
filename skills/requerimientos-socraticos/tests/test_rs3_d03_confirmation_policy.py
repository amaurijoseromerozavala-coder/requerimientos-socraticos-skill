"""Contract controls for the maintainer's D03 design choice."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
DECISION = ROOT / 'docs/design/rs3/authority-boundary-decision.json'
ADR = ROOT / 'docs/design/rs3/ADR-001-local-authority.md'
README = ROOT / 'README.md'


class D03ConfirmationPolicyTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(DECISION.read_text(encoding='utf-8'))

    def test_every_confirmation_is_ratified_but_not_enabled(self):
        self.assertEqual(self.doc['d03']['choice'], 'EVERY_CONFIRMATION')
        self.assertEqual(self.doc['d03']['decision_status'], 'HUMAN_DECIDED_DESIGN')
        self.assertNotIn('RS3-D03', self.doc['pending_decisions'])
        self.assertIs(self.doc['human_confirmation_enabled'], False)
        self.assertEqual(self.doc['real_authority_gate'], 'SECURITY_BOUNDARY_UNMET')

    def test_confirmation_categories_and_unknowns_fail_closed(self):
        scope = self.doc['d03']['confirmation_scope']
        for kind in ('SEMANTIC_ACCEPTANCE', 'EXCEPTION_ACCEPTANCE',
                     'OPERATION_AUTHORIZATION'):
            self.assertEqual(scope[kind], 'FRESH_PBKDF2_BOUND_TO_EXACT_DECISION')
        self.assertEqual(scope['UNMAPPED'], 'BLOCK')
        self.assertEqual(scope['PROPOSAL_OR_CLARIFICATION'], 'NO_CONFIRMATION')
        self.assertEqual(self.doc['d03']['session_reuse'], 'FORBIDDEN')
        self.assertEqual(self.doc['d03']['operation_gate'], 'SEPARATE_FROM_SEMANTIC_GATE')

    def test_adr_preserves_target_verification_gap(self):
        adr = ADR.read_text(encoding='utf-8')
        self.assertIn('D03', adr)
        self.assertIn('cada confirmación', adr)
        self.assertIn('D05', adr)
        self.assertIn('SECURITY_BOUNDARY_UNMET', adr)

    def test_public_summary_does_not_mark_d03_undecided(self):
        readme = README.read_text(encoding='utf-8')
        self.assertIn('D03 exige contraseña para cada confirmación', readme)
        self.assertNotIn('resolver D03', readme)


if __name__ == '__main__':
    unittest.main()
