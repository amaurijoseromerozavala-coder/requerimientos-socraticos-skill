"""Pinned Git bytes, not a mutable worktree or a self-declared source hash."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_logic.py'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args]).decode().strip()


def run_case(kind):
    model = {'inputs': ['A'], 'outputs': ['P'], 'domain': True,
             'rules': [{'id': 'inactive', 'guard': False,
                        'response': {'var': 'P'}}], 'properties': []}
    raw = json.dumps(model, sort_keys=True).encode()
    with tempfile.TemporaryDirectory(prefix='pinned-source-') as root:
        repo = Path(root) / 'repo'
        repo.mkdir()
        git(repo, 'init', '-q')
        source = repo / 'source.txt'
        source.write_bytes(b'A means approved' if kind == 'past_end'
                           else b'A means approved\n')
        if kind == 'symlink':
            source.unlink()
            source.symlink_to('elsewhere.txt')
        git(repo, 'add', 'source.txt')
        subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.invalid',
                        'commit', '-qm', 'source fixture'], check=True)
        commit = git(repo, 'rev-parse', 'HEAD')
        source.unlink()
        source.write_bytes(b'worktree changed\n')
        text = 'A means approved'
        if kind == 'wrong_quote':
            text = 'A means rejected'
        glossary = {'schema_version': 'rs3-gap-glossary/v2',
                    'model_sha256': hashlib.sha256(raw).hexdigest(),
                    'variables': {'A': {'when_true': 'A aplica',
                                        'when_false': 'A no aplica',
                                        'source_ref': 'source.txt',
                                        'source_text': text,
                                        'source_sha256': hashlib.sha256(text.encode()).hexdigest(),
                                        'source_start_byte': 0,
                                        'source_end_byte': (len(text.encode()) + 2
                                                            if kind == 'past_end'
                                                            else len(text.encode()))}}}
        model_path = Path(root) / 'model.json'
        map_path = Path(root) / 'glossary.json'
        model_path.write_bytes(raw)
        map_path.write_text(json.dumps(glossary), encoding='utf-8')
        command = [sys.executable, str(SCRIPT), str(model_path),
                   '--glossary', str(map_path)]
        if kind != 'no_snapshot':
            command += ['--source-repo', str(repo),
                        '--source-commit', 'HEAD' if kind == 'symbolic' else commit]
        done = subprocess.run(command, capture_output=True, text=True, timeout=15)
        return done.returncode, json.loads(done.stdout), commit


class PinnedSourceEvidenceTests(unittest.TestCase):
    def test_pinned_bytes_survive_worktree_mutation(self):
        code, result, commit = run_case('valid')
        self.assertEqual(code, 0)
        packet = result['gap_questions']
        self.assertEqual(packet['status'], 'PROPOSED_UNVERIFIED')
        self.assertEqual(packet['source_bytes'], 'PINNED_GIT_BLOB_SLICE_VERIFIED')
        self.assertEqual(packet['source_authenticity'], 'NOT_ESTABLISHED')
        self.assertEqual(packet['source_commit_oid'], commit)
        self.assertEqual(packet['git_object_format'], 'sha1')
        self.assertEqual(len(packet['questions']), 1)
        self.assertEqual(packet['questions'][0]['sources']['A']['source_text'],
                         'A means approved')

    def test_self_consistent_wrong_quote_and_symlink_rejected(self):
        for kind in ('wrong_quote', 'symlink', 'past_end'):
            with self.subTest(kind=kind):
                code, result, _ = run_case(kind)
                self.assertEqual(code, 2)
                self.assertEqual(result['error']['code'], 'INVALID_INPUT')
                self.assertNotIn('gap_questions', result)

    def test_symbolic_ref_rejected_and_missing_snapshot_blocks(self):
        code, result, _ = run_case('symbolic')
        self.assertEqual(code, 2)
        self.assertEqual(result['error']['code'], 'INVALID_INPUT')
        code, result, _ = run_case('no_snapshot')
        self.assertEqual(code, 0)
        self.assertEqual(result['gap_questions']['status'],
                         'NEEDS_SOURCE_SNAPSHOT')
        self.assertEqual(result['gap_questions']['questions'], [])


if __name__ == '__main__':
    unittest.main()
