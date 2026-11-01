# WU-SUP-JOURNAL-001 — Reserva persistente sin desbloqueo

Primera primitiva interna del contrato recovery-contract.json: inicialización
explícita de directorio nuevo, propietario cooperativo exclusivo, estado IDLE y
reserva RESERVED persistida antes de que una futura integración pueda lanzar.
No lanza procesos de aplicación ni reserva capacidad de disco. Ninguna API de
reset, limpieza, recuperación ni confirmación de terminación en esta unidad.
La integración no podrá usar esta primitiva sola como autorización de lanzamiento:
faltan reserva física, identidad del checker y journal ACTIVE/STOPPING.

Garantía acotada: flock cooperativo sobre inode estable, escrituras mediante
archivo temporal+fsync+replace+fsync de directorio, lectura acotada; no garantía
contra cuenta/root, fallos físicos o almacenamiento que incumpla fsync. Directorio
nuevo explícito; falta/corrupción del journal existente bloquea sin recreación.
Reserva sin terminación probada bloquea también tras cerrar/reabrir o morir dueño.

RED API ausente; GREEN pruebas en temporales: exclusión, corrupción/ausencia,
reserva persistente tras salida abrupta de proceso auxiliar propio, error fsync
sin éxito y sin reutilización de instancia. No ensayos de saturación ni i3.
RDD exacto y GitHub después de aprobación. Sin conexión todavía con adaptadorQA.

## Log
RED API ausente; RED guardia por instancia ausente. GREEN12tests de journal y
41tests de suite. Primitiva sin desbloqueo ni lanzamiento. RDD pendiente.
