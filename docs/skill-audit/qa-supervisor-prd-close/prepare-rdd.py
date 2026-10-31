import json,subprocess
from pathlib import Path
r=Path('/workspace/replica-gentle-ai');a=Path(__file__).resolve().parent;p=r/'docs/requirements/qa-supervisor';cli=str(r/'bin/gentle-ai')
for n in ('rdd-selected.json','rdd-start.json','rdd-consent.json','rdd-final.json','RESULTADO.md','RESULTADO.json'):(a/n).touch(exist_ok=True)
request=a/'request.md';request.write_text('''# Revisión de PRD supervisor local QA
Humano solicita cerrar PRD, confirmó invocador exclusivamente QA local y opción1
recibos mínimos. No implementación ni CI/producción. Candidato documental:
contratos de protocolo/recuperación/tiempo/retención, EARS y FSM. Entrevista real
COMPLETE8preguntas, diseño REVIEWED. Esquema PRD2 válido con estado DRAFT porque
full assurance/implementación no demostrada. No promover a READY por logs.
13 controles de salida sintética,9 checks documentales,16combinaciones y418
transiciones del modelo acotado; recibos separados. No calibración física.
Verificar cruces, autoridad, retención sin contenido bruto, INFRA_LOCK, causas
no inferidas. Revisar archivos completos pertinentes y no inferir ejecución.
''')
files=sorted(str(x.relative_to(r)) for x in p.rglob('*') if x.is_file() and x.suffix!='.html' and '__pycache__' not in x.parts)
# Current checker source dependencies are review context, not changes to their code.
files+=['skills/qa-inquisidor/scripts/validate_report.py','skills/qa-inquisidor/assets/report.schema.json','skills/qa-inquisidor/SKILL.md','skills/requerimientos-socraticos/scripts/json_preflight.py','skills/requerimientos-socraticos/scripts/safe_io.py']
base=[cli,'review','status','--cwd',str(r),'--contract','gentle-ai.review-integration/v2','--agent','codex','--next-transition']
s=json.loads(subprocess.check_output(base,text=True));args=base+['--base-ref','4b825dc642cb6eb9a060e54bf8d69288fbee4904','--workspace-overlay','--untracked-scope','select','--expected-untracked-inventory',s['eligible_untracked_inventory'],'--request-context',str(request),'--lenses','reliability,resilience','--lenses-reason','Review local supervisor PRD contracts and limitations; not implementation or production.']
for f in sorted(set(files)):args+=['--intended-untracked',f]
q=subprocess.run(args,capture_output=True,text=True);(a/'rdd-selected.json').write_text(q.stdout);assert q.returncode==0,(q.stdout,q.stderr);s=json.loads(q.stdout);e=s['next_transition']['execute']
q=subprocess.run([cli,'review','start']+[x['token'] for x in e['arguments']],capture_output=True,text=True);(a/'rdd-start.json').write_text(q.stdout);s=json.loads(q.stdout)
if s.get('action')=='consent_required':(a/'rdd-consent.json').write_text(q.stdout)
print(json.dumps({k:s.get(k) for k in ['action','code','cause','target_identity','risk_level','changed_files','changed_lines']},ensure_ascii=False))
