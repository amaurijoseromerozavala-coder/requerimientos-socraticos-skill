import json,subprocess
from pathlib import Path
r=Path('/workspace/replica-gentle-ai');a=Path(__file__).resolve().parent;plan=json.loads((a/'review-partition.json').read_text());cli=str(r/'bin/gentle-ai')
for g in plan['groups']:
 p=a/('part-'+g['id']);p.mkdir(exist_ok=True)
 for n in ['selected.json','start.json','consent.json','final.json']:(p/n).touch(exist_ok=True)
for g in plan['groups']:
 p=a/('part-'+g['id']);base=[cli,'review','status','--cwd',str(r),'--contract','gentle-ai.review-integration/v2','--agent','codex','--next-transition'];s=json.loads(subprocess.check_output(base,text=True));args=base+['--base-ref','4b825dc642cb6eb9a060e54bf8d69288fbee4904','--workspace-overlay','--untracked-scope','select','--expected-untracked-inventory',s['eligible_untracked_inventory'],'--lenses','reliability,resilience','--lenses-reason','Partial PRD review: '+g['id']+'. Other parts and aggregate integration remain separately required; no implementation approval.']
 for f in g['files']:args+=['--intended-untracked',f]
 q=subprocess.run(args,capture_output=True,text=True);(p/'selected.json').write_text(q.stdout);assert q.returncode==0,(q.stdout,q.stderr);s=json.loads(q.stdout);e=s['next_transition']['execute'];q=subprocess.run([cli,'review','start']+[x['token'] for x in e['arguments']],capture_output=True,text=True);(p/'start.json').write_text(q.stdout);j=json.loads(q.stdout)
 if j.get('action')=='consent_required':(p/'consent.json').write_text(q.stdout)
 print(json.dumps(dict(part=g['id'],**{k:j.get(k) for k in ['action','code','target_identity','risk_level','changed_files','changed_lines']})),flush=True)
