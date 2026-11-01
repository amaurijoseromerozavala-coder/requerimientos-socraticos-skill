import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
import probe_environment as probe
import activation_preflight as preflight

class StorageScopeTests(unittest.TestCase):
    def test_wsl_visible_space_not_host(self):
        with patch.object(probe.platform,'release',return_value='6-microsoft-WSL2'):
            doc=probe.probe('/tmp')
        storage=doc['storage']
        self.assertEqual(storage['scope'],'VISIBLE_FILESYSTEM_ONLY')
        self.assertEqual(storage['host_volume']['status'],'UNKNOWN')
        self.assertIsNone(storage['host_volume']['free_bytes'])
        self.assertFalse(storage['expansion_authorized'])

    def test_storage_request_blocks_even_if_memory_viable(self):
        ready={'status':'READY_FOR_LIVE_ADMISSION','execution':{'workers':'LIVE_GATE_REQUIRED'},'capabilities':{'workers':'CANDIDATE_SUBJECT_TO_LIVE_ADMISSION'}}
        with patch.object(preflight,'_evaluate_memory',return_value=ready):
            report=preflight.evaluate('/tmp',caller_scope='EXTERNAL_CALLER',storage_required_bytes=1024)
        self.assertEqual(report['storage_admission']['status'],'BLOCKED_HOST_STORAGE_UNKNOWN')
        self.assertEqual(report['status'],'INCONCLUSIVE')
        self.assertEqual(report['execution']['workers'],'BLOCKED')
        self.assertFalse(report['storage_admission']['authorized'])

    def test_no_request_not_disk_permission(self):
        report=preflight.evaluate('/tmp',caller_scope='EXTERNAL_CALLER')
        self.assertEqual(report['schema_version'],'1.1.0')
        self.assertEqual(report['storage_admission']['status'],'NOT_ASSESSED')
        self.assertFalse(report['storage_admission']['authorized'])
        self.assertEqual(report['storage_admission']['readiness_scope'],'MEMORY_ROLE_VIABILITY_ONLY')

    def test_invalid_request(self):
        for value in [0,-1,True,'100',1.5]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                preflight.evaluate('/tmp',storage_required_bytes=value)

    def test_cli_blocks_structurally(self):
        r=subprocess.run([sys.executable,'-B',str(SCRIPTS/'activation_preflight.py'),'--path','/tmp','--storage-required-bytes','1024'],capture_output=True,text=True,timeout=5)
        self.assertEqual(r.returncode,3)
        self.assertEqual(json.loads(r.stdout)['storage_admission']['status'],'BLOCKED_HOST_STORAGE_UNKNOWN')

    def test_preflight_reports_official_source_clone(self):
        root = SCRIPTS.parents[2]
        origin = 'https://github.com/amaurijoseromerozavala-coder/requerimientos-socraticos-skill.git'
        commands = [
            ['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
            ['git', '-C', str(root), 'config', '--get', 'remote.origin.url'],
            ['git', '-C', str(root), 'rev-parse', '--verify', 'HEAD^{commit}'],
        ]
        for oid in ('a' * 40, 'b' * 64):
            responses = [subprocess.CompletedProcess(command, 0, value + '\n', '')
                         for command, value in zip(commands, (str(root), origin, oid))]
            with self.subTest(oid_length=len(oid)), patch.object(
                    preflight.subprocess, 'run', side_effect=responses) as run:
                report = preflight.evaluate('/tmp', caller_scope='EXTERNAL_CALLER')
            self.assertEqual(report['source_checkout']['status'], 'VERIFIED_LOCAL_CLONE')
            self.assertTrue(report['source_checkout']['origin_match'])
            self.assertEqual(report['source_checkout']['head_commit'], oid)
            self.assertEqual([call.args[0] for call in run.call_args_list], commands)

    def test_source_checkout_rejects_unlisted_origin(self):
        root = SCRIPTS.parents[2]
        values = (str(root), 'https://example.invalid/fork.git', 'a' * 40)
        responses = [subprocess.CompletedProcess([], 0, value + '\n', '')
                     for value in values]
        with patch.object(preflight.subprocess, 'run', side_effect=responses):
            result = preflight.source_checkout()
        self.assertEqual(result['status'], 'CLONE_UNVERIFIED')
        self.assertFalse(result['origin_match'])
        self.assertIsNone(result['head_commit'])

    def test_unverified_source_blocks_workers_not_documents(self):
        with patch.object(preflight,'source_checkout',return_value={'status':'CLONE_UNVERIFIED','origin_match':False,'head_commit':None}):
            report=preflight.evaluate('/tmp',caller_scope='EXTERNAL_CALLER')
        self.assertEqual(report['status'],'INCONCLUSIVE')
        self.assertEqual(report['execution']['workers'],'BLOCKED')
        self.assertEqual(report['capabilities']['document_analysis'],'AVAILABLE')

class StorageReviewTests(unittest.TestCase):
    def test_clone_requires_commit_object(self):
        root=SCRIPTS.parents[2]
        origin='https://github.com/amaurijoseromerozavala-coder/requerimientos-socraticos-skill.git'
        def command(args, **kwargs):
            if args[-1]=='HEAD^{commit}':
                return subprocess.CompletedProcess(args,1,'','missing object')
            value=str(root) if '--show-toplevel' in args else origin if '--get' in args else 'a'*40
            return subprocess.CompletedProcess(args,0,value+'\n','')
        with patch.object(preflight.subprocess,'run',side_effect=command):
            self.assertEqual(preflight.source_checkout()['status'],'CLONE_UNVERIFIED')

    def test_schema_rejects_contradictory_admission(self):
        import copy
        import jsonschema
        root=SCRIPTS.parents[2]
        schema=json.loads((SCRIPTS.parent/'assets/activation-preflight.schema.json').read_text())
        base=json.loads((root/'docs/skill-audit/wsl-storage/storage-block.json').read_text())
        jsonschema.validate(base,schema)
        for mode in ('ready','workers','unverified','request'):
            doc=copy.deepcopy(base)
            if mode=='ready': doc['status']='READY_FOR_LIVE_ADMISSION'
            elif mode=='workers': doc['execution']['workers']='LIVE_GATE_REQUIRED'
            elif mode=='unverified':
                doc['storage_admission']['requested_bytes']=None
                doc['storage_admission']['status']='NOT_ASSESSED'
                doc['source_checkout']['status']='CLONE_UNVERIFIED'
                doc['status']='READY_FOR_LIVE_ADMISSION'
            else: doc['storage_admission']['status']='NOT_ASSESSED'
            with self.subTest(mode=mode),self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(doc,schema)

if __name__=='__main__': unittest.main(verbosity=2)
