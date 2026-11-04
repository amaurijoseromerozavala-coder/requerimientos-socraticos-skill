"""The view must consume only a completed, supervised analyzer process."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import analyze_to_view
from process_supervision import run_supervised as actual_supervision


class SupervisedAnalysisViewTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix='supervised-view-')
        root = Path(self.workspace.name)
        model = {'inputs': ['A'], 'outputs': ['P'], 'domain': True,
                 'rules': [{'id': 'inactive', 'guard': False,
                            'response': {'var': 'P'}}], 'properties': []}
        raw = json.dumps(model, sort_keys=True).encode()
        self.model = root / 'model.json'
        self.model.write_bytes(raw)
        source = 'Definición propuesta de A'
        mapping = {'schema_version': 'rs3-gap-glossary/v1',
                   'model_sha256': hashlib.sha256(raw).hexdigest(),
                   'variables': {'A': {
                       'when_true': 'A presente',
                       'when_false': '<script>falso</script> & A ausente',
                       'source_ref': 'synthetic/A', 'source_text': source,
                       'source_sha256': hashlib.sha256(source.encode()).hexdigest()}}}
        self.glossary = root / 'glossary.json'
        self.glossary.write_text(json.dumps(mapping), encoding='utf-8')
        self.root = root

    def tearDown(self):
        self.workspace.cleanup()

    def cli(self, model=None):
        return subprocess.run([sys.executable,
                               str(SCRIPTS / 'analyze_to_view.py'),
                               str(model or self.model), '--glossary',
                               str(self.glossary), '--timeout', '5'],
                              capture_output=True, text=True, timeout=15)

    def test_valid_analyzer_result_reaches_static_view(self):
        run = self.cli()
        self.assertEqual(run.returncode, 0)
        self.assertIn('&lt;script&gt;falso&lt;/script&gt;', run.stdout)
        self.assertNotIn('<script>', run.stdout)
        self.assertEqual(run.stderr, '')

    def test_invalid_input_cannot_emit_html(self):
        invalid = self.root / 'invalid.json'
        invalid.write_text('{broken', encoding='utf-8')
        run = self.cli(invalid)
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(run.stdout, '')

    def test_stalled_child_is_stopped_and_no_html_emitted(self):
        sleeper = self.root / 'sleeper.py'
        sleeper.write_text('import time\ntime.sleep(3600)\n', encoding='utf-8')
        observed = []
        def capture(*args, **kwargs):
            result = actual_supervision(*args, **kwargs)
            observed.append(result)
            return result
        with patch.object(analyze_to_view, 'run_supervised', side_effect=capture):
            with self.assertRaises(analyze_to_view.PipelineError) as raised:
                analyze_to_view.run_pipeline(
                    str(self.model), str(self.glossary), timeout=.2,
                    samples=1, analyzer_path=sleeper)
        self.assertEqual(raised.exception.code, 'ANALYZER_WALL_LIMIT')
        self.assertEqual(observed[0]['cleanup_status'],
                         'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED')
        self.assertTrue(observed[0]['timed_out'])
        with self.assertRaises(ChildProcessError):
            os.waitpid(observed[0]['pid'], os.WNOHANG)

    def test_nonzero_truncation_and_uncertain_cleanup_never_render(self):
        base = {'returncode': 0, 'stdout_bytes': b'{}', 'output_limit': False,
                'timed_out': False,
                'cleanup_status': 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED'}
        cases = [({**base, 'returncode': 7}, 'ANALYZER_EXIT_FAILURE'),
                 ({**base, 'output_limit': True}, 'ANALYZER_OUTPUT_LIMIT'),
                 ({**base, 'cleanup_status': 'INCOMPLETE'},
                  'ANALYZER_CLEANUP_UNCONFIRMED')]
        for result, code in cases:
            with self.subTest(code=code), patch.object(
                    analyze_to_view, 'run_supervised', return_value=result):
                with self.assertRaises(analyze_to_view.PipelineError) as raised:
                    analyze_to_view.run_pipeline(str(self.model),
                                                 str(self.glossary), timeout=1,
                                                 samples=1)
                self.assertEqual(raised.exception.code, code)


if __name__ == '__main__':
    unittest.main()
