"""Real analyzer output reaches the read-only view without manual extraction."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
ANALYZER = SCRIPTS / 'analyze_logic.py'
VIEW = SCRIPTS / 'render_gap_questions.py'


class AnalysisToViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix='analysis-to-view-')
        root = Path(cls.workspace.name)
        model = {'inputs': ['A'], 'outputs': ['P'], 'domain': True,
                 'rules': [{'id': 'inactive', 'guard': False,
                            'response': {'var': 'P'}}], 'properties': []}
        raw = json.dumps(model, sort_keys=True).encode()
        model_path = root / 'model.json'
        model_path.write_bytes(raw)
        source = 'Definición propuesta de A'
        glossary = {'schema_version': 'rs3-gap-glossary/v1',
                    'model_sha256': hashlib.sha256(raw).hexdigest(),
                    'variables': {'A': {
                        'when_true': 'A presente',
                        'when_false': '<script>falso</script> & A ausente',
                        'source_ref': 'synthetic/A', 'source_text': source,
                        'source_sha256': hashlib.sha256(source.encode()).hexdigest()}}}
        mapping = root / 'glossary.json'
        mapping.write_text(json.dumps(glossary), encoding='utf-8')
        run = subprocess.run([sys.executable, str(ANALYZER), str(model_path),
                              '--glossary', str(mapping), '--gap-samples', '1'],
                             capture_output=True, text=True, timeout=20)
        if run.returncode != 0:
            cls.workspace.cleanup()
            raise AssertionError('ANALYZER_FIXTURE_FAILED: ' + run.stderr[:200])
        cls.report = json.loads(run.stdout)
        cls.report_path = root / 'report.json'
        cls.report_path.write_text(json.dumps(cls.report), encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def run_view(self, report, *, stdin=False):
        if stdin:
            return subprocess.run([sys.executable, str(VIEW), '--report', '-'],
                                  input=json.dumps(report), capture_output=True,
                                  text=True, timeout=10)
        self.report_path.write_text(json.dumps(report), encoding='utf-8')
        return subprocess.run([sys.executable, str(VIEW), '--report',
                               str(self.report_path)], capture_output=True,
                              text=True, timeout=10)

    def test_real_report_renders_from_file_and_bounded_stdin(self):
        self.assertEqual(self.report['gap_questions']['status'],
                         'PROPOSED_UNVERIFIED')
        for stdin in (False, True):
            with self.subTest(stdin=stdin):
                run = self.run_view(self.report, stdin=stdin)
                self.assertEqual(run.returncode, 0)
                self.assertIn('&lt;script&gt;falso&lt;/script&gt;', run.stdout)
                self.assertNotIn('<script>', run.stdout)

    def test_report_digest_or_assignment_mutation_is_rejected(self):
        for mutate in (
            lambda r: r['provenance'].update(model_sha256='0' * 64),
            lambda r: r['gap_questions']['questions'][0][
                'input_assignment'].update(A=True),
            lambda r: r['gap_region']['samples'][0].update(
                witness_recheck='UNVERIFIED'),
        ):
            with self.subTest(mutate=mutate):
                changed = copy.deepcopy(self.report)
                mutate(changed)
                run = self.run_view(changed)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, '')

    def test_report_without_proposed_question_or_invalid_stdin_fails_closed(self):
        changed = copy.deepcopy(self.report)
        changed['gap_questions']['questions'] = []
        run = self.run_view(changed)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, '')
        for raw in ('{invalid', ' ' * (1024 * 1024 + 1)):
            with self.subTest(length=len(raw)):
                run = subprocess.run([sys.executable, str(VIEW), '--report', '-'],
                                     input=raw, capture_output=True, text=True,
                                     timeout=10)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, '')


if __name__ == '__main__':
    unittest.main()
