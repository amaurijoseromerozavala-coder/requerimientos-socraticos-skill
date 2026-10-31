# Requerimientos socráticos 2.4.4 — memoria del analizador/Z3

Herramientas locales de la skill; sin CI, producción ni commits de producto.
Runner: venv existente, unittest con timeout exterior, procesos y fixtures pequeños.

## Specs

S1. Usuario: «Realiza las correcciones». Alcance aceptado del contraste anterior:
extender el presupuesto virtual al worker del analizador/Z3. No reescribir
preflight por predicciones no medidas ni ampliar permisos0600.

S2. Perfil técnico provisional configurable512MiB,256..1024 múltiplo8; CLI1/8,
solver7/8. Límites LinuxRLIMIT_AS antes de exec, respetando hard heredado;
CLI propia con baseline comprobado, llamadas main desde pruebas/API no deben
reducir límites externos. Reusar admisión cooperativa por cuenta de2.4.3,
sin modificar el perfil Git ni su contrato. No cuota RSS/kernel agregada.

S3. Ante MemoryError observado o rechazo de recursos emitir INCONCLUSIVE sin
cobertura/resultados aprobatorios. Las señales/diagnóstico ausente no demuestran
OOM; conservar errores de solver y argumentos actuales. Observar límites y RSS
por proceso, sin extrapolar máximos ni capacidad de i3/WSL. No garantizar recuperación
de cualquier fallo nativo ni contención universal de descendientes.

S4. Conservar lógica, consultas, tabla,32variables, AST/bytes, plazos y retorno
anterior salvo controles de recursos nuevos. RED/GREEN real, regresión, revisión
independiente y RDD nativo exacto; informe y JSON/ZIP completos.

## Tasks

- T1 [S1,S2] inline: baseline e importación mínima Z3 — DONE.
- T2 [S2] delegado: perfil lógico y admisión compartida — DONE;19tests.
- T3 [S2,S3,S4] delegado: supervisor público del analizador y pruebas — DONE;17nuevos/35grupo.
- T4 [S3,S4] inline: diagnóstico/observación del worker y regresión — DONE;2tests/222regresión.
- T5 [S4] inline: revisión independiente, RDD y exportación — DONE;222/72pruebas,8comparaciones,reciboexacto y fuentescompletas.

## Log

L1.2026-10-28: «Realiza las correcciones». Las afirmaciones del QA se contrastaron:
el analizador acepta256KiB y Git8MiB/archivo; límites Git ya presentes en2.4.3.
La extensión aZ3 es el pendiente autorizado. El perfil es una elección técnica
provisional y no una capacidad física observada. No se ejecuta saturación del host.

2026-10-28: pequeña importaciónZ3+unaconsulta Vm84185088/RSS44335104bytes, muestra
local sin límite previo ni máximo/target. Perfil solver448MiB es provisional.
RED previos en policy/analyzer/worker guardados. Regresión222tests OK7.480s.
Revisor independiente72tests únicos PASS; su primer harness omitióbin/gentle-ai,
lo corrigió y repitiósolo supervisor. No es fallo del producto ni RED previo.
Dos repros reales API: caller intacto y solver448; hard384 heredado rechazado.
Asimetría guardobservadocon_own_cli registrada como refuerzo opcional; no se
reprodujo ejecución fuera de límite: preexecRLIMIT se aplica incondicionalmente.
Un arranque concurrente inicial del harness produjoRESOURCE_BUSY esperado;
se conservó como resumen fiel de terminal, no log íntegro ni RED de producto.

2026-10-28: ocho casos equivalentes de resultadosmatemáticos/errores versus2.4.3;
comparación excluyemétricas nuevas ytiempos variables explícitamente, no stdouttotal.
CLIreal GentleAIrequirementsanalyzePASS:caller64/solver448MiB virtuales,
RSSsolver53219328bytes en modelo pequeño, no máximonicalibracióntarget.
Candidato congelado:222tests,72reproducciónindependiente. RDDen revisión
review-fa1534cd35f28a47,riesgoalto4lentes,10archivoscambiados/681líneas.

2026-10-28: RDDnativo aprobadoyacknowledged para
sha256:32956a803d1fa2df0e87bda4d73b0cb671d47fd2388bb301c9a2312b97430785.
94archivos seleccionados coincidenconárbol40cb93653c9ac7f493445e9e16dc18e5c031cf1e.
InformeRESULTADO.md externo redactado. Empaquetadopendiente; noCI/producción,
NoestadofísicodelPCniglobal demostrado. Hardware/LeanNOT_RUN.

2026-10-28: JSON/ZIP2.4.4 creados y verificados con hashes decontenido yZIP OK.
