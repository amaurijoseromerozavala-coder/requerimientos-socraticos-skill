"""A supervised analyzer may propose one question, never a human decision."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import analyze_to_view


class SupervisedQuestionHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='question-handoff-')
        root = Path(self.temp.name)
        model = {'inputs': ['A'], 'outputs': ['P'], 'domain': True,
                 'rules': [{'id': 'inactive', 'guard': False,
                            'response': {'var': 'P'}}], 'properties': []}
        model_bytes = json.dumps(model, sort_keys=True).encode()
        self.model = root / 'model.json'
        self.model.write_bytes(model_bytes)
        source = 'Definición propuesta de A'
        self.glossary_data = {
            'schema_version': 'rs3-gap-glossary/v1',
            'model_sha256': hashlib.sha256(model_bytes).hexdigest(),
            'variables': {'A': {'when_true': 'A presente',
                                'when_false': 'A ausente',
                                'source_ref': 'synthetic/A',
                                'source_text': source,
                                'source_sha256': hashlib.sha256(
                                    source.encode()).hexdigest()}}}
        self.glossary = root / 'glossary.json'
        self.save_glossary()

    def tearDown(self):
        self.temp.cleanup()

    def save_glossary(self):
        self.glossary.write_text(json.dumps(self.glossary_data), encoding='utf-8')

    def cli(self, handoff=True):
        command = [sys.executable, str(SCRIPTS / 'analyze_to_view.py'),
                   str(self.model), '--glossary', str(self.glossary)]
        if handoff:
            command += ['--format', 'question-json']
        return subprocess.run(command, capture_output=True, text=True, timeout=15)

    def test_real_supervised_analysis_yields_one_proposal_and_html_default(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        handoff = json.loads(result.stdout)
        self.assertEqual(handoff['status'], 'PROPOSED_FOR_INTERROGATION')
        self.assertEqual(handoff['question_count'], 1)
        self.assertEqual(handoff['question']['input_assignment'], {'A': False})
        self.assertEqual(handoff['model_sha256'], self.glossary_data['model_sha256'])
        self.assertEqual(handoff['authority'], 'NOT_GRANTED')
        self.assertEqual(handoff['source_authenticity'], 'NOT_ESTABLISHED')
        self.assertFalse(set(handoff) & {'answer', 'decision', 'confirmed',
                                         'execution_authorized'})
        default = self.cli(False)
        self.assertEqual(default.returncode, 0, default.stderr)
        self.assertTrue(default.stdout.startswith('<!doctype html>'))

    def test_question_identity_repeats_and_changes_with_proposed_phrase(self):
        first = json.loads(self.cli().stdout)
        second = json.loads(self.cli().stdout)
        self.assertEqual(first['question_sha256'], second['question_sha256'])
        self.glossary_data['variables']['A']['when_false'] = 'A no está presente'
        self.save_glossary()
        changed = self.cli()
        self.assertEqual(changed.returncode, 0, changed.stderr)
        self.assertNotEqual(first['question_sha256'],
                            json.loads(changed.stdout)['question_sha256'])

    def test_invalid_report_or_uncertain_cleanup_never_produces_handoff(self):
        self.model.write_text('{invalid', encoding='utf-8')
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        observed = {'returncode': 0, 'stdout_bytes': b'{}',
                    'output_limit': False, 'timed_out': False,
                    'cleanup_status': 'INCOMPLETE'}
        with patch.object(analyze_to_view, 'run_supervised', return_value=observed):
            with self.assertRaises(analyze_to_view.PipelineError):
                analyze_to_view.run_pipeline(str(self.model), str(self.glossary),
                                             output_format='question-json')


if __name__ == '__main__':
    unittest.main()
