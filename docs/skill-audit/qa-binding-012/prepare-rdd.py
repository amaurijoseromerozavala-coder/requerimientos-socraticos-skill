import json,subprocess
from pathlib import Path
r=Path('/workspace/replica-gentle-ai');a=Path(__file__).resolve().parent;cli=str(r/'bin/gentle-ai')
old=json.loads((r/'docs/skill-audit/qa-infra-011/rdd-selected.json').read_text())
files=set(old['projection']['intended_untracked'])
files.add('skills/qa-inquisidor/tests/test_infrastructure.py')
for n in ['rdd-selected.json','rdd-start.json','rdd-consent.json','rdd-final.json','RESULTADO.md','RESULTADO.json','engram.json']:(a/n).touch(exist_ok=True)
request=a/'request.md'
request.write_text("""# QA Inquisidor 0.1.2-alpha
Humano: Haz las mejoras usa gentle-ai.
Incluir schema_version y limitations en inputs_digest. Rechazar vigencia de digests
anteriores; no recalcular automáticamente juicios. Declarar authority_verification
NOT_PERFORMED y execution_authorized false en toda salida JSON. Identidad declarada
no autenticada; ningún evento autoriza ejecución. Sin firmas ni CI ni producción.
TDD: 54 tests, cuatro nuevos RED (3 fallos y 1 error) antes de corregir; 54 GREEN.
La revisión independiente se registra separadamente. No garantía RSS/OOM.
""")
base=[cli,'review','status','--cwd',str(r),'--contract','gentle-ai.review-integration/v2','--agent','codex','--next-transition']
s=json.loads(subprocess.check_output(base,text=True))
args=base+['--base-ref','b4e39373a52a6f2921ca61e5df819165656d33f1','--workspace-overlay','--untracked-scope','select','--expected-untracked-inventory',s['eligible_untracked_inventory'],'--request-context',str(request),'--lenses','reliability,resilience','--lenses-reason','Bind complete input context and explicitly deny execution authority; check compatibility and regression coverage.']
for p in sorted(files):args+=['--intended-untracked',p]
p=subprocess.run(args,capture_output=True,text=True,timeout=30);(a/'rdd-selected.json').write_text(p.stdout)
s=json.loads(p.stdout)
if p.returncode:print(json.dumps(s));raise SystemExit(p.returncode)
e=s['next_transition']['execute']
p=subprocess.run([cli,'review','start']+[x['token'] for x in e['arguments']],capture_output=True,text=True,timeout=30)
(a/'rdd-start.json').write_text(p.stdout);s=json.loads(p.stdout)
if s.get('action')=='consent_required':(a/'rdd-consent.json').write_text(p.stdout)
print(json.dumps({k:s.get(k) for k in ['action','code','cause','lineage_id','target_identity','risk_level','changed_files','changed_lines','phase']},ensure_ascii=False))
