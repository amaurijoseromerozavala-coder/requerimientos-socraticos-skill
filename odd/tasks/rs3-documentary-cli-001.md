# RS3-WU-DOCUMENTARY-CLI-001

## Objetivo

Exponer el comprobador estructural RS3-D01/D02 mediante la entrada portable
`scripts/requirements documentary-check <dossier.json>`. El helper permanece
documental, sin autenticación ni permiso de despliegue. El comando no incorpora
el resultado en un PRD canónico ni muta la fuente.

## Oráculos RED

- Entrada regular JSON acotada, válida: exit 0 y resultado estructurado
  `MODEL_ELIGIBLE` únicamente para el inventario declarado, con SHA-256 de los
  bytes efectivamente leídos para enlazar el resultado al expediente exacto.
- JSON con clave duplicada, archivo mayor de 256 KiB o enlace simbólico:
  exit 2, `INVALID_INPUT`, sin resultado parcial.
- El `--help` portable menciona la operación; intérprete ausente conserva
  `INTERPRETER_UNAVAILABLE` y no usa PATH implícito.
- Ninguna respuesta afirma autoridad o autorización de despliegue.

## Proceso

RED de CLI; implementación mínima; GREEN y regresiones; RDD exacto; commit y
push normal tras gate público. No se ejecutan tareas de producto ni ensayos
físicos.
