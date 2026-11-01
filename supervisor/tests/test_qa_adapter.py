import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from supervisor.qa_adapter import QASupervisor
from supervisor.process_core import ProcessSupervisor, Limits

ROOT = Path(__file__).resolve().parents[2]

def payload(code=0):
    return {'execution_status': 'INFRA_FAILURE' if code == 3 else 'COMPLETED',
            'document_validation': {0:'VALID',2:'INVALID',3:'NOT_ASSESSED'}[code],
            'proposed_event': {0:'RECORD_GAP_OR_STALE',2:'REJECT_INPUT',3:None}[code],
            'failure_observation': {'status':'NO_DECLARATIONS_FOUND','scan_status':'COMPLETE',
                'declared_failure_count':0,'scanned_records':0,'evidence_verification':'NOT_ESTABLISHED'},
            'authority_verification':'NOT_PERFORMED','execution_authorized':False,'execution_performed':False}

def observed(code=0, data=None):
    return {'status':'EXITED','launched':True,'returncode':code,'cleanup':'CONFIRMED',
            'stop_reason':None,'capture_complete':True,'capture_truncated':{'stdout':False,'stderr':False},
            'stdout':json.dumps(payload(code) if data is None else data).encode(), 'stderr':b'warning\n'}

class AdapterTests(unittest.TestCase):
    def make(self): return QASupervisor('/tmp/report.json','/tmp')
    def test_preserves_selected_virtualenv_interpreter(self):
        self.assertEqual(self.make()._core.command[0], str(Path(sys.executable).absolute()))
    def test_channels_and_gap(self):
        adapter=self.make()
        with patch.object(adapter._core,'run',return_value=observed()): r=adapter.run()
        self.assertEqual(r['result_admission'],'ACCEPTED')
        self.assertEqual(r['checker_result']['proposed_event'],'RECORD_GAP_OR_STALE')
        self.assertEqual(r['process']['stderr'],b'warning\n')
        self.assertFalse(r['execution_authorized'])
    def test_exit_two(self):
        adapter=self.make()
        with patch.object(adapter._core,'run',return_value=observed(2)): r=adapter.run()
        self.assertEqual(r['document_admission'],'REJECT_INPUT')
    def test_infra_and_signal(self):
        for code in (3,-9):
            obs=observed(3);obs['returncode']=code
            adapter=self.make()
            with patch.object(adapter._core,'run',return_value=obs): r=adapter.run()
            self.assertEqual(r['execution_status'],'INFRA_FAILURE')
            self.assertEqual(r['cause'],'NOT_DETERMINED')
            self.assertEqual(r['document_admission'],'NOT_ASSESSED')
    def test_partial_escalates(self):
        doc=payload(2);doc['failure_observation']['scan_status']='PARTIAL'
        adapter=self.make()
        with patch.object(adapter._core,'run',return_value=observed(2,doc)): r=adapter.run()
        self.assertTrue(r['human_review_required'])
    def test_bad_protocol(self):
        for raw in (b'{}',b'{"x":1,"x":2}',b'['*100+b']'*100,b'not json'):
            obs=observed();obs['stdout']=raw;adapter=self.make()
            with patch.object(adapter._core,'run',return_value=obs): r=adapter.run()
            self.assertEqual(r['result_admission'],'REJECT_INFRA')
    def test_incoherent_exit(self):
        obs=observed();obs['returncode']=2;adapter=self.make()
        with patch.object(adapter._core,'run',return_value=obs): r=adapter.run()
        self.assertEqual(r['result_admission'],'REJECT_INFRA')
    def test_incomplete_capture(self):
        obs=observed();obs['capture_complete']=False;adapter=self.make()
        with patch.object(adapter._core,'run',return_value=obs): r=adapter.run()
        self.assertEqual(r['execution_status'],'INFRA_FAILURE')
    def test_lock_latches_no_second_launch(self):
        obs=observed();obs['cleanup']='UNCONFIRMED';adapter=self.make()
        with patch.object(adapter._core,'run',return_value=obs) as run:
            self.assertEqual(adapter.run()['state'],'INFRA_LOCK')
            self.assertEqual(adapter.run()['state'],'INFRA_LOCK')
            self.assertEqual(run.call_count,1)
    def test_real_channels(self):
        adapter=self.make()
        script='import sys; print('+repr(json.dumps(payload()))+'); sys.stderr.write("warning\\n")'
        adapter._core=ProcessSupervisor((sys.executable,'-B','-c',script))
        r=adapter.run()
        self.assertEqual(r['result_admission'],'ACCEPTED')
        self.assertEqual(r['process']['stderr'],b'warning\n')
    def test_real_signal_and_timeout(self):
        for script,limits in [('import os,signal; os.kill(os.getpid(),signal.SIGKILL)',Limits()),
                              ('import time; time.sleep(2)',Limits(wall_seconds=.15,grace_seconds=.1,cleanup_seconds=.1))]:
            adapter=self.make()
            adapter._core=ProcessSupervisor((sys.executable,'-B','-c',script),limits)
            r=adapter.run()
            self.assertEqual(r['execution_status'],'INFRA_FAILURE')
            self.assertEqual(r['cause'],'NOT_DETERMINED')
            self.assertEqual(r['process']['cleanup'],'CONFIRMED')
        self.assertEqual(r['process']['stop_reason'],'WALL_DEADLINE')
    def test_real_checker_invalid_document(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'report.json';path.write_text('{}')
            r=QASupervisor(path,temp).run()
        self.assertEqual(r['process']['returncode'],2)
        self.assertEqual(r['document_admission'],'REJECT_INPUT')
        self.assertTrue(r['human_review_required'])

if __name__=='__main__': unittest.main()
