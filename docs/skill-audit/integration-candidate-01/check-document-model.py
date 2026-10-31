"""Check the fixed documentary integration model; stdout is a fresh result.

Does not rewrite historical receipts. This is not a supervisor implementation.
"""
import json
import itertools
import hashlib
from pathlib import Path

# Independent scope oracle: INT-D20..23 and Q-INT-T01, reviewed projection v0.1.
# Changing this vocabulary requires a new contract review, not inferred acceptance.
REVOCATION_STATES = frozenset({
    'ISOLATED', 'VERIFYING', 'WAIT_AUTHORIZATION', 'READY',
    'INCORPORATING', 'RECOVERING', 'INCORPORATED', 'BLOCKED', 'REBASE_REQUIRED',
})
REJECTION_DEFAULT = 'REJECT_PRESERVE_DOMAIN_STATE; bounded audit may record rejection'


def validate_global_revocation_contract(fsm):
    """Validate structure/priority declarations, not execution of prose effects."""
    def need(condition, detail):
        if not condition:
            raise ValueError('GLOBAL_REVOCATION_CONTRACT: ' + detail)

    def exact_states(value):
        return (isinstance(value, list)
                and all(isinstance(x, str) for x in value)
                and len(value) == len(REVOCATION_STATES)
                and set(value) == REVOCATION_STATES)

    need(isinstance(fsm, dict), 'FSM_OBJECT_REQUIRED')
    need(exact_states(fsm.get('states')), 'FIXED_STATE_SCOPE_REQUIRED')
    events = fsm.get('events')
    need(isinstance(events, list) and events.count('revocation_accepted') == 1,
         'REVOCATION_EVENT_REQUIRED_ONCE')
    handlers = fsm.get('global_handlers')
    need(isinstance(handlers, list) and len(handlers) == 1
         and isinstance(handlers[0], dict), 'ONE_GLOBAL_HANDLER_REQUIRED')
    handler = handlers[0]
    need(handler.get('event') == 'revocation_accepted', 'REVOCATION_EVENT_MISMATCH')
    need(handler.get('priority') == 'BEFORE_LOCAL_TRANSITION', 'PRIORITY_MISMATCH')
    need(exact_states(handler.get('applies_to')), 'ALL_STATES_REQUIRED_ONCE')
    need(fsm.get('default') == REJECTION_DEFAULT, 'REJECTION_DEFAULT_MISMATCH')


def main():
    r=Path(__file__).resolve().parents[3];p=r/'docs/requirements/integracion-requisitos-qa-supervisor/candidato-v0.1';a=r/'docs/skill-audit/integration-candidate-01'
    read=lambda n:json.loads((p/n).read_text())
    req=read('requirements.json');ledger=json.loads((p.parent/'decisiones-confirmadas.json').read_text());ids={d['id'] for d in ledger['decisions']};assert len(req['requirements'])==23
    assert {s for x in req['requirements'] for s in x['decision_refs']}==ids
    assert all(x['ears'] and x['falsifier'] and x['implementation_verification']=='NOT_RUN' for x in req['requirements'])
    assert req['source_sha256']==hashlib.sha256((p.parent/'decisiones-confirmadas.json').read_bytes()).hexdigest()
    g=read('incorporation-gate.json')
    def evaluate(inp,rules):
     if set(inp)!=set(g['variables']) or any(type(v)!=bool for v in inp.values()):return 'BLOCK_UNKNOWN'
     for rule in rules:
      if 'when_false_any' in rule:matches=any(not inp[x] for x in rule['when_false_any'])
      elif rule.get('otherwise'):matches=True
      else:matches=all(inp[x] for x in rule.get('when_true',[])) and all(not inp[x] for x in rule.get('when_false',[]))
      if matches:return rule['result']
     return 'BLOCK_UNKNOWN'
    checks=[];mutant=[x for x in g['rules'] if x['id']!='G2'];detected=0;counts={}
    for bits in itertools.product([False,True],repeat=7):
     x=dict(zip(g['variables'],bits));actual=evaluate(x,g['rules']);counts[actual]=counts.get(actual,0)+1
     # Independent oracle for admission precedence; source is confirmed policies, not emitted labels.
     mandatory_ok=all(bits[:5]);want='BLOCK' if not mandatory_ok else 'WAIT_NEW_AUTHORIZATION' if bits[5] and not bits[6] else 'ELIGIBLE_NOT_EXECUTED'
     assert actual==want,(x,actual,want)
     if evaluate(x,mutant)!=want:detected+=1
    assert detected==1
    unknown={x:True for x in g['variables']};unknown['base_unchanged']='UNKNOWN';assert evaluate(unknown,g['rules'])=='BLOCK_UNKNOWN'
    f=read('fsm.json');validate_global_revocation_contract(f);keys=[(t['from'],t['event']) for t in f['transitions']];assert len(keys)==len(set(keys));assert all(t['from'] in f['states'] and t['to'] in f['states'] and t['event'] in f['events'] for t in f['transitions'])
    trans={(t['from'],t['event']):t['to'] for t in f['transitions']}
    assert trans['INCORPORATING','revocation_accepted']=='RECOVERING';assert trans['RECOVERING','restoration_unknown_or_unsafe']=='BLOCKED';assert trans['READY','base_changed']=='REBASE_REQUIRED'
    reachable={f['initial']}
    while True:
     updated=reachable|{t['to'] for t in f['transitions'] if t['from'] in reachable}
     if updated==reachable:break
     reachable=updated
    assert reachable==set(f['states'])
    out={'result':'PASS_WITHIN_DOCUMENT_MODEL_SCOPE','requirements_traced':23,'boolean_valuations':128,'gate_results':counts,'unknown_input_rejected':True,'negative_control_removed_revocation_rule_detected':detected,'projection_unique_edges':len(keys),'projection_reachable_states':len(reachable),'projection_not_global_fsm':True,'red_origin':'Missing4documents recorded before creation; mutations are negative controls, not pre-edit RED execution.','limits':['No runtime execution, filesystem exclusion, durable recovery or hardware verified.','Gate assumptions and qualified events require implementation and observational verification.','Reachability is graph-only, not feasibility or liveness.']}
    out['global_revocation_contract'] = 'PASS_DOCUMENTARY_STRUCTURE_ONLY'
    out['limits'].append('Global handler labels and coverage checked; effects and OS temporal ordering not executed.')
    print(json.dumps(out,indent=2))


if __name__ == '__main__':
    main()
