"""Finite qualified-event document model, not an implementation test."""
import json,copy,itertools,hashlib
from pathlib import Path
p=Path(__file__).resolve().parents[1];d=json.loads((p/'prd.json').read_text());f=d['candidate']['fsm']
def check(m):
 failures=[];reachable={m['initial']['state']};pending=list(reachable)
 while pending:
  s=pending.pop()
  for a,e in itertools.product(m['actors'],m['events']):
   ts=[t for t in m['transitions'] if t['from']==s and t['actor']==a and t['event']==e]
   if len(ts)!=1:failures.append('coverage_or_overlap');continue
   t=ts[0]
   if a=='OTHER' and (t['outcome']!='REJECT' or t['to']!=s):failures.append('actor_authority')
   if s=='INFRA_LOCK' and e!='termination_reconciled' and t['to']!='INFRA_LOCK':failures.append('lock_release')
   if t['to'] not in reachable:reachable.add(t['to']);pending.append(t['to'])
 return failures,reachable
bad=copy.deepcopy(f);bad['transitions'].pop(0);red_gap=check(bad)[0]
bad2=copy.deepcopy(f);next(t for t in bad2['transitions'] if t['from']==f['initial']['state'] and t['actor']=='OTHER')['outcome']='ALLOW';red_authority=check(bad2)[0]
errors,states=check(f);assert not errors;assert red_gap and red_authority
r={'candidate_sha256':d['assurance']['candidate_sha256'],'transitions':len(f['transitions']),'reachable_states':sorted(states),'errors':errors,'negative_controls':{'missing_transition_detected':bool(red_gap),'unauthorized_allow_detected':bool(red_authority)},'scope':'All qualified control events; assumes guards are established externally; no OS/clocks/persistence/total-liveness proof.'};(p/'verification/canonical-model-results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
