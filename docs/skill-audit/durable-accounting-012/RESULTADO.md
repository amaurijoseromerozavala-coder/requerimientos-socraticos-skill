# WU-SUP-DURABLE-012 — evidencia previa a RDD

Estado: CANDIDATO; RDD pendiente. No certifica producción ni calibración del i3/WSL.

## Alcance y cambio

El enlace optativo del núcleo al journal reserva capacidad lógica antes de lanzar, conserva stdout, stderr y un recibo de proceso en archivos privados, verifica sus hashes y vuelve a IDLE tras terminación confirmada. Una reapertura solo reconcilia un terminal con captura STORED verificable. Estados inciertos y artefactos no contabilizados impiden admisión. El adaptador QA aún no usa este enlace.

## ODD → RED → GREEN

- ODD: `odd/tasks/durable-capture-reconciliation.md`, creado antes de modificar código.
- RED inicial: `python3 -B -m unittest supervisor.tests.test_durable_reconciliation -q` falló por ausencia de `store_capture`, `accounting`, `reconcile_terminated` y falta de reutilización.
- RED de recuperación: el caso `test_reopen_reconciles_only_verified_terminal_capture` observó `CONFIRMED_TERMINATED` donde exigía `IDLE`.
- RED de contabilidad: `test_unaccounted_root_staging_blocks_admission` observó una admisión indebida ante archivo `.pending-unaccounted`.
- Primer RDD: aprobado y reconocido para el candidato anterior, con observación R3-001: el test de capacidad estaba enmascarado por una reserva sin resolver. La prueba fue corregida: completa 99 ejecuciones journal, verifica IDLE y exige `RETENTION_CAPACITY_EXCEEDED` en la siguiente reserva. El RDD del candidato corregido queda pendiente.
- GREEN del candidato corregido: `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh`: CI 7, supervisor 73, QA 62, requisitos 262 pruebas OK. La corrida previa del supervisor pasó 72 pruebas antes de añadir el control de capacidad. `git diff --check`: sin errores.

## Frontera de la conclusión

La reserva de 335872 bytes por ejecución es contabilidad cooperativa; `fstatvfs` comprueba el espacio visible, pero no reserva bloques físicos ni demuestra capacidad libre del volumen anfitrión Windows. El máximo de 32 MiB permite 99 reservas completas de 335872 bytes. Un almacén anterior sin `accounting.json` queda cerrado hasta una migración explícita futura. No hay borrado automático, recuperación de RESERVED/ACTIVE/STOPPING, contención de procesos fuera del grupo, integración QA durable ni calibración en el equipo objetivo.
