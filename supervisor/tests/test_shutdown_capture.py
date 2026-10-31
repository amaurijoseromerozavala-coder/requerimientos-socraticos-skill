"""Real bounded child shutdown I/O; no hardware load calibration."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from supervisor.process_core import ProcessSupervisor, Limits

class ShutdownCaptureTests(unittest.TestCase):
    def run_shutdown(self, out_count, err_count, **caps):
        script=f'''import os,signal,time

def shutdown(*args):
    for fd, count, value in [(1,{out_count},b"O"),(2,{err_count},b"E")]:
        remaining=count
        while remaining:
            block=value*min(4096,remaining)
            remaining-=os.write(fd,block)
    raise SystemExit(0)
signal.signal(signal.SIGTERM,shutdown)
os.write(1,b"READY\\n")
time.sleep(10)
'''
        result=ProcessSupervisor((sys.executable,'-B','-c',script),Limits(wall_seconds=.4,grace_seconds=1,cleanup_seconds=.5,**caps)).run()
        self.assertTrue(result['stdout'].startswith(b'READY\n'))
        self.assertEqual(result['stop_reason'],'WALL_DEADLINE')
        self.assertEqual(result['returncode'],0)
        self.assertEqual(result['cleanup'],'CONFIRMED')
        self.assertEqual(result['signals_requested'],['SIGTERM'])
        return result

    def test_shutdown_diagnostics_both_channels(self):
        r=self.run_shutdown(64,64)
        self.assertEqual(r['stdout'],b'READY\n'+b'O'*64)
        self.assertEqual(r['stderr'],b'E'*64)
        self.assertTrue(r['capture_complete'])
        self.assertEqual(r['capture_truncated'],{'stdout':False,'stderr':False})

    def test_shutdown_larger_than_pipe_capacity(self):
        r=self.run_shutdown(200000,50000)
        self.assertEqual(len(r['stdout']),200006)
        self.assertEqual(len(r['stderr']),50000)
        self.assertTrue(r['capture_complete'])

    def test_discard_excess_without_blocking_shutdown(self):
        r=self.run_shutdown(200000,200000,stdout_bytes=128,stderr_bytes=128)
        self.assertEqual(len(r['stdout']),128)
        self.assertEqual(len(r['stderr']),128)
        self.assertEqual(r['capture_truncated'],{'stdout':True,'stderr':True})
        self.assertTrue(r['capture_complete'])

    def test_active_shutdown_writer_does_not_extend_deadline(self):
        script = """import os,signal,time

def shutdown(*args):
    for _ in range(100):
        os.write(2,b'E'*4096)
        time.sleep(.01)
    raise SystemExit(0)
signal.signal(signal.SIGTERM,shutdown)
os.write(1,b'READY\\n')
time.sleep(10)
"""
        r=ProcessSupervisor((sys.executable,'-B','-c',script),Limits(wall_seconds=.4,grace_seconds=.15,cleanup_seconds=.5,stderr_bytes=128)).run()
        self.assertEqual(r['stop_reason'],'WALL_DEADLINE')
        self.assertEqual(r['signals_requested'],['SIGTERM','SIGKILL'])
        self.assertEqual(r['returncode'],-9)
        self.assertEqual(r['cleanup'],'CONFIRMED')
        self.assertEqual(len(r['stderr']),128)
        self.assertTrue(r['capture_truncated']['stderr'])
        self.assertTrue(r['capture_complete'])
        # Generous scheduling tolerance, not a real-time guarantee.
        self.assertLess(r['elapsed_seconds'],3)

if __name__=='__main__': unittest.main(verbosity=2)
