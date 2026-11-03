"""D01/D02: a model-level documentary gate never grants deployment authority."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from documentary_eligibility import InvalidDossier, evaluate_dossier


def dossier():
    return {'schema_version': 'rs3-documentary-v1', 'snapshot_id': 'revision-7',
            'inventory_status': 'DECLARED_COMPLETE', 'critical_gaps': [],
            'requirements': [
                {'id': 'RF-1', 'applicability': 'APPLICABLE',
                 'applicability_basis': 'scope: module A', 'assessment': 'SUPPORTED',
                 'evidence': {'status': 'CURRENT', 'snapshot_id': 'revision-7',
                              'reference': 'evidence/RF-1'}},
                {'id': 'RNF-1', 'applicability': 'APPLICABLE',
                 'applicability_basis': 'scope: module A', 'assessment': 'SUPPORTED',
                 'evidence': {'status': 'CURRENT', 'snapshot_id': 'revision-7',
                              'reference': 'evidence/RNF-1'}}]}


class DocumentaryEligibilityTests(unittest.TestCase):
    def test_all_applicable_supported_and_current_is_only_model_eligible(self):
        result = evaluate_dossier(dossier())
        self.assertEqual(result['production_ready']['meaning'],
                         'ELIGIBLE_FOR_DOCUMENTARY_REVIEW_ONLY')
        self.assertEqual(result['production_ready']['model_status'], 'MODEL_ELIGIBLE')
        self.assertEqual(result['applicable_count'], 2)
        self.assertEqual(result['authority_verification'], 'NOT_PERFORMED')
        self.assertIs(result['deployment_authorized'], False)

    def test_each_material_counterexample_blocks_model_eligibility(self):
        mutations = (
            lambda d: d['requirements'][0].update(assessment='UNSUPPORTED'),
            lambda d: d['requirements'][0]['evidence'].update(status='STALE'),
            lambda d: d['requirements'][0]['evidence'].update(snapshot_id='revision-6'),
            lambda d: d['critical_gaps'].append('GAP-1'),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                item = dossier()
                mutate(item)
                result = evaluate_dossier(item)
                self.assertEqual(result['production_ready']['model_status'], 'NOT_ELIGIBLE')
                self.assertIs(result['deployment_authorized'], False)

    def test_unknown_or_incomplete_never_becomes_success(self):
        mutations = (
            lambda d: d.update(inventory_status='UNKNOWN'),
            lambda d: d['requirements'][0].update(applicability='UNKNOWN'),
            lambda d: d['requirements'][0].update(assessment='UNKNOWN'),
            lambda d: d.update(requirements=[dict(r, applicability='NOT_APPLICABLE',
                                                  assessment='NOT_APPLICABLE',
                                                  evidence={'status': 'NOT_APPLICABLE',
                                                            'snapshot_id': None,
                                                            'reference': None})
                                               for r in d['requirements']]),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                item = dossier()
                mutate(item)
                self.assertEqual(evaluate_dossier(item)['production_ready']['model_status'],
                                 'INCONCLUSIVE')

    def test_nonapplicable_with_basis_does_not_block_applicable_requirements(self):
        item = dossier()
        item['requirements'][1].update(applicability='NOT_APPLICABLE',
                                       assessment='NOT_APPLICABLE',
                                       evidence={'status': 'NOT_APPLICABLE',
                                                 'snapshot_id': None, 'reference': None})
        result = evaluate_dossier(item)
        self.assertEqual(result['production_ready']['model_status'], 'MODEL_ELIGIBLE')
        self.assertEqual(result['applicable_count'], 1)

    def test_duplicate_or_unjustified_exclusion_is_invalid(self):
        item = dossier()
        item['requirements'][1]['id'] = 'RF-1'
        with self.assertRaises(InvalidDossier):
            evaluate_dossier(item)
        item = dossier()
        item['requirements'][1].update(applicability='NOT_APPLICABLE',
                                       applicability_basis='', assessment='NOT_APPLICABLE')
        with self.assertRaises(InvalidDossier):
            evaluate_dossier(item)

    def test_unknown_field_and_unbounded_inventory_are_invalid(self):
        item = dossier()
        item['deployment_authorized'] = True
        with self.assertRaises(InvalidDossier):
            evaluate_dossier(item)
        item = dossier()
        item['requirements'] *= 129
        with self.assertRaises(InvalidDossier):
            evaluate_dossier(item)


if __name__ == '__main__':
    unittest.main()
