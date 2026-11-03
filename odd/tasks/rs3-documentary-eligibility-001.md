# RS3-WU-DOCUMENTARY-ELIGIBILITY-001

## Decisión humana y frontera

RS3-D01: `production_ready` significa elegibilidad para **revisión documental**,
no aptitud de despliegue ni permiso operativo. RS3-D02, respondida por el
maintainer: «Todos los requisitos aplicables, con evidencia actual y sin
brechas críticas». Esta unidad implementa una evaluación estructural del
expediente **declarado**. No acredita que el inventario sea realmente completo,
que la evidencia sea verdadera o que el actor tenga autoridad. La revisión
humana/QA y el permiso de despliegue son gates independientes.

## Oráculos RED

- Inventario declarado completo, no vacío, con todos los requisitos aplicables
  SUPPORTED y evidencias declaradas CURRENT ligadas al snapshot actual, sin
  brechas críticas: `MODEL_ELIGIBLE` solo para revisión documental.
- Un requisito aplicable no respaldado, evidencia STALE/MISSING o de otro
  snapshot, o una brecha crítica produce `NOT_ELIGIBLE`.
- Aplicabilidad desconocida, inventario no declarado completo o cero
  requisitos aplicables producen `INCONCLUSIVE`, nunca éxito por vacuidad.
- IDs duplicados, estados desconocidos o evidencia incoherente se rechazan
  como entrada inválida; una exclusión NOT_APPLICABLE necesita una base.
- Toda salida conserva `authority_verification=NOT_PERFORMED` y
  `deployment_authorized=false`.

## Tareas

RED, evaluador puro y acotado, GREEN/regresión, documentación de D02 en
README/SKILL, RDD exacto, commit y respaldo normal tras gate público. El estado
CURRENT es una **declaración** que solo se contrasta con la identidad de
snapshot suministrada: no se valida el contenido ni la vigencia física.
