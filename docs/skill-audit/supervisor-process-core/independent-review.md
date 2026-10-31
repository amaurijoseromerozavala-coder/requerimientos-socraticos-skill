# Revisión independiente parcial

Agente real `/root/supervisor_core_review`. Reprodujo 8 tests iniciales y encontró
F1: KeyboardInterrupt/SystemExit durante wait dejaba STOPPING y permitía nuevo
lanzamiento; reprodujo un hijo vivo con bloqueo liberado, y lo limpió en teardown.
También identificó incertidumbre durante creación antes de asignar el hijo.

El coordinador reprodujo RED de F1 (dos fallos), corrigió el latch INFRA_LOCK antes
de limpiar y conservó incertidumbre durante creación. La revisión independiente
de la corrección no terminó: el agente informó agotamiento de cuota. No se
cambiaron credenciales ni se eludió esa limitación. Estado: PARTIAL_REVIEW;
F1 corregido y comprobado por el coordinador, reconfirmación independiente pendiente.

El RDD nativo del candidato final todavía no se ha ejecutado. Este archivo no es
un recibo de aprobación ni una certificación de aislamiento.
