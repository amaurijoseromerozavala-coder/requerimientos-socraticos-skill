"""Synthetic caller-source boundary: coherent model edits must still fail."""

from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from local_provider_adapter import LocalProviderAdapter
from source_snapshot import SourceSnapshot
from weak_model_gate import admit_response


def proposal_bytes(**changes):
    item = {'schema_version': '0.1-proposed', 'id': 'RS3-SOURCE-1',
            'source_ref': 'synthetic/human/1', 'source_text': 'P solo si Q',
            'status': 'PROPOSED', 'kind': 'NECESSARY_CONDITION',
            'modality': 'MUST', 'subject': 'P', 'condition': 'Q',
            'direction': 'SUBJECT_IMPLIES_CONDITION',
            'assumptions': [], 'exceptions': [], 'human_confirmation': 'PENDING'}
    item.update(changes)
    return json.dumps(item, separators=(',', ':')).encode('utf-8')


def adapter_for(output, snapshot):
    code = f'import sys;sys.stdout.buffer.write({output!r})'
    return LocalProviderAdapter((sys.executable, '-I', '-B', '-c', code),
                                snapshot, timeout_seconds=.5)


class SourceSnapshotBindingTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = SourceSnapshot('synthetic/human/1', 'P solo si Q')

    def test_exact_source_is_proposed_without_authority(self):
        result = adapter_for(proposal_bytes(), self.snapshot).invoke()
        self.assertEqual(result['admission'], 'PROPOSED_FOR_REVIEW')
        self.assertEqual(result['source_binding'], 'MATCHED_CALLER_SNAPSHOT')
        self.assertIs(result['execution_authorized'], False)
        self.assertNotIn('P solo si Q', str(result))

    def test_coherent_model_reinterpretation_of_source_is_rejected(self):
        changed = proposal_bytes(source_text='P si Q',
                                 kind='SUFFICIENT_CONDITION',
                                 direction='CONDITION_IMPLIES_SUBJECT')
        standalone = admit_response(changed)
        self.assertEqual(standalone['admission'], 'PROPOSED_FOR_REVIEW')
        self.assertEqual(standalone['source_binding'], 'NOT_ASSESSED')
        result = adapter_for(changed, self.snapshot).invoke()
        self.assertEqual((result['admission'], result['reason_code']),
                         ('REJECT_INPUT', 'SOURCE_BINDING_MISMATCH'))
        self.assertIsNone(result['ast'])

    def test_reference_change_is_rejected_even_when_text_matches(self):
        result = adapter_for(proposal_bytes(source_ref='synthetic/human/2'),
                             self.snapshot).invoke()
        self.assertEqual((result['admission'], result['reason_code']),
                         ('REJECT_INPUT', 'SOURCE_BINDING_MISMATCH'))
        self.assertIsNone(result['ast'])

    def test_snapshot_required_bounded_and_immutable(self):
        command = (sys.executable, '-I', '-B', '-c', 'pass')
        with self.assertRaises(ValueError):
            LocalProviderAdapter(command, None)
        with self.assertRaises(ValueError):
            SourceSnapshot('synthetic/human/1', 'X' * 4097)
        with self.assertRaises(FrozenInstanceError):
            self.snapshot.source_text = 'P si Q'


if __name__ == '__main__':
    unittest.main()
