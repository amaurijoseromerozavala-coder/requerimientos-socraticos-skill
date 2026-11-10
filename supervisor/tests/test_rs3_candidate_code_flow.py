"""Falsifiers for the non-authoritative candidate-to-coordinate link."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from supervisor.rs3_candidate_code_flow import CandidateCodeFlow, CandidateFlowBlocked
from supervisor.rs3_coordinate_ledger import CoordinateLedger, LedgerBlocked
from supervisor.rs3_printed_code_challenge import build_presentation
from supervisor.rs3_printed_code_verifier import PrintedCodeVerifier


class CandidateCodeFlowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / 'ledger'
        CoordinateLedger.initialize(self.root, card_id='CARD-1',
                                    coordinates=['A1', 'A2'])
        self.codes = {'A1': 'a' * 32, 'A2': 'b' * 32}
        PrintedCodeVerifier.initialize(self.root, self.codes)
        self.options = [{'id': 'YES', 'type': 'OPTION', 'text': 'Acepto'},
                        {'id': 'ALT', 'type': 'OPTION', 'text': 'Acepto'}]
        self.presentation = build_presentation('¿Aceptas?', self.options,
                                               ui_version='rs3-ui/v1')
        self.metadata = {'proposal_sha256': 'a' * 64,
                         'snapshot_sha256': 'b' * 64,
                         'confirmation_kind': 'SEMANTIC_ACCEPTANCE',
                         'nonce': '1' * 32, 'audience': 'local-human',
                         'policy_sha256': 'c' * 64, 'card_id': 'CARD-1',
                         'coordinate': 'A1', 'expiry': 2_000_000_000}
        self.flow = CandidateCodeFlow(self.root)

    def test_exact_candidate_reserves_then_spends_without_authority(self):
        pending = self.flow.reserve(self.presentation, 'YES', **self.metadata)
        self.assertEqual(pending['state'], 'PENDING')
        self.assertEqual(pending['challenge']['status'], 'PROPOSED_UNAUTHENTICATED')
        digest = pending['challenge']['challenge_sha256']
        self.assertEqual(CoordinateLedger(self.root).snapshot()['coordinates']['A1']
                         ['challenge_sha256'], digest)
        spent = self.flow.check_and_spend(self.presentation, 'YES',
                                          self.codes['A1'], **self.metadata)
        self.assertEqual(spent['state'], 'SPENT')
        self.assertIs(spent['code_match'], True)
        self.assertEqual(spent['challenge_sha256'], digest)
        self.assertEqual(spent['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(spent['execution_authorized'], False)
        self.assertNotIn('receipt', spent)
        self.assertNotIn(self.codes['A1'], str(spent))
        with self.assertRaises(CandidateFlowBlocked):
            self.flow.check_and_spend(self.presentation, 'YES', self.codes['A1'],
                                      **self.metadata)

    def test_changed_candidate_cannot_spend_reserved_coordinate(self):
        self.flow.reserve(self.presentation, 'YES', **self.metadata)
        changed_presentation = build_presentation('¿Aceptas ahora?', self.options,
                                                  ui_version='rs3-ui/v1')
        reordered = build_presentation('¿Aceptas?', self.options[::-1],
                                       ui_version='rs3-ui/v1')
        variants = [(changed_presentation, 'YES', self.metadata),
                    (reordered, 'YES', self.metadata),
                    (self.presentation, 'ALT', self.metadata)]
        for key, value in [('confirmation_kind', 'EXCEPTION_ACCEPTANCE'),
                           ('proposal_sha256', 'f' * 64),
                           ('snapshot_sha256', 'd' * 64),
                           ('audience', 'other-human'),
                           ('policy_sha256', 'e' * 64),
                           ('nonce', '2' * 32),
                           ('expiry', 2_000_000_001)]:
            variants.append((self.presentation, 'YES',
                             {**self.metadata, key: value}))
        for presentation, option, metadata in variants:
            with self.subTest(option=option, metadata=metadata):
                with self.assertRaises(CandidateFlowBlocked):
                    self.flow.check_and_spend(presentation, option,
                                              self.codes['A1'], **metadata)
                self.assertEqual(CoordinateLedger(self.root).snapshot()
                                 ['coordinates']['A1']['state'], 'PENDING')

    def test_wrong_card_coordinate_and_free_digest_block(self):
        for change in ({'card_id': 'CARD-2'}, {'coordinate': 'Z9'},
                       {'challenge_sha256': '0' * 64}):
            with self.subTest(change=change):
                with self.assertRaises(CandidateFlowBlocked):
                    self.flow.reserve(self.presentation, 'YES',
                                      **{**self.metadata, **change})
        self.assertEqual(CoordinateLedger(self.root).snapshot()
                         ['coordinates']['A1']['state'], 'AVAILABLE')

    def test_unreserved_and_uncertain_stage_block_without_code_match(self):
        with self.assertRaises(CandidateFlowBlocked):
            self.flow.check_and_spend(self.presentation, 'YES', self.codes['A1'],
                                      **self.metadata)
        self.flow.reserve(self.presentation, 'YES', **self.metadata)
        stage = self.root / 'state.stage'
        stage.write_text('unfinished')
        stage.chmod(0o600)
        with self.assertRaises(CandidateFlowBlocked):
            self.flow.check_and_spend(self.presentation, 'YES', self.codes['A1'],
                                      **self.metadata)
        self.assertEqual((self.root / 'verifiers.json').stat().st_mode & 0o777,
                         0o600)

    def test_missing_or_unconfirmed_verifier_blocks_before_reservation(self):
        verifier = self.root / 'verifiers.json'
        original = verifier.read_bytes()
        verifier.unlink()
        with self.assertRaises(CandidateFlowBlocked):
            self.flow.reserve(self.presentation, 'YES', **self.metadata)
        self.assertEqual(CoordinateLedger(self.root).snapshot()
                         ['coordinates']['A1']['state'], 'AVAILABLE')
        verifier.write_bytes(original)
        verifier.chmod(0o600)
        marker = self.root / 'provision.pending'
        marker.touch(mode=0o600)
        with self.assertRaises(CandidateFlowBlocked):
            self.flow.reserve(self.presentation, 'YES', **self.metadata)
        marker.unlink()
        verifier.write_bytes(b'{}\n')
        with self.assertRaises(CandidateFlowBlocked):
            self.flow.reserve(self.presentation, 'YES', **self.metadata)
        self.assertEqual(CoordinateLedger(self.root).snapshot()
                         ['coordinates']['A1']['state'], 'AVAILABLE')

    def test_forged_manifest_and_failed_spend_block(self):
        forged = {**self.presentation, 'question': 'Otra pregunta'}
        with self.assertRaises(CandidateFlowBlocked):
            self.flow.reserve(forged, 'YES', **self.metadata)
        self.flow.reserve(self.presentation, 'YES', **self.metadata)
        with mock.patch.object(CoordinateLedger, 'spend_pending',
                               side_effect=LedgerBlocked('synthetic')):
            with self.assertRaises(CandidateFlowBlocked):
                self.flow.check_and_spend(self.presentation, 'YES',
                                          self.codes['A1'], **self.metadata)
        self.assertEqual(CoordinateLedger(self.root).snapshot()
                         ['coordinates']['A1']['state'], 'PENDING')

    def test_same_uid_mutation_after_preflight_blocks_match(self):
        original = PrintedCodeVerifier.require_ready

        def remove_after_ready(verifier, card_id, coordinate):
            original(verifier, card_id, coordinate)
            (self.root / 'verifiers.json').unlink()

        with mock.patch.object(PrintedCodeVerifier, 'require_ready',
                               new=remove_after_ready):
            self.flow.reserve(self.presentation, 'YES', **self.metadata)
        with self.assertRaises(CandidateFlowBlocked):
            self.flow.check_and_spend(self.presentation, 'YES',
                                      self.codes['A1'], **self.metadata)
        self.assertEqual(CoordinateLedger(self.root).snapshot()
                         ['coordinates']['A1']['state'], 'PENDING')

    def test_contract_records_non_authoritative_integration(self):
        contract_path = (Path(__file__).resolve().parents[2] /
                         'docs/design/rs3/authority-portability-contract.json')
        contract = json.loads(contract_path.read_text())
        profile = contract['profiles']['PRINTED_COORDINATES']
        self.assertEqual(profile['candidate_reservation_binding'],
                         'IMPLEMENTED_NON_AUTHORITATIVE')
        self.assertEqual(profile['runtime_enforcement'], 'NOT_IMPLEMENTED')
        self.assertEqual(contract['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(contract['execution_authorized'], False)


if __name__ == '__main__':
    unittest.main()
