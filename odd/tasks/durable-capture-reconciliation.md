# WU-SUP-DURABLE-012 — contabilidad y reconciliación terminal

## Fuente y alcance

El propietario pidió corregir brechas válidas del último dictamen QA y avanzar una unidad amplia hacia producción. `recovery-contract.json` exige no pasar de `CONFIRMED_TERMINATED` a `IDLE` hasta reconciliar recibos y capacidad. SUP-014/015 exigen conservar stdout, stderr y recibo en archivos separados, máximo 100 ejecuciones, 32 MiB compartidos y reserva previa de 335872 bytes. Esta unidad enlaza esos requisitos en el **núcleo con journal optativo**; aún no convierte `QASupervisor` en supervisor durable ni autoriza producción.

## Diseño y aceptación

- `Journal.initialize` crea contabilidad y almacén privados. `reserve` exige contabilidad legible y reserva 335872 bytes antes de `RESERVED` y antes de cualquier lanzamiento. La reserva única por `run_id` permanece si el flujo se interrumpe; no hay expiración ni borrado automático.
- Después de terminación y grupo confirmados, guardar stdout, stderr y recibo de proceso separados, con límites y hashes de los bytes, fsync y permisos 0600. Si la escritura o comprobación falla, la instancia permanece bloqueada y no proclama retención durable.
- `CONFIRMED_TERMINATED → IDLE` solo si la contabilidad STORED, la identidad de proceso y los bytes retenidos coinciden con el recibo. La misma instancia puede entonces ejecutar otra tarea; los estados RESERVED, ACTIVE, STOPPING o evidencia incierta nunca se limpian por tiempo o PID ausente.
- Si se interrumpe entre almacenar el recibo y reconciliar, la reapertura verifica el recibo antes de terminar esa transición. Un archivo de staging no contabilizado bloquea la reapertura; no se elimina automáticamente.
- Presupuesto/contador se calculan incluyendo reservas incompletas; se rechaza el siguiente lanzamiento cuando no cabe. Sin aplicación objetivo, procesos arbitrarios ni ensayo de saturación.

## RED propuesto

1. Dos tareas correctas secuenciales con journal reutilizan la instancia solo después del recibo durable. El código previo deja terminal e INFRA_LOCK.
2. Una segunda reserva del mismo `run_id` o una nueva que exceda 32 MiB no lanza.
3. Un recibo o salida alterados impiden la reconciliación; un estado RESERVED ambiguo no se libera.
4. Una falla de persistencia después de terminación bloquea la instancia.
5. La reapertura recupera solo un terminal con captura STORED verificable; un artefacto parcial fuera del ledger impide admisión.

## Gates

Conservar RED/ GREEN, ejecutar suite completa y RDD de Gentle AI para el candidato exacto. Publicar la unidad solo con recibo aprobado/reconocido; verificar CI remoto. Calibración i3/WSL sigue NOT_RUN.
