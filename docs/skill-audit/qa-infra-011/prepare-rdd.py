import json,subprocess
from pathlib import Path
r=Path('/workspace/replica-gentle-ai');a=Path(__file__).resolve().parent;cli=str(r/'bin/gentle-ai')
old=json.loads((r/'docs/skill-audit/qa-construction-v3/rdd-selected.json').read_text())
files=set(old['projection']['intended_untracked'])
files.add('skills/qa-inquisidor/tests/test_infrastructure.py')
for n in ['rdd-selected.json','rdd-start.json','rdd-consent.json','rdd-final.json','RESULTADO.md','RESULTADO.json','engram.json']:(a/n).touch(exist_ok=True)
request=a/'request.md'
request.write_text('''# Corrección QA Inquisidor0.1.1
Humano: «Realiza las mejoras usa gentle-ai».
Alcance: separar MemoryError/OSError/RecursionError interceptados de errores de entrada.
Infraestructura: exit3, INFRA_FAILURE, documento NOT_ASSESSED, evento/veredicto null,
diagnóstico tipo/errno, causa no determinada. Datos inválidos conservan exit2/REJECT_INPUT.
No se agregan firmas, supervisor externo, CI, producción ni ensayos de agotamiento.
Salida JSON best effort explícita. No prometer emisión tras terminación abrupta.
## Verify
7 controles nuevos RED:5fallos y2errores porcamposausentes antes de corregir.
50 pruebas GREEN local e independiente. Excepciones controladas mediante mocks;
no simulamos que se haya agotado hardware. Recibos en este directorio.
''')
base=[cli,'review','status','--cwd',str(r),'--contract','gentle-ai.review-integration/v2','--agent','codex','--next-transition']
s=json.loads(subprocess.check_output(base,text=True))
args=base+['--base-ref','093c194016a7f8b92892d8f204da5d39bf7649c3','--workspace-overlay','--untracked-scope','select','--expected-untracked-inventory',s['eligible_untracked_inventory'],'--request-context',str(request),'--lenses','reliability,resilience','--lenses-reason','Distinguish unavailable evaluation from invalid input; preserve diagnostic limits and regression coverage.']
for p in sorted(files):args+=['--intended-untracked',p]
p=subprocess.run(args,capture_output=True,text=True,timeout=30);(a/'rdd-selected.json').write_text(p.stdout)
s=json.loads(p.stdout)
if p.returncode:print(json.dumps(s));raise SystemExit(p.returncode)
e=s['next_transition']['execute']
p=subprocess.run([cli,'review','start']+[x['token'] for x in e['arguments']],capture_output=True,text=True,timeout=30)
(a/'rdd-start.json').write_text(p.stdout);s=json.loads(p.stdout)
if s.get('action')=='consent_required':(a/'rdd-consent.json').write_text(p.stdout)
print(json.dumps({k:s.get(k) for k in ['action','code','cause','lineage_id','target_identity','risk_level','changed_files','changed_lines','phase']},ensure_ascii=False))
