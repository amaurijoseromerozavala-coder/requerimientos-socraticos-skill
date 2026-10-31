# QA Inquisidor: construcción local 0.1.0-alpha

El humano reanudó la construcción, exigió funcionamiento real y delegó juicios
técnicos dentro de criterios explícitos, con excepciones consultadas. Esta
continuación conserva v1/v2 y sus recibos; no declara migrado el PRD completo.

Ya existe la skill local en `skills/qa-inquisidor/SKILL.md`, su schema y un
comprobador de consistencia de registros. Modo ANALYSIS_ONLY; no ejecuta casos
de la aplicación. El registro de Gentle AI lista dos skills. Producción y CI
siguen fuera del alcance; hardware físico no observado. No hay sistema de
aplicación seleccionado ni conclusión de calidad global.

## Delta EARS y aceptación

| ID | Requisito | Fuente | Falsador / evidencia |
| --- | --- | --- | --- |
| R29 | Cuando la skill valore alcance/materialidad/suficiencia, deberá aplicar criterios explícitos y consultar excepciones al humano. | Decisión Q-HUMAN-006 | Juicio pendiente o excepción produce GAP, no éxito. |
| R30 | Si cambia assessment, inventario, casos, oráculos, evidencia o contexto, el juicio anterior no deberá justificar éxito. | Q008, K4 | Mutar assessment o artefacto manteniendo juicio: no SUCCESS. |
| R31 | Cuando exista fallo vigente junto a un caso requerido pendiente, el informe deberá conservar ambos hechos. | Q007 | FAIL con lista de gaps y material_gap=true. |
| R32 | Mientras un juicio requerido esté pendiente, la evaluación deberá señalar el pendiente agregado. | Q007, K5 | Scope=PENDING implica GAP y material_gap=true. |
| R33 | Cuando un caso esté NOT_RUN, UNKNOWN o STALE, deberá conservar motivo propio y fuente del requisito. | R22/Q007 | Caso sin reason rechazado antes de derivar evento. |
| R34 | Cuando reciba resultados estructuralmente inválidos, duplicados, contradictorios o de tipo incompatible, el comprobador deberá rechazarlos sin ejecutar casos ni mutar evidencias. | Q007/R21–24 | Controles de referencias, CLI y archivos sin cambios. |

Estas obligaciones guían el alpha; el comprobador verifica estructura y bindings
declarados, no autentica humanos ni acredita que la observación descrita sea cierta.

## Contrato y modelo

`contrato-evidencia.json` define precedencia, criterios, cardinalidades propuestas
y puente de eventos. `modelo-cierre.json` usa seis predicados resumen y cuatro
salidas exclusivas. `tabla-decision.json` enumera sus64 valoraciones, incluidas
combinaciones de resumen que no tienen por qué ser realizables por datos reales.
No se elimina una región desconocida para aumentar cobertura. Los predicados
son admisibilidad/soporte, no codificaciones de UNKNOWN como verdad falsa.

Un REJECT no cambia estado. FAILURE conserva gaps. SUCCESS exige todas las
guardas de su dominio. INVALIDATE conserva historia e invalida juicios ligados.
La FSM global v2 no se reemplaza silenciosamente: el puente v3 refina la entrada,
y su correspondencia completa con un orquestador QA sigue pendiente.

## Verificación observada

- Dos RED previos sobre la abstracción v2: borrado de gaps al registrar fallo
  y gate de éxito descrito solo como contrato externo. No son fallos de una
  aplicación ejecutada.
- La primera suite del checker pasó36 pruebas. Una revisión independiente las
  repitió y encontró tres casos no cubiertos. Se añadieron primero:39 pruebas,
  tres fallos pertinentes observados. Tras corregir y ampliar:43 pruebas OK.
- Tabla exhaustiva:64 filas,0 guardas solapadas/entradas sin regla. Hay32 rechazos,
  16 fallos,15 pendientes y1 éxito en ese universo abstracto.
- Solver público de requerimientos/Gentle: perfil256MiB rechazado por baseline
  de su llamador, INCONCLUSIVE conservado; perfil512MiB permitido por admisión
  viva. Dominio SAT, ausencia de guardas y ausencia de respuesta UNSAT; dos
  propiedades consecuencia del modelo. No prueba independiente de implementación.
- Entrevista de esta sesión:3 intercambios reales Q006–008, recibos comprobados;
  decisión humana separada. Estado INTERROGATING, no COMPLETE global.

La revisión nativa RDD de este candidato se informa exclusivamente en su recibo
y resultado posterior. Las cifras anteriores no anticipan su aprobación.

## Pendientes explícitos

PRD/entrevista global canónicos, FSM de orquestación implementada, aceptación
semántica de una aplicación objetivo y calibración física i3/WSL no completados.
Este alpha ya permite guiar análisis y detectar inconsistencias documentales;
no certifica producción, ausencia de errores ni rendimiento de hardware.
