"""Bounded observation of declarations, never evidence authentication."""
import contextlib
import copy
import io
import json
import unittest
from unittest.mock import patch
import test_report as fixtures

class ObservationChecks(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ReportChecks()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def invoke(self, doc=None, raw=None):
        path = self.fixture.root / 'report.json'
        path.write_text(raw if raw is not None else json.dumps(doc))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = fixtures.qa.main(['--report', str(path), '--evidence-root', str(self.fixture.root)])
        result = json.loads(output.getvalue())
        self.assertFalse(result['execution_authorized'])
        return code, result

    def test_contradiction_retains_unverified_declaration(self):
        doc = copy.deepcopy(self.fixture.doc)
        doc['evidence'][0]['outcome'] = 'FAIL'
        code, result = self.invoke(doc)
        self.assertEqual(code, 2)
        self.assertEqual(result['proposed_event'], 'REJECT_INPUT')
        self.assertEqual(result['failure_observation']['status'], 'UNVERIFIED_DECLARATIONS_FOUND')
        self.assertEqual(result['failure_observation']['declared_failure_count'], 1)
        self.assertEqual(result['failure_observation']['evidence_verification'], 'NOT_ESTABLISHED')
        self.assertNotIn('failure_cases', result)

    def test_adjacent_missing_reference_preserves_declaration(self):
        doc = copy.deepcopy(self.fixture.doc)
        doc['evidence'][0]['outcome'] = 'FAIL'
        doc['inventory'][0]['cases'][0]['status'] = 'FAIL'
        other = copy.deepcopy(doc['inventory'][0])
        other['id'] = 'O2'; other['materiality'] = 'OPTIONAL'
        other['cases'][0].update(id='C2', evidence_id='missing')
        doc['inventory'].append(other)
        code, result = self.invoke(doc)
        self.assertEqual(code, 2)
        self.assertIn('MISSING_EVIDENCE', result['error'])
        self.assertEqual(result['failure_observation']['declared_failure_count'], 1)

    def test_undecodable_is_not_assessed(self):
        for raw in ('{', '{"evidence": [], "evidence": []}'):
            with self.subTest(raw=raw):
                code, result = self.invoke(raw=raw)
                self.assertEqual(code, 2)
                self.assertEqual(result['failure_observation']['status'], 'NOT_ASSESSED')
                self.assertIsNone(result['failure_observation']['declared_failure_count'])

    def test_only_direct_outcomes_count_without_io(self):
        with patch.object(fixtures.qa, 'read_regular', side_effect=AssertionError('unexpected I/O')):
            obs = fixtures.qa.observe_failure_declarations({'evidence': [
                {'outcome': 'PASS', 'nested': {'outcome': 'FAIL'}},
                {'outcome': 'FAIL', 'artifact': {'path': 'not-read'}}]})
        self.assertEqual(obs['declared_failure_count'], 1)
        self.assertEqual(obs['scan_status'], 'COMPLETE')

    def test_scan_limit_is_partial_not_negative(self):
        obs = fixtures.qa.observe_failure_declarations({'evidence': [{'outcome': 'PASS'}] * 128 + [{'outcome': 'FAIL'}]})
        self.assertEqual(obs['scan_status'], 'PARTIAL')
        self.assertEqual(obs['status'], 'NOT_ASSESSED')
        self.assertEqual(obs['scanned_records'], 128)

    def test_malformed_record_keeps_other_declaration(self):
        obs = fixtures.qa.observe_failure_declarations({'evidence': [None, {'outcome': 'FAIL'}]})
        self.assertEqual(obs['status'], 'UNVERIFIED_DECLARATIONS_FOUND')
        self.assertEqual(obs['scan_status'], 'PARTIAL')

    def test_wrong_container_is_not_assessed(self):
        for doc in (None, [], {}, {'evidence': 'FAIL'}):
            self.assertEqual(fixtures.qa.observe_failure_declarations(doc)['status'], 'NOT_ASSESSED')

    def test_empty_list_is_only_no_declarations(self):
        obs = fixtures.qa.observe_failure_declarations({'evidence': []})
        self.assertEqual(obs['status'], 'NO_DECLARATIONS_FOUND')
        self.assertEqual(obs['evidence_verification'], 'NOT_ESTABLISHED')

if __name__ == '__main__': unittest.main()
