"""Document contract checks; fixtures are synthetic and never execute applications."""
import copy,json,hashlib,sys,contextlib,io
from pathlib import Path
from unittest.mock import patch
from jsonschema import Draft202012Validator
p=Path(__file__).resolve().parents[1];root=p.parents[2]
sys.path.insert(0,str(root/'skills/qa-inquisidor/tests'))
from test_report import ReportChecks,qa
schema=json.loads((p/'checker-output.schema.json').read_text());Draft202012Validator.check_schema(schema);v=Draft202012Validator(schema)
def admitted(d):
 if list(v.iter_errors(d)):return False
 b=d['payload'];o=b['failure_observation'];c=o['declared_failure_count']
 if c is not None and c>o['scanned_records']:return False
 if 'gaps' in b:
  if not set(b['gaps'])<=set(b['required_obligations']):return False
  if b['material_gap']!=bool(b['gap_reasons']):return False
  if any(len(b[k])!=len(set(b[k])) for k in ('required_obligations','gaps','failure_cases')):return False
 return True
f=ReportChecks();f.setUp();cases=[]
try:
 def emit(doc,raw=None,error=None):
  path=f.root/'report.json';path.write_text(json.dumps(doc) if raw is None else raw)
  out=io.StringIO()
  with contextlib.redirect_stdout(out):
   if error:
    with patch.object(qa,'read_regular',side_effect=error):code=qa.main(['--report',str(path),'--evidence-root',str(f.root)])
   else:code=qa.main(['--report',str(path),'--evidence-root',str(f.root)])
  return {'returncode':code,'payload':json.loads(out.getvalue())}
 good=emit(f.doc);cases.append(('actual_checker_synthetic_success',good,True))
 bad=copy.deepcopy(f.doc);bad['evidence'][0]['outcome']='FAIL';cases.append(('actual_checker_contradiction',emit(bad),True))
 cases.append(('actual_checker_invalid_json',emit({},'{'),True))
 cases.append(('actual_checker_controlled_oserror',emit({},error=OSError('controlled')),True))
 partial=copy.deepcopy(f.doc);partial['evidence']=[{'outcome':'PASS'}]*128+[{'outcome':'FAIL'}];cases.append(('actual_checker_partial',emit(partial),True))
 for name,fn in [('wrong_exit',lambda x:x.update(returncode=2)),('extra_field',lambda x:x['payload'].update(extra=1)),('authorization_true',lambda x:x['payload'].update(execution_authorized=True)),('wrong_verdict',lambda x:x['payload'].update(verdict='INCONCLUSIVE')),('gap_without_gap',lambda x:x['payload'].update(proposed_event='RECORD_GAP_OR_STALE',verdict='INCONCLUSIVE')),('count_exceeds_scanned',lambda x:x['payload']['failure_observation'].update(status='UNVERIFIED_DECLARATIONS_FOUND',declared_failure_count=2,scanned_records=1)),('partial_as_absence',lambda x:x['payload']['failure_observation'].update(scan_status='PARTIAL')),('missing_field',lambda x:x['payload'].pop('execution_authorized'))]:
  x=copy.deepcopy(good);fn(x);cases.append((name,x,False))
 # Scenario-specific oracles are defined independently of observed output.
 expected_states={
 'actual_checker_synthetic_success':(0,'COMPLETED','VALID','RECORD_CURRENT_SUCCESS','SUPPORTED_WITHIN_DECLARED_EVIDENCE','NO_DECLARATIONS_FOUND','COMPLETE',0),
 'actual_checker_contradiction':(2,'COMPLETED','INVALID','REJECT_INPUT',None,'UNVERIFIED_DECLARATIONS_FOUND','COMPLETE',1),
 'actual_checker_invalid_json':(2,'COMPLETED','INVALID','REJECT_INPUT',None,'NOT_ASSESSED','NOT_ASSESSED',None),
 'actual_checker_controlled_oserror':(3,'INFRA_FAILURE','NOT_ASSESSED',None,None,'NOT_ASSESSED','NOT_ASSESSED',None),
 'actual_checker_partial':(2,'COMPLETED','INVALID','REJECT_INPUT',None,'NOT_ASSESSED','PARTIAL',0)}
 def state(x):
  b=x['payload'];o=b['failure_observation']
  return (x['returncode'],b['execution_status'],b['document_validation'],b.get('proposed_event'),b.get('verdict'),o['status'],o['scan_status'],o['declared_failure_count'])
 results=[]
 for n,x,expected in cases:
  wanted=expected_states.get(n);actual=state(x) if wanted else None
  results.append({'case':n,'expected_admission':expected,'actual_admission':admitted(x),'expected_state':wanted,'actual_state':actual,'pass':admitted(x)==expected and (wanted is None or actual==wanted)})
 infra=next(x for n,x,e in cases if n=='actual_checker_controlled_oserror')
 repeated_infra_rejected=[n for n,wanted in expected_states.items() if state(infra)!=wanted]
 assert len(repeated_infra_rejected)==4, repeated_infra_rejected
 # Negative control: permissive schema accepts an unknown field rejected by the strict contract.
 mutant=copy.deepcopy(schema)
 for branch in mutant['oneOf']:branch['properties']['payload']['additionalProperties']=True
 x=next(x for n,x,e in cases if n=='extra_field');control=not list(Draft202012Validator(mutant).iter_errors(x));assert control
 out={'method':'Local checker helpers over bounded synthetic files; no supervisor implementation or resource pressure','schema_sha256':hashlib.sha256((p/'checker-output.schema.json').read_bytes()).hexdigest(),'cases':results,'negative_control_uniform_infra_rejected_for':repeated_infra_rejected,'negative_control_permissive_schema_accepts_extra_field':control,'pass':all(x['pass'] for x in results)}
 (p/'verification/output-contract-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['pass']
finally:f.doCleanups()
