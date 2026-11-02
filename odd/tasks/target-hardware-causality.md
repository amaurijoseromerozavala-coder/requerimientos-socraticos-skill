# WU-TARGET-CAUSALITY-006 — observación R3-1

## Fuente y alcance

El RDD aprobado de WU-TARGET-SMOKE-005 dejó R3-1: `check_evidence.py` no comprueba la obligación documental de no atribuir causalidad a los cambios de memoria Windows o PSI I/O. Esta unidad endurece únicamente el contrato del registro `observation.json` y su control negativo. No modifica mediciones, código del supervisor ni conclusiones físicas.

## Oráculo y criterios

- Cambiar en memoria la limitación «No cause is assigned...» por una atribución causal debe ser rechazado; antes de la corrección el control negativo debe fallar porque `verify` la acepta.
- La lista de límites del registro debe pertenecer al vocabulario exacto aprobado para este informe cerrado. Un texto extra o sustituido obliga a revisión de candidato y no pasa el chequeo documental.
- El registro original permanece válido. Se vuelven a ejecutar los controles documentales y se conserva la distinción USER_REPORTED/NOT_PROVIDED.
- No se afirma detección general de causalidad en cualquier lenguaje natural ni autenticación de la medición humana.

## Tareas

1. RED: control negativo de atribución causal contra el checker vigente.
2. GREEN: limitar las afirmaciones admitidas y comprobar regresiones del informe.
3. RDD del candidato exacto, reconocer recibo y publicar solo con aprobación.

## Registro

- 2026-11-01 (hora cliente): ODD abierto antes de editar el verificador.
- RED: `negative_causality.py` terminó con exit 1 y `CAUSAL_ATTRIBUTION_ACCEPTED_UNEXPECTED` frente al verificador previo; registro en `causality-red.stderr`.
- GREEN: el mismo control terminó con exit 0 y `CAUSAL_ATTRIBUTION_REJECTED_EXPECTED` después de exigir la lista exacta de limitaciones.
- Regresión: el informe original emitió `DOCUMENTARY_CONTRACT_OK`; cuatro mutaciones de conteo, autoridad, procedencia y límite extra fueron rechazadas.
- No se repitieron mediciones en hardware; el cambio es de contrato documental. RDD pendiente.
