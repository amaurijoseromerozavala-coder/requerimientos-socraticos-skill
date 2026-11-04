# WU-RS3-WEAK-MODEL-TRACEABILITY-007

## Objetivo y precedencia

Actualizar la matriz RS3 tras WU-RS3-SEMANTIC-ORACLES-005 y
WU-RS3-WEAK-MODEL-ADMISSION-006, ambas revisadas y respaldadas. Requiere los
recibos RDD existentes y el ZIP RS3 identificado.

## Alcance

Actualizar HEAD observado a `40328757dcf7f6b758f8f09df845224f1b656572`;
añadir dos eventos de evidencia parcial y referencias conservadoras en
RS3-REQ-036, 038, 039, 040, 043 y 045. Añadir el código/test del oráculo como
pista de inspección para REQ-045. No aprobar requisitos ni afirmar que los
casos del paquete se ejecutaron. No editar código de producto.

## Oráculos RED/GREEN

RED: matriz anterior conserva HEAD `ec164df...` y carece de los eventos
005/006. GREEN: 107/50/52 IDs intactos; todos los requisitos
NOT_VERIFIED_PER_REQUIREMENT; 52 casos NOT_RUN_AS_PACKAGE_CASE; vínculos solo
a rutas existentes y recibos RDD; nueva matriz reproducible byte a byte desde
el ZIP identificado. CI y marcadores históricos sin regresión.

RED observado: dos fallos, por HEAD anterior y ausencia del evento 005.
Al regenerar la matriz, un test legado exigía que REQ-036 tuviese exactamente
un evento; se cambió por pertenencia, preservando la aserción de aceptación no
verificada, porque ahora hay dos evidencias parciales. GREEN observado: ocho
tests focalizados con ZIP, 53 CI locales con una omisión explícita, matriz
idéntica byte a byte en segunda generación (SHA-256
`b1e6d889e05cc2a992f76b0acbdf9a8f460e19543b2be76bee2e53b23daefefe`).

RDD del candidato exacto; commit/push únicamente tras reconocimiento.

## Límite

Los vínculos son evidencia parcial de código, no aceptación por requisito.
Las revisiones Gentle AI fueron estáticas. No se probaron proveedores ni el
hardware objetivo; D03/D05 y producción siguen bloqueados.

## Corrección tras RDD

La primera revisión (`review-0835bb36419522f0`) aprobó el candidato con una
advertencia R3-001: el resumen aún decía 42/65 cuando la matriz ya contenía
43/64. Se reconoció la revisión, pero ese candidato no se publicó. Se añadió
un oráculo de consistencia resumen/matriz antes de corregir el texto; se
requiere nueva identidad y nuevo RDD para el candidato final. RED observado:
el nuevo test falló frente al resumen 42/65. GREEN observado tras corregirlo:
nueve tests focalizados con el ZIP y 54 CI locales, con una omisión explícita.
