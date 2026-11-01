# WU-SUP-JOURNAL-003 — Identidad y transición de ejecución

Fuente: recovery-contract.json. Alcance de primera transición: RESERVED -> ACTIVE
con PID positivo e identidad de inicio observada por el padre de su hijo directo,
y ACTIVE -> STOPPING antes de solicitar término. Persistir cada cambio con la
misma técnica atómica existente. Mantener RESERVED si el padre muere antes de
ACTIVE. Reabrir cualquier estado no IDLE sin permiso de nueva reserva; no
recuperación automática ni confianza en PID solo.

No conectar aún el journal a process_core/qa_adapter; una llamada arbitraria a
record_active no autentica identidad. API para llamador confiable único. No emitir
CONFIRMED_TERMINATED/IDLE hasta contrato de evidencia y contabilidad posterior.

RED API ausente y mutación de PID/reutilización; GREEN casos de secuencia,
crash y estado inválido, regresiones; RDD independiente antes de publicación.

## Log
RED API ausente, GREEN3tests nuevos y46suite. Candidato aislado; RDD pendiente.
