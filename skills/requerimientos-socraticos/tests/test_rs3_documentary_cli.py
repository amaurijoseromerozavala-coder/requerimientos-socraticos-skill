"""The portable entry exposes D01/D02 without granting operational authority."""
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ENTRY = Path(__file__).resolve().parents[1] / 'scripts' / 'requirements'


def dossier():
    return {'schema_version': 'rs3-documentary-v1', 'snapshot_id': 'revision-7',
            'inventory_status': 'DECLARED_COMPLETE', 'critical_gaps': [],
            'requirements': [{'id': 'RF-1', 'applicability': 'APPLICABLE',
                              'applicability_basis': 'module A',
                              'assessment': 'SUPPORTED',
                              'evidence': {'status': 'CURRENT',
                                           'snapshot_id': 'revision-7',
                                           'reference': 'evidence/RF-1'}}]}


def invoke(*arguments, runtime=None):
    env = dict(os.environ, REQUIREMENTS_PYTHON=runtime or sys.executable)
    return subprocess.run(['bash', str(ENTRY), *map(str, arguments)], env=env,
                          capture_output=True, text=True, timeout=10)


class DocumentaryCliTests(unittest.TestCase):
    def test_help_and_valid_dossier(self):
        self.assertIn('documentary-check', invoke('--help').stdout)
        with tempfile.TemporaryDirectory(prefix='rs3-documentary-') as root:
            source = Path(root) / 'dossier.json'
            source.write_text(json.dumps(dossier()), encoding='utf-8')
            result = invoke('documentary-check', source)
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed['production_ready']['model_status'], 'MODEL_ELIGIBLE')
        self.assertEqual(parsed['input_sha256'],
                         hashlib.sha256(json.dumps(dossier()).encode('utf-8')).hexdigest())
        self.assertEqual(parsed['authority_verification'], 'NOT_PERFORMED')
        self.assertIs(parsed['deployment_authorized'], False)

    def test_duplicate_key_oversize_and_symlink_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix='rs3-documentary-') as root:
            source = Path(root) / 'dossier.json'
            link = Path(root) / 'link.json'
            for content, path in (('{"snapshot_id":"x","snapshot_id":"y"}', source),
                                  (' ' * (256 * 1024 + 1), source)):
                source.write_text(content, encoding='utf-8')
                result = invoke('documentary-check', path)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)['error']['code'],
                                 'INVALID_INPUT')
                self.assertNotIn('production_ready', result.stdout)
            source.write_text(json.dumps(dossier()), encoding='utf-8')
            link.symlink_to(source)
            result = invoke('documentary-check', link)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)['error']['code'], 'INVALID_INPUT')

    def test_missing_runtime_preserves_portable_failure(self):
        with tempfile.TemporaryDirectory(prefix='rs3-documentary-') as root:
            source = Path(root) / 'dossier.json'
            source.write_text(json.dumps(dossier()), encoding='utf-8')
            result = invoke('documentary-check', source, runtime='/missing/python')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error']['code'],
                         'INTERPRETER_UNAVAILABLE')


if __name__ == '__main__':
    unittest.main()
