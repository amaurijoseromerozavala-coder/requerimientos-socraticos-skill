"""Controls for the one-time history-rewrite CI base."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from ci.select_evidence_base import select_base


class EvidenceBaseTests(unittest.TestCase):
    def test_exact_forced_transition_uses_existing_ancestor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.git(root, 'init', '-q', '-b', 'main')
            self.git(root, 'config', 'user.name', 'Test')
            self.git(root, 'config', 'user.email', 'test@example.invalid')
            (root / 'a').write_text('one')
            self.git(root, 'add', '.')
            self.git(root, 'commit', '-qm', 'base')
            base = self.git(root, 'rev-parse', 'HEAD').strip()
            (root / 'a').write_text('two')
            self.git(root, 'commit', '-qam', 'next')
            previous = 'f' * 40
            self.assertEqual(select_base(root, previous, 'true',
                                         previous=previous, rewritten=base), base)
            self.assertEqual(select_base(root, base, 'false',
                                         previous=previous, rewritten=base), base)
            self.assertEqual(select_base(root, base, 'true',
                                         previous=previous, rewritten=base), base)
            with self.assertRaises(ValueError):
                select_base(root, previous, 'true', previous=previous,
                            rewritten='e' * 40)

    def test_invalid_event_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            for before, forced in (('invalid', 'false'), ('0' * 40, 'maybe')):
                with self.subTest(before=before, forced=forced):
                    with self.assertRaises(ValueError):
                        select_base(Path(directory), before, forced,
                                    previous='f' * 40, rewritten='e' * 40)

    @staticmethod
    def git(root, *args):
        return subprocess.check_output(['git', *args], cwd=root,
                                       stderr=subprocess.DEVNULL, text=True)


if __name__ == '__main__':
    unittest.main()
