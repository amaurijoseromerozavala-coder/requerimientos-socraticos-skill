"""Bounded cloud experiments; NOT the physical WSL thrashing acceptance test."""
import concurrent.futures
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path('/workspace/replica-gentle-ai')
SKILL = ROOT / 'skills/requerimientos-socraticos'
AUDIT = Path(__file__).resolve().parent
SCRIPT = SKILL / 'scripts/requirements_guard.py'
spec = importlib.util.spec_from_file_location('guard', SCRIPT)
g = importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
sys.path.insert(0, str(SKILL / 'tests'))
from test_interview import ContractTests
report = {'scope': 'Temporary copies on cloud; real QA untouched; no RAM/swap saturation', 'hardware_acceptance': 'NOT_RUN_TARGET_UNAVAILABLE'}
with tempfile.TemporaryDirectory() as td:
    base = Path(td); source = base / 'source';source.mkdir()
    ContractTests().stage_prd(source)
    ContractTests().set_synthetic_ready(source / 'prd.json')
    nested = source / 'z-later' / 'sub';nested.mkdir(parents=True)
    (nested / 'watched.txt').write_bytes(b'original nested content')
    fakebin = base / 'fakebin';fakebin.mkdir()
    marker = base / 'consumer-called'
    consumer = fakebin / 'requirements-consumer'
    consumer.write_text('#!/bin/sh\ntouch "$CONSUMER_MARKER"\nexit 0\n');consumer.chmod(0o700)
    env = os.environ.copy();env.update(CI='true', GITHUB_ACTIONS='true', REQUIREMENTS_CONSUMER=str(consumer), CONSUMER_MARKER=str(marker), PATH=str(fakebin)+os.pathsep+os.environ.get('PATH',''))
    command = [sys.executable, '-B', str(SCRIPT), 'advance', str(source), '--prd', 'prd.json']
    p = subprocess.run(command, env=env, capture_output=True, text=True, timeout=20)
    output = json.loads(p.stdout)
    assert p.returncode == 1 and output['status'] == 'BLOCKED' and 'DOWNSTREAM_NOT_CONFIGURED' in output['error'] and not marker.exists(), (p.returncode, p.stdout, p.stderr)
    report['fake_ci_consumer'] = {'exit_code': p.returncode, 'output':output, 'fake_consumer_called':marker.exists(), 'result':'BYPASS_NOT_OBSERVED'}

    observed = []
    original_add = g.Observation.add
    original_read = g.os.read
    directories = {str(p) for p in source.rglob('*') if p.is_dir()} | {str(source)}
    def add(self, path):
        original_add(self, path);observed.append(str(path))
    reads = []
    def read(fd, size):
        if stat.S_ISREG(os.fstat(fd).st_mode):
            assert directories <= set(observed), 'Content read before all existing directories watched'
            reads.append(True)
        return original_read(fd,size)
    with patch.object(g.Observation,'add',add),patch.object(g.os,'read',read):
        g.observe(source)
    assert reads
    report['ordering'] = {'all_existing_directory_watches_precede_first_content_read':True,'content_read_calls':len(reads),'directory_count':len(directories)}

    target = nested / 'watched.txt';before = target.read_bytes()
    fired = []
    def read_with_fork_writer(fd,size):
        if not fired and stat.S_ISREG(os.fstat(fd).st_mode):
            fired.append(True)
            subprocess.run(['/tmp/requirements-fork-writer',str(target)],check=True,timeout=5)
        return original_read(fd,size)
    try:
        with patch.object(g.os,'read',read_with_fork_writer):g.observe(source)
    except g.GuardError as error:
        assert 'OBSERVED_CHANGE' in str(error), str(error)
        report['fork_writer_during_content_read']={'result':'BLOCKED','error':str(error),'writer_executed':bool(fired),'content_restored':target.read_bytes()==before}
    else:raise AssertionError('Fork mutation escaped observation')

    def run(_):
        began = time.monotonic()
        p = subprocess.run([sys.executable,'-B',str(SCRIPT),'validate',str(source),'--prd','prd.json','--timeout','15'],capture_output=True,text=True,timeout=20)
        return {'exit_code':p.returncode,'seconds':time.monotonic()-began,'output':json.loads(p.stdout)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:results=list(pool.map(run,range(20)))
    assert all(x['exit_code']==0 for x in results), results
    assert len({x['output']['tree_sha256'] for x in results})==1
    report['twenty_cloud_validators']={'processes':20,'all_exit_zero':True,'one_tree_identity':True,'max_seconds':max(x['seconds'] for x in results),'memory_pressure':'NOT_INDUCED','physical_hardware_inference':'NONE'}

report['guard_sha256']=hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
(AUDIT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
