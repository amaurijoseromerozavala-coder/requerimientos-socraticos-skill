"""Adversarial bounded Linux guard tests. Temporary trees only."""
import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/requirements_guard.py'
spec = importlib.util.spec_from_file_location('guard', SCRIPT)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'source'
        self.root.mkdir()
        (self.root / 'a.json').write_text('{"a":1}')
    def tearDown(self):
        self.tmp.cleanup()
    def baseline(self):
        return g.observe(self.root)
    def rejects_mutation(self, mutation):
        baseline = self.baseline()
        mutation()
        with self.assertRaisesRegex(g.GuardError, 'TREE_CHANGED|UNSUPPORTED_ENTRY'):
            g.observe(self.root, baseline)
    def test_added_file(self):
        self.rejects_mutation(lambda: (self.root / '99-override.md').write_text('injected'))
    def test_deleted_file(self):
        self.rejects_mutation(lambda: (self.root / 'a.json').unlink())
    def test_renamed_file(self):
        self.rejects_mutation(lambda: (self.root / 'a.json').rename(self.root / 'renamed'))
    def test_empty_directory(self):
        self.rejects_mutation(lambda: (self.root / 'empty').mkdir())
    def test_permissions(self):
        self.rejects_mutation(lambda: (self.root / 'a.json').chmod((self.root / 'a.json').stat().st_mode ^ 0o100))
    def test_content(self):
        self.rejects_mutation(lambda: (self.root / 'a.json').write_text('changed'))
    def test_symlink_rejected(self):
        (self.root / 'alias').symlink_to(self.root / 'a.json')
        with self.assertRaisesRegex(g.GuardError, 'UNSUPPORTED_ENTRY'):
            self.baseline()
    def test_fifo_does_not_hang(self):
        os.mkfifo(self.root / 'fifo')
        with self.assertRaisesRegex(g.GuardError, 'UNSUPPORTED_ENTRY'):
            self.baseline()
    def test_modify_restore_observed(self):
        with g.Observation() as monitor:
            monitor.add(self.root)
            p = self.root / 'a.json'; original = p.read_bytes()
            p.write_bytes(b'mutated');p.write_bytes(original)
            with self.assertRaisesRegex(g.GuardError, 'OBSERVED_CHANGE'):
                monitor.check()
    def test_later_subtree_modify_restore_during_first_file_read(self):
        from unittest.mock import patch
        import stat
        later = self.root / 'z-later'
        later.mkdir()
        target = later / 'file.json'
        target.write_bytes(b'original')
        baseline = self.baseline()
        original_read = g.os.read
        fired = []
        def mutate_on_first_regular_read(fd, size):
            if not fired and stat.S_ISREG(os.fstat(fd).st_mode):
                fired.append(True)
                target.write_bytes(b'transient')
                target.write_bytes(b'original')
            return original_read(fd, size)
        with patch.object(g.os, 'read', side_effect=mutate_on_first_regular_read):
            with self.assertRaisesRegex(g.GuardError, 'OBSERVED_CHANGE'):
                g.observe(self.root, baseline)
        self.assertTrue(fired, 'Mutation stimulus must execute')

    def test_new_subdirectory_observed(self):
        with g.Observation() as monitor:
            monitor.add(self.root)
            (self.root / 'new').mkdir()
            with self.assertRaisesRegex(g.GuardError, 'OBSERVED_CHANGE'):
                monitor.check()
    def test_root_rename_observed(self):
        with g.Observation() as monitor:
            monitor.add(self.root)
            self.root.rename(self.root.with_name('renamed'))
            with self.assertRaisesRegex(g.GuardError, 'OBSERVED_CHANGE'):
                monitor.check()
    def test_inotify_overflow_is_rejected(self):
        # Explicit synthetic kernel record; not an actual overflow stress claim.
        from unittest.mock import patch
        record = g.struct.pack('iIII', -1, 0x4000, 0, 0)
        with g.Observation() as monitor, patch.object(g.os, 'read', return_value=record):
            with self.assertRaisesRegex(g.GuardError, 'OBSERVED_CHANGE_OR_MONITOR_LOSS'):
                monitor.check()
    def test_lock_contention_timeout(self):
        with g.lock(self.root.resolve(), .2):
            began = time.monotonic()
            with self.assertRaisesRegex(g.GuardError, 'LOCK_TIMEOUT'):
                with g.lock(self.root.resolve(), .05):
                    self.fail('Must not acquire competing lock')
            self.assertLess(time.monotonic() - began, 1)
    def test_five_concurrent_validators(self):
        sys.path.insert(0, str(SCRIPT.parents[1] / 'tests'))
        import test_interview
        test_interview.ContractTests().stage_prd(self.root)
        def run(_):
            return subprocess.run([sys.executable, '-B', str(SCRIPT), 'validate', str(self.root), '--prd', 'prd.json'], capture_output=True, text=True, timeout=10)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(run, range(5)))
        for result in results:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len({json.loads(r.stdout)['tree_sha256'] for r in results}), 1)
    def test_unchanged_tree(self):
        baseline = self.baseline()
        self.assertEqual(g.observe(self.root, baseline)['tree_sha256'], baseline['tree_sha256'])
    def test_corrupt_baseline(self):
        baseline = self.baseline();baseline['tree_sha256'] = 'f' * 64
        with self.assertRaisesRegex(g.GuardError, 'INVALID_BASELINE'):
            g.observe(self.root, baseline)
    def test_nonobject_baselines_are_structured_blocked(self):
        baseline = Path(self.tmp.name) / 'baseline.json'
        for value in [[], 'text', 42, True, None]:
            with self.subTest(value=value):
                baseline.write_text(json.dumps(value))
                p = subprocess.run([sys.executable, '-B', str(SCRIPT), 'verify', str(self.root), '--baseline', str(baseline)], capture_output=True, text=True, timeout=10)
                self.assertEqual(p.returncode, 1, p.stdout)
                self.assertEqual(json.loads(p.stdout)['status'], 'BLOCKED')
                self.assertIn('INVALID_BASELINE', p.stdout)
                self.assertNotIn('Traceback', p.stderr)
    def test_depth_limit_is_explicit(self):
        nested = self.root
        for _ in range(65):
            nested = nested / 'd'
            nested.mkdir()
        with self.assertRaisesRegex(g.GuardError, 'DEPTH_LIMIT'):
            self.baseline()

    def test_budget(self):
        with g.Observation() as monitor:
            with self.assertRaisesRegex(g.GuardError, 'BYTE_LIMIT'):
                g.tree(self.root, monitor, max_bytes=1)
    def test_invalid_timeout(self):
        with self.assertRaisesRegex(g.GuardError, 'INVALID_TIMEOUT'):
            g.observe(self.root, timeout=float('nan'))
    def test_manual_ready_does_not_advance(self):
        # A genuine structurally valid synthetic READY document from existing
        # tests passes documentary validation, but never advances the guard.
        sys.path.insert(0, str(SCRIPT.parents[1] / 'tests'))
        import test_interview
        helper = test_interview.ContractTests()
        path = helper.stage_prd(self.root)
        helper.set_synthetic_ready(path)
        valid = subprocess.run([sys.executable, '-B', str(SCRIPT), 'validate', str(self.root), '--prd', 'prd.json'], capture_output=True, text=True, timeout=15)
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        blocked = subprocess.run([sys.executable, '-B', str(SCRIPT), 'advance', str(self.root), '--prd', 'prd.json'], capture_output=True, text=True, timeout=15)
        self.assertEqual(blocked.returncode, 1, blocked.stdout)
        self.assertIn('DOWNSTREAM_NOT_CONFIGURED', blocked.stdout)
    def test_corrupt_document_blocks(self):
        (self.root / 'prd.json').write_text('{broken')
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), 'validate', str(self.root), '--prd', 'prd.json'], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertIn('DOCUMENT_INVALID', result.stdout)

if __name__ == '__main__':
    unittest.main(verbosity=2)
