# WU-RS3-TRACEABILITY-UPDATE-004

## Objetivo y precedencia

Actualizar la instantánea de trazabilidad RS3 después de
WU-RS3-PROPOSAL-BINDING-003, respaldada en
`ec164df5b4c12e8a1b438a389fb5f35e19dc8627`. El paquete sigue siendo
`DRAFT_PROPOSED_NOT_RATIFIED`. Depende del RDD reconocido de esa unidad y del
generador de reconciliación vigente.

## Alcance

Enlazar únicamente RS3-REQ-036, RS3-REQ-041 y RS3-REQ-047 con la evidencia de
la unidad anterior; actualizar el HEAD observado y el resumen. No promover
requisitos, tareas o casos a PASS; no modificar CandidateIR/EARS ni autoridad.

## Oráculo TDD

RED: la matriz actual no tiene `evidence_refs` para esos tres IDs y conserva
un HEAD de auditoría anterior. GREEN: el generador reproduce byte a byte el
nuevo registro desde el ZIP identificado, las tres filas apuntan a un recibo
existente, todas conservan `NOT_VERIFIED_PER_REQUIREMENT`, y los 52 casos del
paquete siguen `NOT_RUN_AS_PACKAGE_CASE`.

RED observado: el nuevo test falló por el HEAD anterior
`cc95580f6f5d9177d9467f5ed3d4bd0e19a82bd9`. GREEN observado: los siete
tests focalizados pasaron con el ZIP identificado y la matriz regenerada.

Regresiones: suite CI, control de rutas y marcadores históricos. RDD del
candidato exacto; respaldo Git solo tras reconocimiento.

## Límite

La aprobación RDD revisó parches sin ejecutar comandos. El enlace demuestra
trazabilidad de una mejora parcial, no fidelidad semántica completa, autoridad
humana ni habilitación de producción.
