# WU-RS3-D05-MOUNT-OPTION-BOUNDARY-042

## Objetivo y alcance

El RDD de WU041 dejó la advertencia `R3-001`: el detector `9p` buscaba
`aname=drvfs` como subcadena y podía clasificar `aname=drvfs-backup` como un
montaje Windows. Corregir únicamente esa comparación en las dos rutas del
sondeo D05 y conservar el formato WSL `aname=drvfs;path=...`. No ampliar el
gate de autoridad ni cambiar el procedimiento de instalación.

## Oráculos RED congelados

1. Un `9p` con `aname=drvfs-backup` o `other=aname=drvfs` no se clasifica como
   Windows aunque su raíz sea escribible.
2. `9p` con la opción completa `aname=drvfs` o el valor seguido de parámetros
   WSL `;path=...` sí se clasifica. `drvfs` como tipo de FS sigue reconocido.
3. El sondeo conserva `authority_verification=NOT_ESTABLISHED` y
   `execution_authorized=false`; la ausencia de detección es `NOT_ASSESSED`,
   no una prueba de aislamiento.

ODD → RED → corrección mínima → GREEN/regresión → revisión independiente →
RDD del candidato exacto → respaldo Git. No hay ensayos materiales nuevos en
el i3/WSL; permanecen `NOT_RUN`.

## Evidencia local

- RED: `Ran 18 tests`, `FAILED (failures=1)`; `aname=drvfs-backup` se
  clasificaba erróneamente como `EXPOSED`.
- GREEN: `Ran 18 tests`, `OK`. La comparación exige `aname=drvfs` como opción
  completa y admite parámetros WSL posteriores delimitados por `;`.
- Regresión `ci/run_quality.sh` exit 0: CI 55, supervisor 175, QA 62,
  requisitos 429, todos `OK`; Python 3.12 con `z3-solver==4.15.4.0`.
- CI remoto de la unidad precedente WU041 terminó `success` para el commit
  `640ed140489c4aeab44a25e130d59b91b54539d8`. No es prueba de WU042.
