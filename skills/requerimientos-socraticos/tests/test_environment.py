"""Public-interface tests for bounded, non-identifying environment discovery."""
import json
import os
import importlib.util
from unittest.mock import patch
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/probe_environment.py'

class EnvironmentTests(unittest.TestCase):
    def run_probe(self, *args):
        p = subprocess.run([sys.executable, '-B', str(SCRIPT), *args], capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def test_probe_has_no_hardware_coverage_claim(self):
        doc = self.run_probe()
        self.assertEqual(doc['kind'], 'OBSERVED_LOCAL_ENVIRONMENT')
        self.assertEqual(doc['coverage']['status'], 'NOT_COMPUTED_FROM_HARDWARE')
        self.assertEqual(doc['capacity_estimate']['status'], 'NOT_CALIBRATED')
        self.assertFalse(doc['execution_authorized'])
        self.assertEqual(doc['target_equivalence'], 'NOT_ESTABLISHED')
        self.assertEqual(doc['observation_scope']['physical_host'], 'NOT_OBSERVED')
        self.assertEqual(doc['resource_admission'], 'NOT_ASSESSED')
        self.assertTrue(Path(doc['runtime']['executable']).is_absolute())
        self.assertEqual(doc['runtime']['authentication'], 'NOT_ESTABLISHED')
        for key in ['hostname', 'username', 'device_id', 'product_id', 'environment']:
            self.assertNotIn(key, doc)

    def test_path_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as d:
            doc = self.run_probe('--path', d)
            self.assertEqual(list(Path(d).iterdir()), [])
            self.assertGreater(doc['storage']['free_bytes'], 0)
            self.assertEqual(doc['storage']['status'], 'OBSERVED')

    def test_missing_path_is_explicit_unknown(self):
        doc = self.run_probe('--path', '/definitely-not-an-existing-requirements-path')
        self.assertEqual(doc['storage']['status'], 'UNKNOWN')
        self.assertIsNone(doc['storage']['free_bytes'])

    def test_cpu_and_memory_have_provenance(self):
        doc = self.run_probe()
        self.assertIn('source', doc['cpu'])
        self.assertIn('source', doc['memory'])
        self.assertEqual(doc['thermal']['status'], 'NOT_MEASURED')
        self.assertIn('observed_at', doc)

    def test_cpu_model_reads_bounded_prefix_from_large_cpuinfo(self):
        spec = importlib.util.spec_from_file_location('probe_environment_cpu_prefix', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        from unittest.mock import mock_open
        source = 'model name : Test CPU 99\n' + ('padding\n' * 5000)
        opened = mock_open(read_data=source)
        with patch.object(module.Path, 'open', opened):
            observation = module.cpu_model_observation()
        self.assertEqual(observation['model'], 'Test CPU 99')
        opened.return_value.read.assert_called_once_with(16384)

    def test_cgroup_unknown_and_unlimited_are_distinct(self):
        spec = importlib.util.spec_from_file_location('probe_environment', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for token, expected in [('max', 'UNLIMITED_VISIBLE_SCOPE'), (None, 'UNKNOWN'), ('not-a-number', 'MALFORMED')]:
            fake = {'/proc/self/cgroup': '0::/\n', '/sys/fs/cgroup/memory.max': token,
                    '/sys/fs/cgroup/memory.current': '10', '/sys/fs/cgroup/cpu.max': 'max 100000'}
            with patch.object(module, 'read_small', side_effect=lambda p: fake.get(str(p))), patch.object(module.Path, 'is_dir', return_value=True):
                observation = module.cgroup_observation()
            self.assertEqual(observation['limit_states'][0]['memory'], expected)
            self.assertEqual(observation['limit_states'][0]['cpu'], 'UNLIMITED_VISIBLE_SCOPE')
            self.assertEqual(observation['memory_limits'], [])

    def test_launcher_rejects_missing_explicit_interpreter(self):
        launcher = SCRIPT.parents[3] / 'bin/gentle-ai'
        env = dict(os.environ, REQUIREMENTS_PYTHON='/definitely-missing-requirements-interpreter')
        p = subprocess.run([str(launcher), 'requirements', 'probe'], env=env, capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)['error']['code'], 'INTERPRETER_UNAVAILABLE')

    def test_launcher_rejects_empty_explicit_interpreter(self):
        launcher = SCRIPT.parents[3] / 'bin/gentle-ai'
        p = subprocess.run([str(launcher), 'requirements', 'probe'], env=dict(os.environ, REQUIREMENTS_PYTHON=''), capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)['error']['code'], 'INTERPRETER_UNAVAILABLE')

    def test_launcher_resolves_explicit_interpreter_from_path(self):
        launcher = SCRIPT.parents[3] / 'bin/gentle-ai'
        with tempfile.TemporaryDirectory() as tmp:
            selected = Path(tmp) / 'requirements-selected-python'
            selected.write_text('#!'+sys.executable+'\nprint(\'{"kind":"SELECTED_TEST_INTERPRETER"}\')\n')
            selected.chmod(0o700)
            env = dict(os.environ, REQUIREMENTS_PYTHON=selected.name, PATH=tmp+os.pathsep+os.environ['PATH'])
            p = subprocess.run([str(launcher), 'requirements', 'probe'], env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)['kind'], 'SELECTED_TEST_INTERPRETER')

if __name__ == '__main__':
    unittest.main(verbosity=2)
