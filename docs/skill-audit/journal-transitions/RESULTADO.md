# WU-SUP-JOURNAL-003 — candidato aislado

El registro acepta RESERVED -> ACTIVE con PID positivo e identidad de inicio
explícita y ACTIVE -> STOPPING con la misma identidad. Ambos pasos usan fsync,
replace y bloqueo cooperativo. Tras cerrar/reabrir, ACTIVE o STOPPING no permiten
nueva reserva. RESERVED sin identidad de hijo sigue bloqueado.

RED: API de transiciones ausente. GREEN3tests específicos y46tests de suite.
No hay confirmación de terminación ni recuperación automática. La identidad
es declarada por un llamador confiable, no autenticada por este módulo. Todavía
no está conectado al lanzamiento real, reserva física o incorporación QA.

Preparado en worktree separado del candidato README pendiente de RDD. No commit,
no publicación, no RDD de esta unidad todavía. Ensayos acotados sin calibración
del hardware objetivo.
