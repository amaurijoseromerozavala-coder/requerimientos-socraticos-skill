# RS3-WU-WITNESS-RECHECK-001

## Alcance

Corresponde a T022 del paquete RS3: comprobar una asignación matemática
declarada como testigo antes de comunicarla. Reutiliza el worker supervisado
existente; no crea otro proceso, no ejecuta código del modelo ni interpreta
lenguaje natural. La verificación es de fórmula y asignación, no de producto.

## Oráculos RED

- Un testigo SAT de `NO_OUTPUT` se reevalúa contra la fórmula exacta y sus
  inputs fijados; un testigo alterado produce REFUTED.
- Faltan variables, sobran variables o aparece un valor no booleano: INVALID.
- Presupuesto vencido: UNKNOWN, no VERIFICADO por inferencia.
- La CLI solo comunica SAT con testigo si la reevaluación devuelve VERIFIED;
  incluye la procedencia `MODEL_COMPLETION_APPLIED`, nunca OBSERVED.
- Suites anteriores y límites del supervisor mantienen sus resultados.

## Tareas

Tests RED pertinentes, helper acotado, integración mínima en el analizador,
GREEN y regresiones, RDD nativo del candidato exacto, gates de contenido y
respaldo posterior. Sin autoridad humana ni afirmación física.
