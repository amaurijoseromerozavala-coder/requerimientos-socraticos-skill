"""Bounded lifecycle tests; only short-lived owned fixture processes."""
import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'scripts/analyze_logic.py'


def load():
    spec = importlib.util.spec_from_file_location('requirements_supervisor', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SupervisorTests(unittest.TestCase):
    def test_worker_output_limit_is_inconclusive(self):
        module = load()
        worker = {'output_limit': True, 'timed_out': False, 'returncode': -9,
                  'stdout': 'truncated invalid JSON', 'elapsed_seconds': .01,
                  'cleanup_status': 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED',
                  'parent_death_policy': 'LINUX_DIRECT_CHILD_PDEATHSIG'}
        captured = io.StringIO()
        with patch.object(module, 'runtime_identity', return_value={}), \
                patch.object(module, 'admission', return_value=contextlib.nullcontext((123, {}))), \
                patch.object(module, 'run_supervised', return_value=worker), \
                patch.object(sys, 'argv', [str(SCRIPT), 'fixture.json', '--timeout', '2']), \
                contextlib.redirect_stdout(captured):
            returncode = module.main()
        result = json.loads(captured.getvalue())
        self.assertEqual(returncode, 3)
        self.assertEqual(result['status'], 'INCONCLUSIVE')
        self.assertEqual(result['error']['code'], 'WORKER_OUTPUT_LIMIT')
        self.assertNotIn('coverage', result)

    def test_waiting_worker_stops_and_is_reaped(self):
        module = load()
        started = time.monotonic()
        result = module.run_supervised([sys.executable, '-c', 'import time; time.sleep(5)'], .15)
        self.assertTrue(result['timed_out'])
        self.assertLess(time.monotonic()-started, 2)
        self.assertNotEqual(result['returncode'], 0)
        if os.name == 'posix':
            with self.assertRaises(ChildProcessError):
                os.waitpid(result['pid'], os.WNOHANG)

    def test_successful_worker_is_preserved(self):
        result = load().run_supervised([sys.executable, '-c', 'print(\'{"ok":true}\')'], 2)
        self.assertFalse(result['timed_out'])
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(json.loads(result['stdout']), {'ok': True})

    def test_cli_short_budget_is_inconclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'model.json'
            p.write_text(json.dumps({'inputs': [], 'outputs': [], 'domain': True, 'rules': [], 'properties': []}))
            run = subprocess.run([sys.executable, '-B', str(SCRIPT), str(p), '--timeout', '0.000001'], capture_output=True, text=True, timeout=3)
        result = json.loads(run.stdout)
        self.assertEqual(run.returncode, 3)
        self.assertEqual(result['status'], 'INCONCLUSIVE')
        self.assertEqual(result['error']['code'], 'WALL_CLOCK_LIMIT')
        self.assertNotIn('coverage', result)

    def test_runtime_identity_is_observed_not_authenticated(self):
        result = load().runtime_identity()
        self.assertTrue(Path(result['executable']).is_absolute())
        self.assertEqual(len(result['executable_sha256']), 64)
        self.assertEqual(result['authentication'], 'NOT_ESTABLISHED')
        self.assertIn('z3-solver', result['distributions'])

    def test_no_implicit_interpreter_fallback(self):
        launcher = ROOT.parents[1]/'bin/gentle-ai'
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, XDG_DATA_HOME=tmp)
            env.pop('REQUIREMENTS_PYTHON', None)
            p = subprocess.run([str(launcher), 'requirements', 'probe'], env=env, capture_output=True, text=True, timeout=3)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)['error']['code'], 'INTERPRETER_UNAVAILABLE')

    def test_cli_depth_is_rejected_before_decoder_recursion(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'deep.json'
            p.write_bytes(b'['*100000+b']'*100000)
            run = subprocess.run([sys.executable, '-B', str(SCRIPT), str(p), '--timeout', '2'], capture_output=True, text=True, timeout=4)
        self.assertEqual(run.returncode, 2)
        result = json.loads(run.stdout)
        self.assertEqual(result['error']['code'], 'INVALID_INPUT')
        self.assertEqual(result['error']['message'], 'JSON exceeds maximum depth')
        self.assertNotIn('Traceback', run.stderr)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux parent-death contract')
    def test_linux_direct_worker_follows_parent_lifecycle(self):
        # Keep adoption/reaping inside an owned test harness, never init or host services.
        code = r"""
import ctypes, importlib.util, json, os, signal, subprocess, sys, tempfile, time
from pathlib import Path
libc=ctypes.CDLL(None)
if libc.prctl(36,1,0,0,0)!=0:
 print(json.dumps({'supported':False}));raise SystemExit(0)
parent=None;worker=None;reaped=False
with tempfile.TemporaryDirectory() as tmp:
 marker=Path(tmp)/'worker'
 child_code='import os,time;from pathlib import Path;Path('+repr(str(marker))+').write_text(str(os.getpid()));time.sleep(5)'
 parent_code='import importlib.util;spec=importlib.util.spec_from_file_location("sup",'+repr(sys.argv[1])+');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.run_supervised('+repr([sys.executable,'-c',child_code])+',5)'
 try:
  parent=subprocess.Popen([sys.executable,'-c',parent_code],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  deadline=time.monotonic()+3
  while not marker.exists() and time.monotonic()<deadline:time.sleep(.01)
  if not marker.exists():raise RuntimeError('worker checkpoint missing')
  worker=int(marker.read_text());parent.kill();parent.wait(timeout=2)
  deadline=time.monotonic()+2
  while time.monotonic()<deadline:
   pid,status=os.waitpid(worker,os.WNOHANG)
   if pid:
    reaped=True
    print(json.dumps({'supported':True,'terminated':os.WIFSIGNALED(status) and os.WTERMSIG(status)==signal.SIGKILL}));break
   time.sleep(.01)
  if not reaped:raise RuntimeError('direct worker did not terminate')
 finally:
  if parent is not None and parent.poll() is None:parent.kill();parent.wait(timeout=2)
  if worker is not None and not reaped:
   try:os.kill(worker,signal.SIGKILL);os.waitpid(worker,0)
   except (ProcessLookupError,ChildProcessError):pass
"""
        p = subprocess.run([sys.executable, '-B', '-c', code, str(SCRIPT)], capture_output=True, text=True, timeout=9)
        self.assertEqual(p.returncode, 0, p.stderr)
        result = json.loads(p.stdout)
        if not result['supported']:
            self.skipTest('test harness cannot establish child subreaping')
        self.assertTrue(result['terminated'])

    @unittest.skipUnless(sys.platform.startswith('linux'), 'owned Linux subreaper fixture')
    def test_exited_leader_does_not_leave_group_pipes_waiting(self):
        code = r"""
import ctypes, importlib.util, json, os, signal, subprocess, sys, time
libc=ctypes.CDLL(None)
if libc.prctl(36,1,0,0,0)!=0:
 print(json.dumps({'supported':False}));raise SystemExit(0)
spec=importlib.util.spec_from_file_location('sup',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
child='import time;time.sleep(.8)'
worker='import subprocess,sys;p=subprocess.Popen([sys.executable,"-c",'+repr(child)+']);print(p.pid,flush=True)'
result=m.run_supervised([sys.executable,'-c',worker],.10)
pid=int(result['stdout'].strip())
try:
 os.waitpid(pid,0)
finally:
 try:os.kill(pid,signal.SIGKILL);os.waitpid(pid,0)
 except (ProcessLookupError,ChildProcessError):pass
print(json.dumps({'supported':True,'elapsed':result['elapsed_seconds'],'timed_out':result['timed_out']}))
"""
        p = subprocess.run([sys.executable, '-B', '-c', code, str(SCRIPT)], capture_output=True, text=True, timeout=3)
        self.assertEqual(p.returncode, 0, p.stderr)
        result = json.loads(p.stdout)
        if not result['supported']:
            self.skipTest('subreaper fixture unavailable')
        self.assertTrue(result['timed_out'])
        self.assertLess(result['elapsed'], .7)

    def test_unsupported_supervision_adapter_starts_no_worker(self):
        module = load()
        with patch.object(module.os, 'name', 'nt'), patch.object(module.subprocess, 'Popen') as spawn:
            with self.assertRaisesRegex(OSError, 'SUPERVISION_UNSUPPORTED_PLATFORM'):
                module.run_supervised([sys.executable, '-c', 'print(1)'], 1)
        spawn.assert_not_called()

    def test_public_argument_errors_preserve_invalid_input_contract(self):
        for args in [[], ['unused.json', '--timeout', '0'], ['unused.json', '--unknown-option'], ['unused.json', '--timeout', 'invalid']]:
            run = subprocess.run([sys.executable, '-B', str(SCRIPT), *args], capture_output=True, text=True, timeout=3)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stdout)['error']['code'], 'INVALID_INPUT')
            self.assertNotIn('Traceback', run.stderr)

if __name__ == '__main__':
    unittest.main(verbosity=2)
