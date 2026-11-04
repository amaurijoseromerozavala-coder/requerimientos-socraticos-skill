# WU-RS3-D05-TEST-PORTABILITY-015

## Origen y alcance

Gentle AI aprobó WU-014 con la observación informativa `R3-001`: dos tests
sintéticos dependen de UID/capacidades reales del runner. Corregir únicamente
esa fragilidad de pruebas. No cambiar el sondeador, sus salidas, permisos o
la política de autoridad. El i3/WSL objetivo sigue NOT_RUN.

## Oráculos RED congelados

1. Simular que el runner es root reproduce el fallo del caso favorable actual.
2. Simular capacidades efectivas no nulas reproduce el fallo del caso de
   directorio ausente actual.
3. Los tests corregidos usan identidades no privilegiadas y metadatos
   sintéticos explícitos; el resultado favorable local jamás habilita D05.
4. La suite bajo el runner normal y las regresiones siguen pasando.

RED observado → corrección mínima del test → GREEN/regresión → RDD exacto →
respaldo Git. No hay credenciales reales, sudo ni cambios del host.

## Evidencia local RED/GREEN

- RED: bajo `mock.patch(os.getuid, return_value=0)`, el test favorable anterior produjo 1 fallo; bajo `mock.patch(_effective_caps, return_value='NONZERO')`, el test de directorio ausente anterior produjo 1 fallo.
- GREEN: repitiendo esas mismas dos simulaciones tras fijar UID/metadatos sintéticos y capacidades explícitas se observaron 0 fallos. Las 5 pruebas focalizadas terminaron OK.
- Regresión: `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh` terminó exit 0: 55 CI, 127 supervisor, 62 QA y 342 requisitos.
