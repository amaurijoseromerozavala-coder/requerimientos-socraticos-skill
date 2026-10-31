import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
f=json.loads((p/'fsm-propuesta.json').read_text());d=json.loads((p/'prd-draft.json').read_text());t={(x['from'],x['event']):x['to'] for x in f['transitions']};checks={
'cleanup_enters_lock':t.get(('STOPPING','cleanup_deadline'))=='INFRA_LOCK',
'lock_blocks_new_request':t.get(('INFRA_LOCK','request'))=='INFRA_LOCK',
'ack_does_not_unlock':t.get(('INFRA_LOCK','human_ack_only'))=='INFRA_LOCK',
'reconciliation_required':t.get(('INFRA_LOCK','termination_reconciled'))=='CLASSIFYING',
'no_lock_to_running':not any(x['from']=='INFRA_LOCK' and x['to']=='RUNNING' for x in f['transitions']),
'rejection_types':set(d.get('result_contract',{}).get('failure_classes',[]))=={'REJECT_INPUT','INFRA_FAILURE','PROTOCOL_FAILURE'},
'optional_os_diagnostics':d.get('os_diagnostics',{}).get('required_for_completion') is False,
'no_elevation':d.get('os_diagnostics',{}).get('privilege_elevation') is False,
'invoker_confirmed':d['supervisor_mode']['value']=='LOCAL_QA_LAUNCHER'}
print(json.dumps({'scope':'document/model assertions, not execution tests','checks':checks,'pass':all(checks.values())},indent=2));raise SystemExit(0 if all(checks.values()) else 1)
