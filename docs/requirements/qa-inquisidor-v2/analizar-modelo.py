"""Static enumeration of a documentary abstraction; never executes target tests."""
import copy
import hashlib
import itertools
import json
from collections import deque
from pathlib import Path

BASE=Path(__file__).resolve().parent

def enumerate_model(model):
    def key(c):return json.dumps(c,sort_keys=True)
    initial=model['initial'];queue=deque([initial]);seen={key(initial)};witness={key(initial):[]};deliveries={};accepted=0;rejected=0;delivered_inconclusive=False
    while queue:
        c=queue.popleft()
        if c['verdict']=='PASS_WITHIN_SCOPE':
            assert c['context_ready'] and c['evidence_current'] and c['material_success'] and not c['material_gap'] and not c['valid_counterexample'],'PASS_UNSUPPORTED'
        if c['state']=='REPORT_DELIVERED':
            assert c['report_complete'],'INCOMPLETE_DELIVERY'
            deliveries.setdefault(c['verdict'],witness[key(c)])
            delivered_inconclusive|=c['verdict']=='INCONCLUSIVE' and c['material_gap']
        for actor,event in itertools.product(model['actors'],model['events']):
            matches=[r for r in model['rules'] if r['from']==c['state'] and r['actor']==actor and r['event']==event and all(c[k]==v for k,v in r['guard'].items())]
            assert len(matches)<=1,'CONFLICTING_GUARDS'
            if not matches:
                rejected+=1
                continue
            accepted+=1;rule=matches[0]
            if event=='EXECUTE':assert actor=='EXECUTOR' and c['specific_authorization'] and c['context_ready'],'UNAUTHORIZED_EXECUTION_EVENT'
            assert actor!='OTHER' and event!='OTHER','UNKNOWN_EVENT_ACCEPTED'
            after={**c,**rule['effects'],'state':rule['to']}
            if event=='INVALIDATE':assert not after['specific_authorization'] and after['verdict']=='PENDING','STALE_AUTHORIZATION'
            if key(after) not in seen:
                seen.add(key(after));queue.append(after);witness[key(after)]=witness[key(c)]+[{'actor':actor,'event':event,'from':c['state'],'to':after['state']}]
    assert {'PASS_WITHIN_SCOPE','FAIL','INCONCLUSIVE','BLOCKED'} <= set(deliveries),'MISSING_VERDICT_PATH'
    assert delivered_inconclusive,'NO_HONEST_PARTIAL_DELIVERY_PATH'
    return {'reachable_configurations':len(seen),'accepted_transitions':accepted,'rejections':rejected,'delivery_with_material_gap_without_PASS':'REACHABLE','abstract_delivery_witnesses':deliveries}

def main():
    source=BASE/'fsm-propuesta.json';raw=source.read_bytes();model=json.loads(raw)
    # First execute a deliberately weakened guard as a negative control; do not
    # confuse its failure with a run of an application or the QA skill.
    weakened=copy.deepcopy(model)
    for r in weakened['rules']:
        if r['event']=='EXECUTE':r['guard']={'context_ready':True}
    try:enumerate_model(weakened)
    except AssertionError as error:
        assert str(error)=='UNAUTHORIZED_EXECUTION_EVENT',str(error)
        negative={'result':'EXPECTED_REJECTION','counterexample':str(error)}
    else:raise AssertionError('Negative control failed to detect weakened guard')
    result={'scope':'STATIC_DOCUMENTARY_MODEL_ONLY','model_sha256':hashlib.sha256(raw).hexdigest(),'negative_control':negative,'unmodified_model':enumerate_model(model),'not_proven':['External truth/authority/coverage bindings','Runtime implementation','Hardware properties','Liveness/fairness','Complete canonical PRD migration']}
    (BASE/'resultado-modelo.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
