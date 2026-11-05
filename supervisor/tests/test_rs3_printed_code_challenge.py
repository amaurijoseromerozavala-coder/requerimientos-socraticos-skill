"""Falsifiers for non-authoritative printed-code challenge identities."""

import copy
import hashlib
import json
from pathlib import Path
import unittest

from supervisor.rs3_printed_code_challenge import (
    ChallengeBlocked, build_candidate_challenge, build_presentation)


def independent_digest(domain, value):
    payload = json.dumps(value, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=True).encode('ascii')
    return hashlib.sha256(domain.encode('ascii') + b'\n' + payload).hexdigest()


class PrintedCodeChallengeTests(unittest.TestCase):
    def setUp(self):
        self.options = [
            {'id': 'A', 'type': 'OPTION', 'text': 'Acepto'},
            {'id': 'B', 'type': 'OPTION', 'text': 'Acepto'},
        ]
        self.presentation = build_presentation(
            '¿Qué decides?', self.options, ui_version='rs3-ui/v1')
        self.fields = dict(proposal_sha256='a' * 64, snapshot_sha256='b' * 64,
                           confirmation_kind='SEMANTIC_ACCEPTANCE',
                           nonce='1' * 32, audience='local-human',
                           policy_sha256='c' * 64, card_id='CARD-1',
                           coordinate='A1', expiry=2_000_000_000)

    def challenge(self, option='A', **changes):
        return build_candidate_challenge(self.presentation, option,
                                         **{**self.fields, **changes})

    def test_equal_text_distinct_ids_have_distinct_identities(self):
        first, second = self.challenge('A'), self.challenge('B')
        self.assertNotEqual(first['selected_option_sha256'], second['selected_option_sha256'])
        self.assertNotEqual(first['canonical_decision_sha256'], second['canonical_decision_sha256'])
        self.assertNotEqual(first['challenge_sha256'], second['challenge_sha256'])
        self.assertEqual(first['selected_option_id'], 'A')
        self.assertEqual(second['selected_option_id'], 'B')

    def test_domain_separated_canonical_bytes_reproduce_digests(self):
        option = self.options[0]
        expected_option = independent_digest('rs3-option/v1', option)
        self.assertEqual(self.challenge()['selected_option_sha256'], expected_option)
        manifest = {key: value for key, value in self.presentation.items()
                    if key != 'presentation_manifest_sha256'}
        self.assertEqual(self.presentation['presentation_manifest_sha256'],
                         independent_digest('rs3-presentation/v1', manifest))
        challenge = self.challenge()
        binding = {key: value for key, value in challenge.items()
                   if key not in ('schema', 'status', 'challenge_sha256',
                                  'authority_verification', 'execution_authorized')}
        self.assertEqual(challenge['challenge_sha256'],
                         independent_digest('rs3-challenge/v1', binding))
        contract = json.loads((Path(__file__).resolve().parents[2] /
                               'docs/design/rs3/authority-portability-contract.json').read_text())
        self.assertEqual(set(binding), set(contract['challenge_binding']))

    def test_each_material_change_invalidates_challenge_identity(self):
        original = self.challenge()['challenge_sha256']
        variants = dict(proposal_sha256='d' * 64, snapshot_sha256='e' * 64,
                        confirmation_kind='EXCEPTION_ACCEPTANCE',
                        nonce='2' * 32, audience='other-human',
                        policy_sha256='f' * 64, card_id='CARD-2',
                        coordinate='B2', expiry=2_000_000_001)
        for field, value in variants.items():
            with self.subTest(field=field):
                self.assertNotEqual(self.challenge(**{field: value})['challenge_sha256'],
                                    original)
        changed_question = build_presentation('¿Qué decides ahora?', self.options,
                                              ui_version='rs3-ui/v1')
        changed_order = build_presentation('¿Qué decides?', self.options[::-1],
                                           ui_version='rs3-ui/v1')
        for manifest in (changed_question, changed_order):
            self.assertNotEqual(build_candidate_challenge(manifest, 'A', **self.fields)
                                ['challenge_sha256'], original)

    def test_rejects_ambiguous_or_untrusted_fields(self):
        with self.assertRaises(ChallengeBlocked):
            build_presentation('Pregunta', [self.options[0], self.options[0]],
                               ui_version='rs3-ui/v1')
        with self.assertRaises(ChallengeBlocked):
            build_presentation('Pregunta', [{**self.options[0], 'prompt': 'hidden'}],
                               ui_version='rs3-ui/v1')
        with self.assertRaises(ChallengeBlocked):
            build_presentation('Pregunta\u202e', self.options, ui_version='rs3-ui/v1')
        with self.assertRaises(ChallengeBlocked):
            self.challenge('missing')
        with self.assertRaises(ChallengeBlocked):
            self.challenge('A', selected_option_sha256='0' * 64)
        with self.assertRaises(ChallengeBlocked):
            self.challenge('A', code='synthetic-secret-do-not-log')
        with self.assertRaises(ChallengeBlocked):
            self.challenge('A', confirmation_kind=[])
        with self.assertRaises(ChallengeBlocked):
            build_presentation('Q' * 8193, self.options, ui_version='rs3-ui/v1')
        forged = copy.deepcopy(self.presentation)
        forged['question'] = 'Otra pregunta'
        with self.assertRaises(ChallengeBlocked):
            build_candidate_challenge(forged, 'A', **self.fields)

    def test_result_cannot_claim_confirmation_or_execution(self):
        result = self.challenge()
        self.assertEqual(result['status'], 'PROPOSED_UNAUTHENTICATED')
        self.assertEqual(result['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(result['execution_authorized'], False)
        self.assertNotIn('credential_match', result)
        self.assertNotIn('receipt', result)


if __name__ == '__main__':
    unittest.main()
