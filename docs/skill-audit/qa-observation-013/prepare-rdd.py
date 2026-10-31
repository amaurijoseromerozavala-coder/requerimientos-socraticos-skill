import json,subprocess
from pathlib import Path
r=Path('/workspace/replica-gentle-ai');a=Path(__file__).resolve().parent;cli=str(r/'bin/gentle-ai')
old=json.loads((r/'docs/skill-audit/qa-binding-012/rdd-selected.json').read_text())
files=set(old['projection']['intended_untracked'])
files.add('skills/qa-inquisidor/tests/test_infrastructure.py')
files.add('skills/qa-inquisidor/tests/test_observation.py')
for n in ['rdd-selected.json','rdd-start.json','rdd-consent.json','rdd-final.json','RESULTADO.md','RESULTADO.json','engram.json']:(a/n).touch(exist_ok=True)
request=a/'request.md'
request.write_text("""# QA Inquisidor 0.1.3-alpha
Humano: Has las correcciones pertinentes.
Observación de declaraciones FAIL independiente de admisión documental. CLI
examina únicamente evidence[*].outcome de JSON ya decodificado, máximo128 filas,
sin I/O adicional. NOT_ASSESSED si no se decodifica o no se puede interpretar;
exploración parcial no afirma ausencia. No autentica evidencia ni autoridad,
no cambia veredicto ni autorización. Mantener REJECT_INPUT/INFRA_FAILURE.
TDD: 8 tests nuevos RED (9 errores contando subtests); 62 tests GREEN.
Revisión independiente separada en independent.md/log. Sin CI ni estrés físico.
""")
base=[cli,'review','status','--cwd',str(r),'--contract','gentle-ai.review-integration/v2','--agent','codex','--next-transition']
s=json.loads(subprocess.check_output(base,text=True))
args=base+['--base-ref','e584178633999dd05bb8aa6cf107ecfeac3913e9','--workspace-overlay','--untracked-scope','select','--expected-untracked-inventory',s['eligible_untracked_inventory'],'--request-context',str(request),'--lenses','reliability,resilience','--lenses-reason','Bounded observation of unverified failure declarations without changing rejection or execution authority.']
for p in sorted(files):args+=['--intended-untracked',p]
p=subprocess.run(args,capture_output=True,text=True,timeout=30);(a/'rdd-selected.json').write_text(p.stdout)
s=json.loads(p.stdout)
if p.returncode:print(json.dumps(s));raise SystemExit(p.returncode)
e=s['next_transition']['execute']
p=subprocess.run([cli,'review','start']+[x['token'] for x in e['arguments']],capture_output=True,text=True,timeout=30)
(a/'rdd-start.json').write_text(p.stdout);s=json.loads(p.stdout)
if s.get('action')=='consent_required':(a/'rdd-consent.json').write_text(p.stdout)
print(json.dumps({k:s.get(k) for k in ['action','code','cause','lineage_id','target_identity','risk_level','changed_files','changed_lines','phase']},ensure_ascii=False))
