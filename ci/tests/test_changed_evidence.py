"""Git-object controls for new public evidence; values are synthetic."""
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout

from ci.check_review_evidence import check_changed


class ChangedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='changed-evidence-')
        self.root = Path(self.temp.name)
        self.previous = Path.cwd()
        os.chdir(self.root)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        path = self.root / 'docs/skill-audit/previous.json'
        path.parent.mkdir(parents=True)
        path.write_text('{"token":"abcdefgh1234"}')
        self.git('add', '.')
        self.git('commit', '-qm', 'historical fixture')
        self.base = self.git('rev-parse', 'HEAD').strip()

    def tearDown(self):
        os.chdir(self.previous)
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(('git', *args), text=True)

    def observed(self, base):
        output = io.StringIO()
        with redirect_stdout(output):
            result = check_changed(base)
        return result, output.getvalue()

    def test_new_value_blocks_without_printing_it(self):
        path = self.root / 'docs/skill-audit/new.json'
        path.write_text('{"token":"ijklmnop5678"}')
        self.git('add', '.')
        self.git('commit', '-qm', 'new fixture')
        result, output = self.observed(self.base)
        self.assertEqual(result, 2)
        self.assertIn('flagged=1', output)
        self.assertNotIn('ijklmnop5678', output)

    def test_unchanged_historical_value_does_not_block_clean_candidate(self):
        path = self.root / 'docs/skill-audit/new.json'
        path.write_text('{"status":"OK"}')
        self.git('add', '.')
        self.git('commit', '-qm', 'new fixture')
        result, output = self.observed(self.base)
        self.assertEqual(result, 0)
        self.assertIn('checked=1 flagged=0 unknown=0', output)

    def test_escaped_command_in_new_evidence_blocks(self):
        path = self.root / 'docs/skill-audit/new.json'
        path.write_text('{"command":"review \\u002d\\u002dtoken=ijklmnop5678"}')
        self.git('add', '.')
        self.git('commit', '-qm', 'escaped fixture')
        result, output = self.observed(self.base)
        self.assertEqual(result, 2)
        self.assertIn('flagged=1', output)
        self.assertNotIn('ijklmnop5678', output)

    def test_invalid_base_and_symlink_fail_closed(self):
        self.assertEqual(self.observed('not-a-commit')[0], 2)
        path = self.root / 'docs/skill-audit/link.json'
        path.symlink_to('previous.json')
        self.git('add', '.')
        self.git('commit', '-qm', 'link fixture')
        result, output = self.observed(self.base)
        self.assertEqual(result, 2)
        self.assertIn('unknown=1', output)


if __name__ == '__main__':
    unittest.main()
