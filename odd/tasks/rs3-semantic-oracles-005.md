# WU-RS3-SEMANTIC-ORACLES-005

## Objetivo y fuente

RS3-REQ-038, RS3-REQ-040, RS3-REQ-043 y RS3-REQ-045 son propuestas del ZIP
RS3; la autoridad humana vigente exige no inventar interpretación. Construir
un oráculo independiente y **acotado** para frases sintéticas inequívocas en
español. No se pretende interpretar lenguaje natural general.

## Gramática de prueba y contrato

Reconocer solo `P solo si Q`, `P si Q`, `P si y solo si Q` y
`Si Q, entonces P`, con identificadores ASCII acotados. Para una coincidencia
exacta, contrastar sujeto, condición, clase y dirección propuestos por el LLM.
Un desacuerdo, negación no modelada o texto fuera de esta gramática impide
compilar el AST y devuelve `NEEDS_CLARIFICATION`; la causa queda explícita.
El oráculo no confirma intención humana ni otorga permisos.

## Oráculo RED congelado

1. Una propuesta coordinadamente invertida sobre `P solo si Q` no debe
   producir `Q→P`, aunque su `kind` y `direction` concuerden entre sí.
2. `P si Q` debe producir `Q→P`, y `P solo si Q` debe producir `P→Q`, según
   sus cuatro valuaciones booleanas independientes.
3. `P solo si no Q`, texto con instrucciones incrustadas y texto no reconocido
   deben quedar inconclusos, sin AST ni EARS normativo.
4. El test previo que cambia el sujeto a `production_ready` sin cambiar la
   fuente literal es inconsistente; corregir su fixture de forma explícita,
   no debilitar el nuevo oráculo.
   También se corrige el test que cambia clase/dirección entre necesaria,
   suficiente y equivalencia sin cambiar su texto fuente. Ese defecto de
   fixture apareció al ejecutar la suite completa después del primer GREEN
   focalizado.

GREEN: suite focalizada, suite Requerimientos Socráticos y regresiones CI.
RDD exacto y respaldo Git posterior. D03/D05 y producción siguen bloqueados.

## Límite material

El patrón fijo no prueba fidelidad para frases fuera de su gramática; esas
frases permanecen `NEEDS_CLARIFICATION`. La referencia y el texto fuente
continúan siendo suministrados por el llamador; no se autentica su origen.
No se incorpora un LLM ni se ejecuta Z3 en esta unidad.

## Observaciones TDD

RED observado: los nuevos tests fallaron ocho veces por ausencia de
`semantic_fidelity`; antes del oráculo, una propuesta invertida aún obtenía
AST. Después de implementarlo, la suite completa descubrió un test antiguo de
EARS que cambiaba modalidad lógica sin cambiar su texto fuente. Se corrigieron
las frases del fixture, conservando las aserciones sobre dirección. GREEN:
320 tests de Requerimientos Socráticos y 52 de CI local pasaron; un test CI
dependiente del ZIP externo quedó omitido explícitamente.
