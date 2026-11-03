# WU-SEC-HISTORY-CI-002 — base verificada tras reconstrucción de historia

## Specs

El primer workflow tras actualizar la rama reconstruida observó una base del
evento que ya no existe en el checkout nuevo. El gate respondió `unknown=1` y
bloqueó. La unidad ofrece una excepción puntual y verificable para esa
transición, sin aceptar bases ausentes de forma general.

Solo cuando el evento de push declara una actualización forzada y su `before`
es el OID público anterior fijado, el workflow usa el OID de la base saneada.
Debe verificar que esa base existe y es ancestro de `HEAD`. Cualquier otra
base ausente continúa fallando cerrada. El control de historial alcanzable
permanece activo y las actualizaciones normales usan `before` sin sustitución.

## Oráculos

RED: el workflow actual no contiene selección puntual de base y el primer
workflow remoto falló con `EVIDENCE_CHANGED ... unknown=1`.

GREEN: pruebas de contrato para la guarda exacta, selección normal y fallo si
la base saneada no es ancestro; suite completa y CI remoto tras publicación.
RDD revisa el candidato exacto antes del commit y de la actualización normal.

No se reinterpreta la ejecución fallida como PASS. Los documentos históricos
con estructura ambigua permanecen fuera del alcance de este control de cambio.
