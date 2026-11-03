# WU-RS3-RECONCILIATION-BUILDER-ORACLES-002

## Origen y alcance

Hallazgo informativo R3-001 de la revisión `review-d5395473e2bd9b8d`:
los tests del inventario no ejercitan el generador. Añadir oráculos de
rechazo de paquete distinto y reproducción exacta desde el paquete RS3
identificado. No se amplía la adopción de requisitos ni se cambia la matriz.

## RED congelado

1. Un ZIP con un byte cambiado debe producir `PACKAGE_IDENTITY_MISMATCH`
   antes de leer miembros.
2. Desde el ZIP identificado y el HEAD de auditoría, el generador debe emitir
   exactamente los bytes del registro versionado.
3. Si el ZIP no está disponible, la prueba de integración debe declararse
   `NOT_RUN` mediante skip; la prueba negativa sintética sigue ejecutándose.

RED observado: `test_identified_source_reproduces_versioned_matrix` falló
con `AttributeError` porque `render` todavía no existía; el otro caso pasó.
GREEN observado: ambas pruebas pasaron localmente con el ZIP identificado.
La suite CI local ejecutó 51 tests, con una omisión explícita por falta del ZIP
externo. En CI, el caso que
requiere el archivo externo se omite explícitamente. Regresiones: suite CI,
marcadores históricos y diff. RDD del candidato exacto y respaldo Git tras
reconocimiento; nunca se afirma aceptación de los 107 requisitos.

## Restricciones

No versionar el ZIP ni rutas personales. No alterar el generador para ocultar
un fallo del test. El paquete no se extrae ni ejecuta. El hash del ZIP es una
identidad de bytes, no una firma de autoría.
