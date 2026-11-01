# WU-README-STATE-001 — candidato para RDD

Se corrigió un hallazgo aplicable de QA: README presentaba el supervisor local
ampliado como solo DRAFT y decía que aún faltaban diario durable e integración QA.
Ahora enumera núcleo, adaptador interno, reserva persistente y sistema completo
pendiente. La reserva se limita a RESERVED y no gobierna aún el lanzamiento.

Contraste: XERJ CLI y MCP localizaron process_core.py, qa_adapter.py y journal.py.
Lectura de Git/archivos confirmó que `boolean_model_final.json`, `2026-10-31-PRD-CONSOLIDADO.md`,
un subsistema VWAP y un colector SQLite no están en este repositorio. Sus exigencias
no se promovieron a requisitos ni cambios de código. La FSM parcial del diseño
integrado sigue declarada como incompleta. La evidencia humana del equipo WSL
indica swap0 en la última medición; no se afirmó estrés o paginación comprobada.

RED: checker detectó falta de fila núcleo. GREEN: checker de estados pasó.
Control negativo en copia temporal eliminó fila adaptador y falló con diagnóstico
específico. No tests físicos ni cambio de código ejecutable. RDD nativo pendiente.
