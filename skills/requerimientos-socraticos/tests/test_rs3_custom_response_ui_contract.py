"""Explore the UI FSM for paths that could launder custom prose into authority."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / 'docs/design/rs3/human-decision-ui-contract.json'


class HumanDecisionUIContractTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(CONTRACT.read_text(encoding='utf-8'))
        self.edges = self.doc['transitions']

    def test_custom_response_requires_new_snapshot_before_authority(self):
        stack = [('CUSTOM_RESPONSE', False, False, False)]
        visited = set()
        while stack:
            state, reformulated, new_snapshot, selected = stack.pop()
            key = state, reformulated, new_snapshot, selected
            if key in visited:
                continue
            visited.add(key)
            if state == 'AUTH_RECEIPT':
                self.assertTrue(reformulated and new_snapshot and selected)
                continue
            for edge in self.edges:
                if edge['from'] != state:
                    continue
                event = edge['event']
                stack.append((edge['to'],
                              reformulated or event == 'AGENT_REFORMULATES',
                              new_snapshot or event == 'GUARDIAN_ISSUES_NEW_SNAPSHOT',
                              selected or event == 'SELECT_OPTION'))
        self.assertIn(('AUTH_RECEIPT', True, True, True), visited)

    def test_custom_branch_has_no_code_or_authority_write(self):
        custom_events = {'SUBMIT_CUSTOM', 'SEND_TO_AGENT', 'AGENT_REFORMULATES',
                         'HUMAN_REJECTS_INTERPRETATION'}
        for edge in self.edges:
            if edge['event'] in custom_events:
                self.assertEqual(edge['authority_git_write'], False)
                self.assertEqual(edge['card_code_request'], False)
                self.assertEqual(edge['card_code_consumption'], False)
        self.assertEqual(self.doc['custom_response_storage'],
                         'INTERROGATION_HISTORY_ONLY')
        self.assertEqual(self.doc['custom_response_authority_receipt'], 'FORBIDDEN')

    def test_link_and_visual_evidence_cannot_grant_authority(self):
        self.assertEqual(self.doc['link_issuer'], 'INDEPENDENT_GUARDIAN')
        self.assertEqual(self.doc['agent_link_role'], 'RELAY_ONLY')
        self.assertEqual(self.doc['link_token_authority'], 'NONE')
        self.assertEqual(self.doc['display_requirement'], 'FULL_CANONICAL_TEXT_AND_DIGEST')
        self.assertEqual(self.doc['screenshot_proves_human_viewed'], False)
        self.assertEqual(self.doc['qa_primary_comparison'],
                         'CANONICAL_PRESENTATION_MANIFEST_VS_GIT_RECEIPT')

    def test_no_runtime_promotion(self):
        self.assertEqual(self.doc['state'], 'DESIGN_NOT_IMPLEMENTED')
        self.assertEqual(self.doc['authority_verification'], 'NOT_ESTABLISHED')
        self.assertEqual(self.doc['target_hardware_verification'], 'NOT_RUN')
        self.assertIs(self.doc['execution_authorized'], False)


if __name__ == '__main__':
    unittest.main()
