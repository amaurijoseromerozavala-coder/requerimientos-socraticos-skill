"""Fail-closed installation contract for a hash-locked Python runtime."""

import hashlib
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import prepare_runtime as runtime


class PrepareRuntimeTests(unittest.TestCase):
    def test_portable_guidance_tracks_remaining_gaps(self):
        skill_root = SCRIPTS.parent
        guidance = (skill_root / 'references/gentle-pi.md').read_text()
        deployment = (skill_root / 'references/authority-deployment.md').read_text()
        contract = json.loads((skill_root / 'assets/rs3-authority-deployment.json')
                              .read_text())
        self.assertIn('prepare_runtime.py', guidance)
        self.assertIn('requirements-runtime.lock', deployment)
        gaps = contract['runtime_replication']['current_gaps']
        self.assertNotIn('TRANSITIVE_DEPENDENCIES_NOT_HASH_LOCKED', gaps)
        self.assertIn('CI_NOT_USING_RUNTIME_LOCK', gaps)
        self.assertEqual(contract['runtime_replication']['status'],
                         'NOT_ESTABLISHED')

    def test_lock_contains_full_pinned_hashed_graph(self):
        raw = runtime.read_verified_lock()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), runtime.LOCK_SHA256)
        for name in ('jsonschema==4.26.0', 'z3-solver==4.15.4.0',
                     'attrs==', 'referencing==', 'rpds-py==',
                     'jsonschema-specifications=='):
            self.assertIn(name.encode(), raw)
        self.assertIn(b'--hash=sha256:', raw)
        with tempfile.TemporaryDirectory() as directory:
            altered = Path(directory) / 'altered.lock'
            altered.write_bytes(raw + b'\n# mutation\n')
            with mock.patch.object(runtime, 'LOCK_PATH', altered):
                with self.assertRaises(runtime.RuntimePreparationBlocked):
                    runtime.read_verified_lock()

    def test_incompatible_python_and_existing_target_block_before_install(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'venv'
            target.mkdir()
            with mock.patch.object(runtime, '_run') as run:
                with self.assertRaises(runtime.RuntimePreparationBlocked):
                    runtime.prepare_runtime(target, python=sys.executable)
                with self.assertRaises(runtime.RuntimePreparationBlocked):
                    runtime.prepare_runtime(Path('relative-venv'), python=sys.executable)
                with self.assertRaises(runtime.RuntimePreparationBlocked):
                    runtime.prepare_runtime(Path(directory) / 'new', python='python3')
                run.assert_not_called()
        with self.assertRaises(runtime.RuntimePreparationBlocked):
            runtime.validate_python_identity({'implementation': 'pypy',
                                              'major': 3, 'minor': 12})
        with self.assertRaises(runtime.RuntimePreparationBlocked):
            runtime.validate_python_identity({'implementation': 'cpython',
                                              'major': 3, 'minor': 11})

    def test_install_command_requires_hashes_and_binary_wheels(self):
        command = runtime.install_command('/tmp/stage/bin/python', '/tmp/stage/requirements.lock')
        self.assertIn('--require-hashes', command)
        self.assertIn('--only-binary=:all:', command)
        self.assertIn('--no-input', command)
        self.assertIn('--isolated', command)
        self.assertEqual(command[1:3], ['-I', '-m'])
        self.assertIn('/tmp/stage/requirements.lock', command)
        self.assertNotIn(str(runtime.LOCK_PATH), command)

    def test_failed_install_cleans_staging_and_does_not_promote(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'venv'
            with (mock.patch.object(runtime, '_python_identity',
                                    return_value={'implementation': 'cpython',
                                                  'major': 3, 'minor': 12}),
                  mock.patch.object(runtime, '_run',
                                    side_effect=[None, runtime.RuntimePreparationBlocked(
                                        'SYNTHETIC_INSTALL_FAILURE')])):
                with self.assertRaises(runtime.RuntimePreparationBlocked):
                    runtime.prepare_runtime(target, python=sys.executable)
            self.assertFalse(target.exists())
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_pythonpath_sitecustomize_cannot_run_in_install_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / 'marker'
            (Path(directory) / 'sitecustomize.py').write_text(
                f'from pathlib import Path;Path({str(marker)!r}).write_text("ran")')
            command = runtime.install_command(sys.executable, '/tmp/lock')
            with mock.patch.dict(os.environ, {'PYTHONPATH': directory}):
                subprocess.run([sys.executable, '-I', '-c', 'pass'], check=True)
            self.assertFalse(marker.exists())
            self.assertEqual(command[1:3], ['-I', '-m'])

    def test_verified_lock_snapshot_survives_source_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.lock'
            original = runtime.read_verified_lock()
            source.write_bytes(original)
            target = Path(directory) / 'venv'
            commands = []
            def simulated_run(command, remaining):
                commands.append(command)
                if len(commands) == 1:
                    source.write_bytes(b'mutated after verification')
                if len(commands) == 2:
                    snapshot = Path(command[-1])
                    self.assertNotEqual(snapshot, source)
                    self.assertEqual(snapshot.read_bytes(), original)
            with (mock.patch.object(runtime, 'LOCK_PATH', source),
                  mock.patch.object(runtime, '_python_identity', return_value={
                      'implementation': 'cpython', 'major': 3, 'minor': 12}),
                  mock.patch.object(runtime, '_run', side_effect=simulated_run),
                  mock.patch.object(runtime, '_installed_artifacts', return_value=[]),
                  mock.patch.object(runtime, '_repair_relocation')):
                runtime.prepare_runtime(target, python=sys.executable)

    def test_promotion_does_not_replace_new_empty_target(self):
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory) / 'stage'
            target = Path(directory) / 'target'
            stage.mkdir()
            target.mkdir()
            with self.assertRaises(runtime.RuntimePreparationBlocked):
                runtime._promote(stage, target)
            self.assertTrue(stage.exists())
            self.assertTrue(target.exists())

    def test_insufficient_visible_storage_blocks_before_work(self):
        with tempfile.TemporaryDirectory() as directory:
            with (mock.patch.object(runtime, 'shutil') as shutil_mock,
                  mock.patch.object(runtime, '_run') as run):
                shutil_mock.disk_usage.return_value.free = 1
                with self.assertRaisesRegex(runtime.RuntimePreparationBlocked,
                                            'VISIBLE_STORAGE_INSUFFICIENT'):
                    runtime.prepare_runtime(Path(directory) / 'venv',
                                            python=sys.executable)
                run.assert_not_called()

    def test_timeout_is_structured_block(self):
        with self.assertRaisesRegex(runtime.RuntimePreparationBlocked,
                                    'PREPARATION_TIMEOUT'):
            runtime._run([sys.executable, '-c', 'import time;time.sleep(2)'], 0.01)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux process groups')
    def test_timeout_kills_child_process_group(self):
        with tempfile.TemporaryDirectory() as directory:
            pid_file = Path(directory) / 'pid'
            source = ('import subprocess,sys,time;'
                      'p=subprocess.Popen([sys.executable,"-c",'
                      '"import time;time.sleep(10)"]);'
                      'open(sys.argv[1],"w").write(str(p.pid));time.sleep(10)')
            pid = None
            try:
                with self.assertRaisesRegex(runtime.RuntimePreparationBlocked,
                                            'PREPARATION_TIMEOUT'):
                    runtime._run([sys.executable, '-c', source, str(pid_file)], 0.5)
                pid = int(pid_file.read_text())
                for _ in range(20):
                    stat_path = Path('/proc') / str(pid) / 'stat'
                    if not stat_path.exists() or stat_path.read_text().split(') ', 1)[1][0] == 'Z':
                        break
                    time.sleep(0.01)
                else:
                    self.fail('descendant survived timeout')
            finally:
                if pid is not None:
                    try:
                        os.kill(pid, 9)
                    except ProcessLookupError:
                        pass

    def test_install_report_records_selected_wheels(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / 'report.json'
            report.write_text(json.dumps({'install': [{'metadata': {
                'name': 'example', 'version': '1.0'}, 'download_info': {
                'archive_info': {'hashes': {'sha256': 'a' * 64}}}}]}))
            self.assertEqual(runtime._installed_artifacts(report), [{
                'name': 'example', 'version': '1.0', 'sha256': 'a' * 64}])

    def test_killpg_failure_reports_uncertain_cleanup(self):
        process = mock.Mock(pid=987654)
        process.wait.side_effect = subprocess.TimeoutExpired(['synthetic'], 1)
        with (mock.patch.object(runtime.subprocess, 'Popen', return_value=process),
              mock.patch.object(runtime.os, 'killpg', side_effect=PermissionError('synthetic'))):
            with self.assertRaisesRegex(runtime.RuntimePreparationBlocked,
                                        'PROCESS_CLEANUP_UNCONFIRMED') as caught:
                runtime._run(['synthetic'], 1)
        self.assertTrue(caught.exception.cleanup_unconfirmed)

    def test_uncertain_cleanup_preserves_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'venv'
            with (mock.patch.object(runtime, '_python_identity', return_value={
                      'implementation': 'cpython', 'major': 3, 'minor': 12}),
                  mock.patch.object(runtime, '_run', side_effect=runtime.RuntimePreparationBlocked(
                      'PROCESS_CLEANUP_UNCONFIRMED', cleanup_unconfirmed=True))):
                with self.assertRaises(runtime.RuntimePreparationBlocked):
                    runtime.prepare_runtime(target, python=sys.executable)
            self.assertFalse(target.exists())
            self.assertEqual(len(list(Path(directory).glob('.rs3-runtime-stage-*'))), 1)

    def test_promoted_venv_console_script_and_activation_use_final_path(self):
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory) / 'stage'
            target = Path(directory) / 'venv'
            subprocess.run([sys.executable, '-I', '-m', 'venv', str(stage)],
                           check=True, timeout=30)
            runtime._repair_relocation(stage, target)
            runtime._promote(stage, target)
            result = subprocess.run([str(target / 'bin/pip'), '--version'],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            activated = subprocess.run(
                ['bash', '-c', '. "$1/bin/activate"; printf "%s" "$VIRTUAL_ENV"',
                 'bash', str(target)], capture_output=True, text=True, timeout=10)
            self.assertEqual(activated.returncode, 0, activated.stderr)
            self.assertEqual(activated.stdout, str(target))

    def test_post_promotion_check_failure_removes_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'venv'
            calls = [None, None, None, None,
                     runtime.RuntimePreparationBlocked('SYNTHETIC_POST_PROMOTION_FAILURE')]
            with (mock.patch.object(runtime, '_python_identity', return_value={
                      'implementation': 'cpython', 'major': 3, 'minor': 12}),
                  mock.patch.object(runtime, '_run', side_effect=calls),
                  mock.patch.object(runtime, '_installed_artifacts', return_value=[]),
                  mock.patch.object(runtime, '_repair_relocation')):
                with self.assertRaises(runtime.RuntimePreparationBlocked):
                    runtime.prepare_runtime(target, python=sys.executable)
            self.assertFalse(target.exists())

    def test_cleanup_failure_blocks_without_success(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'venv'
            with (mock.patch.object(runtime, '_python_identity', return_value={
                      'implementation': 'cpython', 'major': 3, 'minor': 12}),
                  mock.patch.object(runtime, '_run', side_effect=runtime.RuntimePreparationBlocked('FAIL')),
                  mock.patch.object(runtime.shutil, 'rmtree', side_effect=OSError('synthetic'))):
                with self.assertRaisesRegex(runtime.RuntimePreparationBlocked,
                                            'STAGING_CLEANUP_UNCONFIRMED'):
                    runtime.prepare_runtime(target, python=sys.executable)


if __name__ == '__main__':
    unittest.main()
