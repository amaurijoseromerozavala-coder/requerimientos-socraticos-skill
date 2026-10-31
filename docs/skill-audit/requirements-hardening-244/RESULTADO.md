# Requerimientos socráticos 2.4.4 — memoria del analizador/Z3

Fecha: 2026-10-28. Autorización humana: «Realiza las correcciones». Se implementó
el pendiente aceptado de memoria del analizador. No se adoptaron los mandatos
del QA sobre regex, permisos0644 o CI. Gentle AI real4.2.0 revisó las herramientas
locales de la skill; upstream no modificado.

## ANALYSIS

El analizador público admite --memory-budget-mib, default512, rango256..1024
múltiplo8. Es perfil técnico provisional: caller1/8 y solver7/8, por tanto64 y
448MiB. La CLI propia conserva hard448 para que el hijo configure448/448 sin
aumentar un hard heredado; la CLI mantiene soft64. El worker recibe RLIMIT_AS
antes de exec y, por tanto, antes de importar y usar Z3.

Se reutiliza el supervisor acotado y el mismo gate cooperativo por cuenta que
Git. Tener perfiles distintos no permite dos trabajos admitidos simultáneos.
Headroom visible2x y rechazo de UNKNOWN/insuficiente/ocupado se conservan. El
dict/validación del perfil Git permanecen iguales; admisión regenera un snapshot
canónico de tipos exactos para que cambios del dict externo no alteren el criterio.

La CLI comprueba su VmSize antes de reducir su soft. main() externo no cambia
los límites del llamador, pero sí configura el worker antes de exec. Los límites
virtuales no son cuotaRSS, reserva física, contención global de procesos ni
garantía de MemoryError para todo fallo nativo. El adaptador preexec conserva
su alcance de CLI de un solo hilo y kernel/cuenta/motor confiables.

El worker informa observaciones locales de memoria y límites reales al emitir
un resultado satisfactorio. La CLI exige que soft/hard observado coincida con
lo solicitado. Un MemoryError capturado intenta emitir un registro fijo
INCONCLUSIVE/MEMORY_BUDGET_EXCEEDED, exit3, sin queries/table/coverage. El supervisor
descarta esos campos si recibe ese diagnóstico. Una señal o JSON ausente conserva
WORKER_FAILED sin afirmar OOM; errores nativos mantienen SOLVER_ERROR y los
contratos INVALID_INPUT/SOLVER_UNAVAILABLE se conservan.

El plazo incluye identidad del runtime, preparación y admisión. Si se agota
antes del worker no se crea éste. Se conservan la limpieza adicional acotada,
las consultas, propiedades, tabla,32variables, AST y256KiB de entrada. No se
reescribió el preflight basándose en tamaños que el analizador no admite.

## TEST PLAN

RED previos guardados: perfil lógico ausente, wrapper sin presupuesto y MemoryError
del worker sin capturar. Después se comprobaron límites reales en CLI512/1024,
hard heredado, baseline, ausencia de mutación de caller externo, gate común con
Git, tiempo de admisión, diagnóstico sin resultados y señales sin causa probada.
Los fixtures son pequeños y los procesos propios, con timeout exterior.

El primer harness ejecutó grupos concurrentes y recibió RESOURCE_BUSY esperado
por el nuevo gate compartido. Se repitieron secuencialmente y se conservó un
resumen fiel de terminal en harness-contention.log; no se llama log íntegro ni
RED del producto. El revisor independiente inicialmente omitió el launcher en
su copia; corrigió su harness y repitió solo el grupo afectado. Tampoco es un
fallo del producto ni un RED de comportamiento.

Se verificó además que admisión use tipos canónicos y su propio snapshot, sin
coerciones float/int o bool/int. No se generaron archivos de30MiB, cargas de
agotamiento ni pruebas de presión del hardware.

## VERIFICATION

- Regresión final: **222 pruebas correctas**,7.480s observados; timeout exterior50s,
  full-tests.log. La duración no es garantía para otro entorno/modelo.
- Revisión independiente: **72 pruebas únicas correctas**, en copia y con hashes
  propios, grupos secuenciales con timeout20s. Dos repros reales de API confirmaron
  caller intacto, solver448 y rechazo del hard heredado384MiB sin aumentarlo.
- Comparación con2.4.3: **8 casos equivalentes** en retorno y campos matemáticos/
  errores. Se excluyeron expresamente nuevas métricas, identidad de runtime y
  tiempos variables; no se afirma igualdad de todo stdout. differential.json.
- CLI real Gentle AI con modelo pequeño: PASS. Caller soft64 y worker448MiB,
  RSS del solver53219328bytes en la muestra; public-logic-analysis.json. No es
  máximo de toda la ejecución ni calibración i3/WSL.
- Revisión nativa: riesgo alto, cuatro lentes, `review-fa1534cd35f28a47`, approved
  en último evento y acknowledgement exacto. Candidato:
  `sha256:32956a803d1fa2df0e87bda4d73b0cb671d47fd2388bb301c9a2312b97430785`.
- **94 archivos** seleccionados coinciden byte a byte con el árbol revisado
  `40cb93653c9ac7f493445e9e16dc18e5c031cf1e`; integrity-final.json.

La revisión nativa inspecciona fuentes/contratos/pruebas completos. La ejecución
222 y la reproducción independiente72 son evidencias separadas, no atribuidas
al RDD. validation.json permanece congelado antes de revisión; el cierre se
acredita en recibos externos, sin reescribir una autoaprobación en el candidato.

El revisor registró como posible refuerzo la asimetría del guard de observaciones
entre CLI propia y main() externo. No reprodujo ejecución fuera del límite:
RLIMIT_AS antes de exec se aplica en ambos. Ese alcance se conserva explícito;
no se presenta como una garantía de autoridad externa o kernel inmutable.

Se mantiene0600, CI diferido, QA/producción sin habilitar y
BLOCKED_GLOBAL_ENFORCEMENT. Hardware físico i3/WSL y Lean NOT_RUN. RSS agregado,
presión/temperatura del host, máximos de todos los modelos y disponibilidad
universal NOT_PROVEN. No se amplían los resultados de esta entrega a esos ámbitos.

## Registro documental

No hubo nuevas preguntas de intención al humano ni respuestas inventadas. Las
consultas técnicas resolvieron el perfil, imports por archivo, contratos de
observación y ensayos. El perfil numérico es una elección provisional del
implementador; no una decisión humana de capacidad física. El ODD y su espejo
Engram conservan localizadores y evolución; fuentes y recibos son evidencia actual.
