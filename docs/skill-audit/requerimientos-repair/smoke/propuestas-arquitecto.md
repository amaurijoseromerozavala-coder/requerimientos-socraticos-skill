# Propuestas literales del arquitecto interrogador

Emitidas por un proceso Codex independiente durante la prueba de reparación. Son propuestas con evidencia pendiente, no decisiones humanas aceptadas ni cambios aplicados a QA.

## P1 — EVIDENCE_PENDING

El gate documental está respaldado por pruebas acotadas, pero sigue NOT_PROVEN que la transición efectiva a READY invoque obligatoriamente el validador. Los fixtures con metadatos RDD sintéticos no resuelven esa incertidumbre. Conviene hacer explícito qué evidencia permite declarar cada garantía, sin presentar esta incertidumbre como un defecto demostrado del runtime.

### P1-A0

Baseline: conservar el validador documental existente, la obligación contractual de usarlo y la distinción actual entre pruebas documentales y cumplimiento universal NOT_PROVEN.

- Las 34 pruebas satisfactorias respaldan las condiciones documentales evaluadas.
- La evidencia suministrada no demuestra una invocación obligatoria en todas las transiciones efectivas a READY.

### P1-A1

Proponer para la skill un contrato de evidencia de cierre que vincule cada declaración de READY validado con la versión o hash del validador, los hashes de los documentos evaluados, el resultado y un recibo de ejecución real. Mantener separadas la validación documental, la evidencia RDD y la ejecución efectiva de la transición; declarar UNKNOWN cuando falte su vínculo. Esta propuesta se limita a contratos y verificación de la skill.

- Permite contrastar una declaración de cierre con los artefactos concretamente evaluados.
- Añade mantenimiento de recibos y exige renovarlos cuando cambien los documentos.
- Un recibo acredita una ejecución concreta; por sí solo no impide que otro consumidor omita la validación.
- Su compatibilidad con los contratos actuales requiere evidencia adicional.

**Hipótesis:** Un contrato que vincule declaraciones de cierre con ejecuciones y documentos identificables hará detectables los cierres sin evidencia correspondiente, dentro del flujo documental evaluado.

**Falsador:** La hipótesis queda refutada si el flujo documental evaluado admite una declaración de READY validado con un recibo ausente, fallido o correspondiente a otros documentos. Si el contrato vigente ya detecta todos esos casos con evidencia equivalente, no se justifica añadir otro mecanismo.

## Límites declarados por el arquitecto

- Se utilizó exclusivamente la evidencia suministrada; no se consultaron herramientas ni se implementaron cambios.
- Los hashes coincidentes prueban igualdad de contenido de los 19 archivos inventariados entre las observaciones, no ausencia de modificaciones intermedias ni integridad fuera del inventario.
- Las 34 pruebas respaldan el gate documental descrito; no acreditan recibos RDD reales ni cumplimiento universal del runtime o de cualquier LLM.
- S-MCP acredita un registro histórico en Engram. No se suministraron descubrimiento MCP, topología CodeGraph ni consultas Context7; no se presuponen esas consultas.
- S-WEB aporta fundamento metodológico sobre atributos de calidad y tradeoffs, no evidencia tecnológica ni autorización de políticas. No se suministraron la consulta web ni un recibo completo de lectura.
- Falta inspección del contrato vigente para determinar si la alternativa aporta una capacidad nueva. No consta aceptación humana de la propuesta.
