# WU-SEC-CAPTURE-INTEGRATION-002 — corrección tras RDD escalado

El linaje RDD anterior quedó escalado: una excepción para el campo JSON
`token` confundía metadatos de argumentos con una clave sensible independiente.
Esta unidad conserva el candidato anterior sin otorgarle aprobación y genera
una nueva identidad revisable.

RED: un JSON con `token` independiente cuyo valor comienza por `--` debe
mostrar que el saneador anterior lo dejaba intacto. GREEN: la copia elimina
ese valor; un objeto de argumento nativo con `name`, `value` y `token`
coherentes conserva opciones no sensibles. Un argumento `name=token` sigue
saneándose. Los controles usan únicamente valores ficticios.

La suite completa, el chequeo de evidencia pública y `git diff --check`
constituyen regresión. Gentle AI debe revisar y reconocer la identidad nueva
antes de un commit solo local. No hay push, cierre de alertas ni reescritura.
