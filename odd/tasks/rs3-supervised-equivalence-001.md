# RS3-WU-SUPERVISED-EQUIVALENCE-001

## Objetivo

Hacer accesible la comparación de reglas RS3 desde `requirements analyze`,
pasando por los límites y supervisor ya existentes. El modelo JSON no cambia:
una comparación opcional identifica dos IDs de reglas existentes y scope
`absolute|contextual`. El worker devuelve un campo separado `equivalence`;
`queries` y `table.coverage` conservan su semántica.

## Oráculos RED

- Absoluta: `SAT(XOR(F,H))` informa diferencia con testigo revalidado.
- Contextual: `SAT(D ∧ C_other ∧ XOR(F,H))`. Si el contexto es satisfacible y
  el XOR es UNSAT, informa equivalencia **solo en ese contexto**; si el contexto
  es UNSAT, informa `VACUOUS_CONTEXT`, nunca equivalencia.
- Scope/IDs faltantes o ajenos, o flags parciales: `INVALID_INPUT`, exit 2,
  sin resultado de comparación.
- Timeout o UNKNOWN no se transforma en equivalencia. Sin flags, la forma de
  salida anterior permanece compatible.

## Proceso

ODD → RED por CLI real → implementación worker/launcher → GREEN/regresiones →
RDD exacto → respaldo. No se otorga autoridad ni aprobación de producto.
