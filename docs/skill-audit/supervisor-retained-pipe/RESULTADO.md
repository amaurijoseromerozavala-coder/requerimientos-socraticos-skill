# WU-SUP-CORE-003 — Captura incompleta con hijo recolectado

Estado: COVERAGE_ADDED_TESTS_PASS_RDD_PENDING.
Observación: review-7f20158690dc0591/R3-001.

El núcleo ya cumplía el caso: no se modificaron process_core.py ni _child_entry.py.
Prueba real Linux: hijo directo termina con 0, descendiente conserva stdout/stderr
abiertos; supervisor retorna cleanup=CONFIRMED, capture_complete=false, sin enviar
señales y con motivo WALL_DEADLINE, en ~0,60 segundos observados. La aserción permite
hasta 2 segundos por planificación; no afirma tiempo real.

El fixture corre en proceso aislado, configura subreaper para adoptar al
descendiente, verifica que seguía vivo al retornar el núcleo y después lo recolecta
cuando termina su espera finita de 3 segundos. waitpid confirma ausencia de hijos
restantes. El proceso principal de la suite no cambia de rol subreaper.

TDD honesto: no hubo RED funcional sobre el núcleo actual. El control negativo
modifica solo una copia temporal a capture_complete=true; el caso falla con
CAPTURE_MUST_BE_INCOMPLETE (exit 1), sin fallo de limpieza del fixture. La prueba
positiva pasa. La suite completa suma 16 tests OK en ~9 segundos. Logs originales
conservados; stdout de suite completa contiene también capturas voluminosas de
regresiones anteriores y no forma parte del contexto seleccionado de revisión.

Esto cubre la distinción recolección/EOF, no contención de descendientes,
recuperación durable ni calibración i3/WSL. RDD y publicación pendientes.
