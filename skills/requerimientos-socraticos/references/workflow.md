# ODD, TDD y RDD estrictos para documentos

"Strict" es la política de esta skill; no inventa modos `--strict` de Gentle AI.
No aplica las condiciones específicas de `rdd-defect-workflow` (issues de bugs
del propio proyecto) a todos los PRD ni crea issues o commits automáticamente.

## ODD

La versión 2 exige el interrogatorio descrito en `interrogation.md` antes de
cerrar significado/canonicalizar. Interrogador, respondedor y humano tienen
autoridades distintas. Los estados de entrevista refinan CLARIFYING en esta
FSM documental; no sustituyen los estados del PRD. Mientras se espera una
respuesta solo se permite un borrador identificado como incompleto.

Autoriza → explora → resuelve incertidumbre → clasifica → documenta trabajo
sustancial → edita solo documentos → verifica → cierra. El usuario que pide un
PRD autoriza sus documentos, no implementación. Conserva un solo documento ODD
en `odd/tasks/<slug>.md` con Specs literales, Tasks y Log si hace falta relevo.
Lee ese documento al reanudar. Espeja el documento ODD completo en Engram cuando
el flujo instalado lo exija; el PRD canónico permanece en disco, con resumen y
localizador en memoria. Lee ambas escrituras; no son atómicas. Sin Engram, deja
el espejo pendiente y no pierdas el trabajo local.

## TDD documental estricto

Antes de editar cada obligación, registra un escenario RED y el oráculo que
rechaza su versión insuficiente: campo obligatorio ausente, guardas solapadas,
evento sin rechazo, privilegio indebido, transición a estado prohibido o una
traza que viola un invariante. Ejecútalo sobre el modelo/documento en consola
cuando haya comprobador. Luego corrige solo el documento/modelo y observa GREEN.
Refactoriza redacción y vuelve a comprobar equivalencia y regresiones afectadas.

No generes tests de implementación ni código del producto. Las pruebas son JSON,
tablas de decisión, trazas y comandos temporales sobre modelos locales. Un test
no ejecutable puede registrarse como especificación, pero no como PASS: el gate
TDD estricto queda BLOCKED. No inventes un RED de un artefacto ya terminado.
Un control negativo debe producir el fallo previsto, no cualquier error ajeno.

## RDD y candidato exacto

1. Consulta `gentle-ai --help`, `gentle-ai review --help` y ayuda de subcomandos
   que existan en el binario actual. La documentación remota puede adelantarse.
2. Consulta `gentle-ai review mode status --cwd <raíz>`; no habilites el modo ni
   cambies el kill switch en nombre del usuario.
3. Congela entradas, requisitos, modelo y evidencias. Guarda SHA-256 del candidato
   y dependencias. Usa selección Git exacta admitida por el runtime; un hash
   documental aislado no es un recibo nativo RDD.
4. Si están disponibles modo, repo, proveedor y candidato válidos, inicia el
   flujo nativo con argumentos soportados. Reenvía el consentimiento si el
   binario lo exige; sigue las transiciones que devuelva, sin inventar comandos,
   lineage, aprobación ni acknowledgements. No hagas commit para fabricar una
   frontera si el alcance autorizado es solo documental.
5. Revisa de forma adversarial semántica/autoridad, invariantes/FSM, cobertura,
   falsadores, trazabilidad y evidencia. Un revisor independiente es requerido
   para el gate estricto; una auto-revisión se etiqueta SELF_REVIEW_ONLY.
6. Cualquier corrección produce nueva revisión/hash y reabre pruebas/revisión
   dependientes; solo usa una corrección acotada cuando el runtime la permita.
7. Sin infraestructura nativa o con modo OFF, conserva el PRD como DRAFT/BLOCKED
   y registra `NATIVE_UNAVAILABLE`/`DISABLED`. Puedes entregar trabajo útil, pero
   no `READY`, `native PASS` ni una certificación de ausencia de fallos.

La autorización para revisar un candidato no se extiende a candidatos futuros.
READY permite revisión/uso documental humano, nunca implementar o desplegar.
Las preguntas de un revisor RDD no sustituyen el interrogatorio de requisitos.
Un recibo aprobado tampoco acepta una propuesta de diseño ni resuelve intención.

## FSM del proceso documental

Estados: CAPTURED, CLARIFYING, SPECIFYING, VALIDATING, REVIEWING, READY, BLOCKED.
El registro de transiciones del PRD conserva evento, origen, destino y razón.

| Origen | Evento y guarda | Destino |
|---|---|---|
| CAPTURED | alcance registrado | CLARIFYING |
| CLARIFYING | hay unknown material | CLARIFYING; una pregunta |
| CLARIFYING | significado suficiente | SPECIFYING |
| SPECIFYING | EARS/lógica/FSM trazados | VALIDATING |
| VALIDATING | contraejemplo | SPECIFYING; invalidar evidencia afectada |
| VALIDATING | comprobaciones completas | REVIEWING |
| REVIEWING | hallazgo | SPECIFYING; candidato nuevo |
| REVIEWING | todos los gates vigentes pasan | READY |
| cualquiera | recurso/evidencia necesaria ausente | BLOCKED |
| BLOCKED | bloqueo resuelto con evidencia | CLARIFYING |
| READY | cambia entrada/modelo/evidencia | CLARIFYING; invalidar READY |

Toda transición no listada se rechaza sin cambiar el estado ni borrar evidencias.
No existe salto desde captura a READY ni resolución automática de decisiones.
