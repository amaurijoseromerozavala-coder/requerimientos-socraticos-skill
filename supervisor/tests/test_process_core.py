import concurrent.futures
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from supervisor.process_core import ProcessSupervisor, Limits

# Print observed process envelopes, with byte streams encoded for audit logs.
_original_run = ProcessSupervisor.run
def observed_run(self):
    result = _original_run(self)
    printable = {k: (v.hex() if isinstance(v, bytes) else v) for k,v in result.items()}
    print(json.dumps({'observed_process_result': printable, 'stream_encoding': 'hex'}), flush=True)
    return result
ProcessSupervisor.run = observed_run

class ProcessTests(unittest.TestCase):
    def supervisor(self, script, **limits):
        return ProcessSupervisor((sys.executable, '-B', '-c', script), Limits(**limits))

    def test_normal_and_resource_limit(self):
        s = self.supervisor('import resource; print(resource.getrlimit(resource.RLIMIT_AS)[0]); import sys; print("err", file=sys.stderr)')
        r = s.run()
        self.assertEqual(r['returncode'], 0)
        self.assertEqual(r['stdout'], b'268435456\n')
        self.assertEqual(r['stderr'], b'err\n')
        self.assertEqual(r['cleanup'], 'CONFIRMED')
        self.assertEqual(s.state, 'IDLE')

    def test_ignored_term_escalates_and_reaps(self):
        s = self.supervisor('import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); print("ready",flush=True); time.sleep(10)', wall_seconds=.5, grace_seconds=.1, cleanup_seconds=.5)
        r = s.run()
        self.assertIn(b'ready', r['stdout'])
        self.assertEqual(r['stop_reason'], 'WALL_DEADLINE')
        self.assertEqual(r['returncode'], -signal.SIGKILL)
        self.assertEqual(r['signals_requested'], ['SIGTERM','SIGKILL'])
        self.assertEqual(r['signal_cause'], 'NOT_DETERMINED')
        self.assertEqual(r['cleanup'], 'CONFIRMED')
        with self.assertRaises(ChildProcessError): os.waitpid(r['pid'], os.WNOHANG)

    def test_external_signal_not_classified_as_timeout_or_oom(self):
        s = self.supervisor('import time; time.sleep(10)', wall_seconds=3)
        original = subprocess.Popen
        children=[]; ready=threading.Event()
        def launch(*a, **kw):
            child=original(*a, **kw); children.append(child); ready.set(); return child
        with patch('supervisor.process_core.subprocess.Popen', side_effect=launch):
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(s.run)
                self.assertTrue(ready.wait(2))
                self.assertEqual(s.run()['status'], 'BUSY')
                self.assertEqual(len(children), 1)
                try:
                    os.kill(children[0].pid, signal.SIGKILL)
                    r=future.result(timeout=4)
                finally:
                    if children[0].poll() is None: children[0].kill()
                    children[0].wait(timeout=2)
        self.assertEqual(r['returncode'], -9)
        self.assertIsNone(r['stop_reason'])
        self.assertEqual(r['signal_cause'], 'NOT_DETERMINED')
        self.assertEqual(r['cleanup'], 'CONFIRMED')

    def test_uncertain_wait_blocks_next_run(self):
        s=self.supervisor('import time; time.sleep(10)',wall_seconds=.2,grace_seconds=.05,cleanup_seconds=.1)
        children=[]; original=subprocess.Popen
        def launch(*a, **kw):
            child=original(*a, **kw); children.append(child); return child
        try:
            with patch('supervisor.process_core.subprocess.Popen',side_effect=launch), patch.object(s,'_wait',side_effect=OSError('injected wait observation failure')):
                r=s.run()
                second=s.run()
            self.assertEqual(r['cleanup'],'UNCONFIRMED')
            self.assertEqual(s.state,'INFRA_LOCK')
            self.assertEqual(second['status'],'INFRA_LOCK')
            self.assertEqual(len(children),1)
        finally:
            for child in children:
                if child.poll() is None: child.kill()
                child.wait(timeout=2)

    def test_interrupted_cleanup_latches_lock(self):
        for interruption in (KeyboardInterrupt, SystemExit):
            with self.subTest(interruption=interruption.__name__):
                s=self.supervisor('import time; time.sleep(10)',wall_seconds=.1)
                children=[]; original=subprocess.Popen
                def launch(*a, **kw):
                    child=original(*a, **kw); children.append(child); return child
                try:
                    with patch('supervisor.process_core.subprocess.Popen',side_effect=launch), patch.object(s,'_wait',side_effect=interruption):
                        with self.assertRaises(interruption): s.run()
                        self.assertEqual(s.state,'INFRA_LOCK')
                        self.assertEqual(s.run()['status'],'INFRA_LOCK')
                        self.assertEqual(len(children),1)
                finally:
                    for child in children:
                        if child.poll() is None: child.kill()
                        child.wait(timeout=2)

    def test_uncertain_creation_interruption_blocks_new_launch(self):
        s=self.supervisor('import time; time.sleep(10)')
        children=[]; original=subprocess.Popen
        def interrupted_launch(*a, **kw):
            child=original(*a, **kw); children.append(child)
            raise KeyboardInterrupt('injected before child assignment')
        try:
            with patch('supervisor.process_core.subprocess.Popen',side_effect=interrupted_launch):
                with self.assertRaises(KeyboardInterrupt): s.run()
                self.assertEqual(s.state,'INFRA_LOCK')
                self.assertEqual(s.run()['status'],'INFRA_LOCK')
                self.assertEqual(len(children),1)
        finally:
            for child in children:
                if child.poll() is None: child.kill()
                child.wait(timeout=2)
                child.stdout.close()
                child.stderr.close()

    def test_output_cap(self):
        r=self.supervisor('import os,time; os.write(1,b"x"*4096); time.sleep(10)',stdout_bytes=128,wall_seconds=2).run()
        self.assertEqual(r['stop_reason'],'OUTPUT_LIMIT')
        self.assertEqual(len(r['stdout']),128)
        self.assertEqual(r['cleanup'],'CONFIRMED')

    def test_invalid_limits_no_launch(self):
        for opts in ({'wall_seconds':0},{'wall_seconds':float('nan')},{'grace_seconds':True},{'memory_mib':0},{'stdout_bytes':-1}):
            with self.subTest(opts=opts), patch('supervisor.process_core.subprocess.Popen') as launch:
                with self.assertRaises(ValueError): self.supervisor('pass',**opts)
                launch.assert_not_called()

    def test_missing_executable(self):
        with self.assertRaises(ValueError): ProcessSupervisor(('/missing/executable',),Limits())

    def test_readme_current_state(self):
        text=(ROOT/'README.md').read_text()
        self.assertIn('WU-SUP-CORE-001',text)
        self.assertNotIn('corrección documental R3-001 probada, nuevo RDD pendiente',text)

if __name__=='__main__': unittest.main(verbosity=2)
