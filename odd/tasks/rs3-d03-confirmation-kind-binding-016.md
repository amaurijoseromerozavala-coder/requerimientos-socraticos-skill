# WU-RS3-D03-CONFIRMATION-KIND-BINDING-016

## Objetivo, precedencias y alcance

D03 exige una comprobación nueva por cada confirmación y separa aceptación
semántica de autorización operativa. El auditor PBKDF2 actual vincula propuesta,
snapshot y texto, pero no la **categoría**. Vincularla al digest del sujeto y
exigirla en el archivo de decisión manual. Depende de WU-013 y WU-012.

Solo se admiten `SEMANTIC_ACCEPTANCE`, `EXCEPTION_ACCEPTANCE` y
`OPERATION_AUTHORIZATION`. Propuestas, aclaraciones y categorías no mapeadas no
son comprobaciones de confirmación y se rechazan. La entrada manual pasa a
`rs3-manual-decision/v2`; v1 se rechaza sin migración implícita. El audit log
sigue sin emitir autoridad y no se usan credenciales reales.

No se implementa la cuenta D05, el servicio de autoridad ni confirmación
humana. La coincidencia PBKDF2 continúa como dato `NOT_ESTABLISHED`.

## Oráculos RED congelados

1. Con propuesta/snapshot/texto idénticos, dos categorías válidas producen
   sujetos diferentes; la primera no consume la segunda.
2. Categoría desconocida o `PROPOSAL_OR_CLARIFICATION` se rechaza antes de
   PBKDF2 y no registra aceptación.
3. La CLI manual exige categoría v2 y rechaza archivo v1, duplicado o sin
   categoría antes de leer la contraseña.
4. Un replay dentro de la misma categoría sigue bloqueado.
5. Ninguna salida concede `HUMAN_CONFIRMED` o ejecución.

RED → implementación → GREEN/regresión → Gentle AI RDD exacto → Git. Solo
contraseñas sintéticas en tests; equipo objetivo NOT_RUN.

## Evidencia RED/GREEN local

- RED: tres controles nuevos terminaron exit 1: el auditor no aceptaba
  `confirmation_kind`, y la CLI aún aceptaba el archivo v1 sin categoría.
- GREEN focalizado: 21 tests del auditor, CLI y guarda UID terminaron OK tras
  exigir la categoría y vincularla al digest.
- GREEN final: `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh`
  terminó exit 0 sobre el árbol final: 55 CI, 130 supervisor, 62 QA y 342
  requisitos. La primera corrida también pasó, pero se repitió porque después
  se añadió un control negativo de CLI.
