# RS3-WU-FORMAL-EQUIVALENCE-001

## Objetivo y alcance

Implementar la consulta cerrada de equivalencia entre **dos reglas existentes**
del modelo booleano validado. `ABSOLUTE` pregunta por `SAT(XOR(F,H))`;
`CONTEXTUAL` pregunta por `SAT(D ∧ C_other ∧ XOR(F,H))`, excluyendo ambas
reglas comparadas de `C_other`. La consulta devuelve fórmula, no un veredicto
de producto. Se mantiene el límite de variables/AST/tiempo del analizador;
esta unidad no modifica el JSON público ni añade una ejecución de solver.

## Oráculos RED

- Si dos obligaciones difieren fuera de `D`, la consulta absoluta es SAT y la
  contextual es UNSAT.
- Si la diferencia existe dentro de `D` y las otras reglas, ambas son SAT.
  Incluir por error las reglas comparadas en `C_other` falsearía la contextual.
- Una tercera regla que prohíbe la diferencia hace UNSAT la contextual, sin
  cambiar la absoluta.
- Scope desconocido, ID desconocido o comparación de una regla consigo misma
  se rechazan con diagnóstico cerrado.
- Reescribir una obligación como regla de guarda `TRUE` puede conservar
  `no_output` y cambiar `gap`; el motor no las declara métricas equivalentes.

## Proceso

ODD → RED de las fórmulas y la métrica → GREEN → regresiones → RDD del
candidato exacto → respaldo GitHub. No se afirma equivalencia de la realidad
ni se altera RS3-D01/D02 o la autoridad humana.
