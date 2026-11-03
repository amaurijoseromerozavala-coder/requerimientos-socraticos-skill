"""Bounded controls for the reachable Git history marker gate."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from ci.check_history_markers import scan_history


class HistoryMarkerGateTests(unittest.TestCase):
    def test_prior_commit_with_synthetic_marker_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.git(root, 'init', '-q', '-b', 'main')
            self.git(root, 'config', 'user.name', 'Test')
            self.git(root, 'config', 'user.email', 'test@example.invalid')
            (root / 'old.json').write_text('{"token":"--token=' + 'a' * 64 + '"}')
            self.git(root, 'add', '.')
            self.git(root, 'commit', '-qm', 'old')
            (root / 'old.json').write_text('{"token":"[REDACTED]"}')
            self.git(root, 'add', '.')
            self.git(root, 'commit', '-qm', 'new')
            self.assertEqual(scan_history(root), 2)

    def test_clean_history_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.git(root, 'init', '-q', '-b', 'main')
            self.git(root, 'config', 'user.name', 'Test')
            self.git(root, 'config', 'user.email', 'test@example.invalid')
            (root / 'old.json').write_text('{"status":"OK"}')
            self.git(root, 'add', '.')
            self.git(root, 'commit', '-qm', 'clean')
            self.assertEqual(scan_history(root), 0)

    @staticmethod
    def git(root, *args):
        subprocess.run(['git', *args], cwd=root, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)


if __name__ == '__main__':
    unittest.main()
