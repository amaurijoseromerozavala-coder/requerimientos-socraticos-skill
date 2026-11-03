"""Falsify mismatched public RDD provenance without claiming external attestation."""
import copy
import json
from pathlib import Path
import subprocess
import unittest

from ci.check_rdd_record import COMMIT, REWRITTEN_COMMIT, verify_git, verify_structure

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / 'docs/skill-audit/supervisor-pre-reap/RDD-CIERRE.json'
MARKER = ROOT / 'docs/skill-audit/supervisor-pre-reap/terminal-consumption.json'


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(RECORD.read_text(encoding='utf-8'))
        self.marker = json.loads(MARKER.read_text(encoding='utf-8'))

    def test_exact_historical_commit_and_consumed_target(self):
        verify_structure(self.record, self.marker)
        verify_git(ROOT, self.record)

    def test_archived_identity_is_not_in_reachable_public_history(self):
        reachable = set(subprocess.check_output(
            ['git', 'rev-list', '--all'], cwd=ROOT, text=True).splitlines())
        self.assertNotIn(COMMIT, reachable)
        self.assertIn(REWRITTEN_COMMIT, reachable)

    def test_changed_target_or_tree_is_rejected(self):
        for field in ('target_identity', 'candidate_tree', 'commit'):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.record)
                changed[field] = '0' * len(changed[field])
                with self.assertRaises(ValueError):
                    verify_structure(changed, self.marker)

    def test_inflated_review_scope_is_rejected(self):
        changed = copy.deepcopy(self.record)
        changed['reviewer_execution'] = 'INDEPENDENTLY_REPRODUCED'
        with self.assertRaises(ValueError):
            verify_structure(changed, self.marker)

    def test_changed_terminal_marker_is_rejected(self):
        marker = dict(self.marker, lineage='different-lineage')
        with self.assertRaises(ValueError):
            verify_structure(self.record, marker)


if __name__ == '__main__':
    unittest.main()
