# WU-SUP-JOURNAL-002 — candidato pendiente RDD

Resuelve observaciones review-ef2bb19372d7c729/R4-001 y R3-001.
RED: fsync y unlink fallan; OSError secundario ocultaba JournalBlocked original.
Corrección: limpieza solo en error y si se creó temporal propio; conserva causa
primaria, anota CLEANUP_FAILED/errno secundario y mantiene bloqueo de instancia.
No cleanup redundante tras replace/fsync exitosos. No nueva recuperación/reset.

Pruebas públicas de registro: state duplicada con últimoIDLE, schema desconocido,
RESERVED sin identidad, IDLE con identidad, estado desconocido. Todos bloquean
sin reescribir bytes. Ya pasaban en producción anterior: brecha era de cobertura.
Control negativo reemplaza hook por dict en copia temporal y detecta exactamente
admisión indebida de clave duplicada. No confundir ese fallo esperado con defecto
actual del parser.

14tests journal y43suitePASS. Inyección de fallos acotada, no cambio de montaje ni
ensayo físico de SSD/WSL. Sin integración de lanzamiento, reserva física o CI.
RDD pendiente; logs originales y control reproducible conservados.
