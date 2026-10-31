import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[3]
ENTRY=ROOT/'skills/requerimientos-socraticos/scripts/requirements'

class PortableEntryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='portable skill ')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.skill=self.root/'skills/requerimientos-socraticos'
        (self.skill/'scripts').mkdir(parents=True)
        self.entry=self.skill/'scripts/requirements'
        if ENTRY.exists(): shutil.copy2(ENTRY,self.entry)
        self.env=dict(os.environ,REQUIREMENTS_PYTHON=sys.executable)

    def invoke(self,*args,env=None,path=None):
        return subprocess.run(['bash',str(path or self.entry),*args],env=env or self.env,
                              capture_output=True,text=True,timeout=5,cwd='/tmp')

    def test_help_without_runtime(self):
        r=self.invoke('--help',env=dict(self.env,REQUIREMENTS_PYTHON='/missing/python'))
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('activate',r.stdout)

    def test_all_routes_relocatable(self):
        routes={'activate':'activation_preflight.py','preflight':'activation_preflight.py',
                'probe':'probe_environment.py','analyze':'analyze_logic.py',
                'validate':'validate_git.py','git-validate':'validate_git.py',
                'normalize':'normalize_text.py','lint':'requirements_guard.py'}
        for helper in set(routes.values()):
            (self.skill/'scripts'/helper).write_text('import json,sys; print(json.dumps({"file":__file__,"args":sys.argv[1:]}))')
        for operation,helper in routes.items():
            with self.subTest(operation=operation):
                r=self.invoke(operation,'argument with spaces')
                self.assertEqual(r.returncode,0,r.stderr)
                d=json.loads(r.stdout)
                self.assertEqual(Path(d['file']),self.skill/'scripts'/helper)
                self.assertEqual(d['args'],(['validate'] if operation=='lint' else [])+['argument with spaces'])

    def test_symlink(self):
        (self.skill/'scripts/probe_environment.py').write_text('print("OK")')
        link=self.root/'entry link'; link.symlink_to(self.entry)
        r=self.invoke('probe',path=link)
        self.assertEqual((r.returncode,r.stdout),(0,'OK\n'),r.stderr)

    def test_invalid_explicit_runtime_no_fallback(self):
        for value in ('','/missing/python'):
            r=self.invoke('activate',env=dict(self.env,REQUIREMENTS_PYTHON=value))
            self.assertEqual(r.returncode,2)
            self.assertEqual(json.loads(r.stdout)['error']['code'],'INTERPRETER_UNAVAILABLE')

    def test_repository_venv_without_explicit_override(self):
        (self.root/'.venv/bin').mkdir(parents=True)
        (self.root/'.venv/bin/python').symlink_to(sys.executable)
        (self.skill/'scripts/probe_environment.py').write_text('print("LOCAL_VENV")')
        env=dict(self.env); env.pop('REQUIREMENTS_PYTHON')
        r=self.invoke('probe',env=env)
        self.assertEqual((r.returncode,r.stdout),(0,'LOCAL_VENV\n'),r.stderr)

    def test_unknown_operation_is_rejected(self):
        r=self.invoke('not-an-operation')
        self.assertEqual(r.returncode,2)
        self.assertEqual(json.loads(r.stdout)['error']['code'],'UNKNOWN_OPERATION')

    def test_wrapper_has_no_cloud_paths(self):
        source=(ROOT/'bin/gentle-ai').read_text()
        self.assertNotIn('/workspace/',source)
        self.assertNotIn('CODEX_HOME',source)

    def test_wrapper_external_upstream_and_recursion(self):
        (self.root/'bin').mkdir()
        wrapper=self.root/'bin/gentle-ai'; shutil.copy2(ROOT/'bin/gentle-ai',wrapper)
        fake=self.root/'upstream'; fake.write_text('#!/bin/sh\nprintf "upstream:%s\\n" "$*"\n'); fake.chmod(0o700)
        r=self.invoke('--version',path=wrapper,env=dict(self.env,GENTLE_AI_UPSTREAM=str(fake)))
        self.assertEqual((r.returncode,r.stdout),(0,'upstream:--version\n'),r.stderr)
        r=self.invoke('--version',path=wrapper,env=dict(self.env,GENTLE_AI_UPSTREAM=str(wrapper)))
        self.assertEqual(r.returncode,2)
        self.assertIn('UPSTREAM_UNAVAILABLE',r.stdout)

if __name__=='__main__': unittest.main(verbosity=2)
