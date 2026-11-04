"""Contract controls for immutable-by-identity requirement/test revisions."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / 'docs/design/rs3/ratified-oracle-contract.json'


class RatifiedOracleContractTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(CONTRACT.read_text(encoding='utf-8'))

    def test_ratification_requires_human_selection_and_guardian_receipt(self):
        states = self.doc['state_rules']
        self.assertEqual(states['CUSTOM_RESPONSE'], 'PROPOSAL_ONLY')
        self.assertEqual(states['AGENT_PROPOSED_REQUIREMENT'], 'PROPOSAL_ONLY')
        self.assertEqual(states['RATIFIED_REQUIREMENT'],
                         'EXPLICIT_OPTION_AND_GUARDIAN_RECEIPT_REQUIRED')
        self.assertEqual(self.doc['agent_can_issue_ratification'], False)

    def test_per_test_identity_covers_oracle_and_execution_closure(self):
        fields = set(self.doc['sealed_test_manifest_fields'])
        self.assertTrue({
            'requirement_revision_sha256', 'requirement_source_sha256',
            'oracle_spec_sha256', 'test_bytes_sha256', 'test_path',
            'helper_bytes_sha256', 'runner_bytes_sha256',
            'dependency_lock_sha256', 'environment_profile_sha256',
            'source_git_tree_oid', 'guardian_receipt_id',
        } <= fields)
        self.assertEqual(self.doc['digest_algorithm'], 'SHA-256_EXACT_BYTES')
        self.assertEqual(self.doc['git_oid_algorithm'], 'READ_FROM_REPOSITORY')

    def test_change_never_rewrites_existing_seal(self):
        for material in ('TEST_BYTES', 'HELPER_BYTES', 'RUNNER_BYTES',
                         'DEPENDENCY_LOCK', 'ORACLE_SPEC', 'REQUIREMENT_REVISION'):
            self.assertEqual(self.doc['on_sealed_change'][material],
                             'BLOCK_AND_PROPOSE_NEW_RATIFIED_REVISION')
        self.assertEqual(self.doc['prior_revision_retention'], 'PRESERVE')
        self.assertEqual(self.doc['red_gate'], 'SEALED_BEFORE_IMPLEMENTATION')

    def test_local_manifest_does_not_self_authorize(self):
        self.assertEqual(self.doc['authority_source'],
                         'INDEPENDENT_GUARDIAN_RECEIPT_NOT_AGENT_WORKTREE')
        self.assertEqual(self.doc['existing_tests'],
                         'UNRATIFIED_UNTIL_INDIVIDUALLY_REVIEWED')
        self.assertEqual(self.doc['runtime_enforcement'], 'NOT_IMPLEMENTED')
        self.assertEqual(self.doc['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(self.doc['execution_authorized'], False)


if __name__ == '__main__':
    unittest.main()
