"""Small real file/CLI checks; no application commands or load generation."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/validate_report.py'
spec = importlib.util.spec_from_file_location('qa_report_checker', SCRIPT)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)

class ReportChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ctx = {k: hashlib.sha256(k.encode()).hexdigest()
                    for k in ('snapshot', 'environment', 'versions', 'scope', 'criteria')}
        self.source = self.file('source.txt', 'Synthetic requirement and delegation fixture; not human authentication.')
        self.oracle = self.file('oracle.txt', 'Expected fixture output: 2')
        self.artifact = self.file('observed.txt', 'Observed fixture output: 2')
        c = {'id': 'C1', 'kind': 'STATIC', 'oracle': self.oracle,
             'oracle_sequence': 1, 'status': 'PASS', 'evidence_id': 'E1',
             'reason': 'Synthetic result linked to fixture evidence'}
        self.doc = {'schema_version': '0.1.0', 'assessment_id': 'fixture-A',
                    'mode': 'ANALYSIS_ONLY', 'context': self.ctx,
                    'delegation': {'source': self.source, 'status': 'CONFIRMED', 'exceptions_pending': False},
                    'judgment': {'id': 'J1', 'actor_runtime': 'fixture-reviewer',
                                 'assessment_id': 'fixture-A', 'inputs_sha256': '0' * 64,
                                 'context': dict(self.ctx), 'scope': 'SUPPORTED',
                                 'materiality': 'SUPPORTED', 'sufficiency': 'SUPPORTED',
                                 'criteria_sequence': 0, 'judgment_sequence': 3,
                                 'rationale': 'Synthetic fixture only'},
                    'inventory': [{'id': 'O1', 'component': 'fixture', 'applicability': 'APPLICABLE',
                                   'materiality': 'REQUIRED', 'rationale': 'Fixture requirement',
                                   'source_refs': [self.source], 'cases': [c]}],
                    'evidence': [{'id': 'E1', 'case_id': 'C1', 'kind': 'STATIC',
                                  'context': dict(self.ctx), 'outcome': 'PASS',
                                  'artifact': self.artifact, 'observed_sequence': 2,
                                  'observation': 'Synthetic observation; not a target-system result'}],
                    'limitations': ['Synthetic fixture, no system-wide conclusion.']}
        self.doc['judgment']['inputs_sha256'] = qa.inputs_digest(self.doc)

    def file(self, name, text):
        raw = text.encode()
        (self.root / name).write_bytes(raw)
        return {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}

    def run_doc(self):
        return qa.validate_report(self.doc, self.root)

    def reject(self, code):
        with self.assertRaisesRegex((ValueError, OSError), code):
            self.run_doc()

    def gap(self):
        r = self.run_doc()
        self.assertEqual(r['proposed_event'], 'RECORD_GAP_OR_STALE')
        self.assertFalse(r['execution_performed'])

    def test_supported_fixture_is_not_system_certificate(self):
        r = self.run_doc()
        self.assertEqual(r['proposed_event'], 'RECORD_CURRENT_SUCCESS')
        self.assertEqual(r['verdict'], 'SUPPORTED_WITHIN_DECLARED_EVIDENCE')
        self.assertFalse(r['execution_performed'])
        self.assertGreaterEqual(len(r['limits']), 4)

    def test_not_run_is_gap(self):
        c = self.doc['inventory'][0]['cases'][0]
        c.update(status='NOT_RUN', evidence_id=None)
        self.doc['evidence'] = []
        self.gap()

    def test_failure_preserves_other_not_run(self):
        self.doc['inventory'][0]['cases'][0]['status'] = 'FAIL'
        self.doc['evidence'][0]['outcome'] = 'FAIL'
        o = copy.deepcopy(self.doc['inventory'][0]); o['id'] = 'O2'
        o['cases'][0].update(id='C2', status='NOT_RUN', evidence_id=None)
        self.doc['inventory'].append(o)
        r = self.run_doc()
        self.assertEqual(r['proposed_event'], 'RECORD_CURRENT_FAILURE')
        self.assertEqual(r['failure_cases'], ['C1'])
        self.assertEqual(r['gaps'], ['O2'])
        self.assertTrue(r['material_gap'])

    def test_unknown_materiality_is_required(self):
        self.doc['inventory'][0]['materiality'] = 'UNKNOWN'; self.gap()

    def test_unknown_applicability_is_required(self):
        self.doc['inventory'][0]['applicability'] = 'UNKNOWN'; self.gap()

    def test_na_cannot_remove_required_obligation(self):
        self.doc['inventory'][0]['applicability'] = 'NOT_APPLICABLE'; self.gap()

    def test_empty_inventory_rejected(self):
        self.doc['inventory'] = []; self.reject('SCHEMA_INVALID')

    def test_optional_only_no_vacuous_success(self):
        self.doc['inventory'][0]['materiality'] = 'OPTIONAL'; self.gap()

    def test_duplicate_obligation_rejected(self):
        self.doc['inventory'].append(copy.deepcopy(self.doc['inventory'][0])); self.reject('DUPLICATE_ID')

    def test_duplicate_case_rejected(self):
        self.doc['inventory'][0]['cases'].append(copy.deepcopy(self.doc['inventory'][0]['cases'][0])); self.reject('DUPLICATE_ID')

    def test_duplicate_evidence_rejected(self):
        self.doc['evidence'].append(copy.deepcopy(self.doc['evidence'][0])); self.reject('DUPLICATE_ID')

    def test_dangling_case_evidence(self):
        self.doc['evidence'][0]['case_id'] = 'missing'; self.reject('CASE_EVIDENCE_MISMATCH')

    def test_orphan_evidence(self):
        e = copy.deepcopy(self.doc['evidence'][0]); e['id'] = 'E2'
        self.doc['evidence'].append(e); self.reject('ORPHAN_EVIDENCE')

    def test_missing_evidence(self):
        self.doc['evidence'] = []; self.reject('MISSING_EVIDENCE')

    def test_contradictory_result(self):
        self.doc['evidence'][0]['outcome'] = 'FAIL'; self.reject('CONTRADICTORY_RESULT')

    def test_static_evidence_not_physical(self):
        self.doc['inventory'][0]['cases'][0]['kind'] = 'PHYSICAL'; self.reject('EVIDENCE_KIND_MISMATCH')

    def test_stale_snapshot(self):
        self.doc['evidence'][0]['context']['snapshot'] = 'a' * 64; self.gap()

    def test_stale_environment(self):
        self.doc['evidence'][0]['context']['environment'] = 'a' * 64; self.gap()

    def test_stale_versions(self):
        self.doc['evidence'][0]['context']['versions'] = 'a' * 64; self.gap()

    def test_changed_criteria(self):
        self.doc['judgment']['context']['criteria'] = 'a' * 64; self.gap()

    def test_criteria_not_prior(self):
        self.doc['judgment']['criteria_sequence'] = 4; self.gap()

    def test_oracle_not_prior(self):
        self.doc['inventory'][0]['cases'][0]['oracle_sequence'] = 4; self.gap()

    def test_exception_pending(self):
        self.doc['delegation']['exceptions_pending'] = True; self.gap()

    def test_no_delegation(self):
        self.doc['delegation']['status'] = 'PENDING'; self.gap()

    def test_unjustified_scope(self):
        self.doc['judgment']['scope'] = 'PENDING'; self.gap()

    def test_changed_artifact_bytes(self):
        (self.root / 'observed.txt').write_text('different'); self.reject('ARTIFACT_HASH_MISMATCH')

    def test_missing_source(self):
        (self.root / 'source.txt').unlink(); self.reject('No such file')

    def test_outside_path_rejected(self):
        self.doc['evidence'][0]['artifact']['path'] = '../outside'; self.reject('UNSAFE_PATH')

    def test_symlink_rejected(self):
        (self.root / 'link').symlink_to(self.root / 'observed.txt')
        self.doc['evidence'][0]['artifact']['path'] = 'link'; self.reject('Too many levels')

    def test_unexpected_field(self):
        self.doc['automatically_execute'] = True; self.reject('SCHEMA_INVALID')

    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_JSON_KEY'): qa.decode(b'{"a":1,"a":2}')

    def test_nested_json_rejected_before_decoder(self):
        with self.assertRaisesRegex(ValueError, 'depth'): qa.decode(b'[' * 33 + b']' * 33)

    def test_nonfinite_json_rejected(self):
        with self.assertRaisesRegex(ValueError, 'NONFINITE_JSON'): qa.decode(b'{"x":NaN}')

    def test_oversized_json_rejected(self):
        with self.assertRaisesRegex(ValueError, 'maximum bytes'): qa.decode(b' ' * (qa.MAX_BYTES + 1))

    def test_cli_report_and_readonly_behavior(self):
        path = self.root / 'report.json'; path.write_text(json.dumps(self.doc))
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        r = subprocess.run([sys.executable, '-B', str(SCRIPT), '--report', str(path),
                            '--evidence-root', str(self.root)], capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['proposed_event'], 'RECORD_CURRENT_SUCCESS')
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_changed_assessment_requires_new_judgment(self):
        self.doc['assessment_id'] = 'another-assessment'
        self.gap()

    def test_policy_gap_propagates_to_material_gap(self):
        self.doc['judgment']['scope'] = 'PENDING'
        r = self.run_doc()
        self.assertTrue(r['material_gap'])

    def test_not_run_requires_case_reason(self):
        c = self.doc['inventory'][0]['cases'][0]
        c.update(status='NOT_RUN', evidence_id=None)
        c.pop('reason', None)
        self.doc['evidence'] = []
        self.reject('SCHEMA_INVALID')

    def test_changed_artifact_reference_requires_new_judgment(self):
        self.doc['evidence'][0]['artifact'] = self.file('other.txt', 'A different observation')
        self.gap()

    def test_changed_inventory_requires_new_judgment(self):
        self.doc['inventory'][0]['component'] = 'different-component'
        self.gap()

    def test_missing_actor_rejected(self):
        del self.doc['judgment']['actor_runtime']; self.reject('SCHEMA_INVALID')

    def test_digest_is_independent_of_json_key_order(self):
        reordered = dict(reversed(list(self.doc.items())))
        self.assertEqual(qa.inputs_digest(self.doc), qa.inputs_digest(reordered))

    def test_limitations_change_invalidates_judgment(self):
        self.doc['limitations'] = ['Changed scope limitation']
        self.gap()

    def test_schema_version_is_bound(self):
        before = qa.inputs_digest(self.doc)
        self.doc['schema_version'] = 'future-version'
        self.assertNotEqual(before, qa.inputs_digest(self.doc))
        self.reject('SCHEMA_INVALID')

    def test_success_does_not_authenticate_or_authorize(self):
        self.doc['judgment']['actor_runtime'] = 'another-declared-actor'
        r = self.run_doc()
        self.assertEqual(r['authority_verification'], 'NOT_PERFORMED')
        self.assertIs(r['execution_authorized'], False)

    def test_old_digest_is_not_current(self):
        fields = ('assessment_id', 'mode', 'context', 'delegation', 'inventory', 'evidence')
        raw = json.dumps({k: self.doc[k] for k in fields}, sort_keys=True,
                         separators=(',', ':'), ensure_ascii=False).encode()
        self.doc['judgment']['inputs_sha256'] = hashlib.sha256(raw).hexdigest()
        self.gap()

    def test_cli_structured_rejection(self):
        path = self.root / 'invalid.json'; path.write_text('{"a":1,"a":2}')
        r = subprocess.run([sys.executable, '-B', str(SCRIPT), '--report', str(path),
                            '--evidence-root', str(self.root)], capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(json.loads(r.stdout)['proposed_event'], 'REJECT_INPUT')

if __name__ == '__main__': unittest.main()
