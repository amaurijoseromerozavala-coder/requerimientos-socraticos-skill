# WU-SUP-PRE-REAP-007 — resultado previo a RDD

El supervisor Linux observa la salida del hijo con `waitid(WNOWAIT)`, conserva su PID mientras identifica el grupo y solicita terminación acotada de sus miembros activos antes de `wait()`. Después de una escalada, utiliza el plazo de limpieza para observar el grupo antes de recolectar. Una limpieza posterior a la salida normal del hijo se clasifica `STOPPED/GROUP_CLEANUP`, de modo que el adaptador QA no incorpore el resultado como salida ordinaria.

Cuatro controles RED capturan el comportamiento anterior; la suite final ejecutó 64 pruebas con resultado OK. Los registros del control y el resumen de la suite están en este directorio. Son ensayos locales acotados, sin saturación ni medición en el i3/WSL del propietario.

La unidad no contiene miembros que abandonen el grupo, no implementa reconciliación del journal ni recupera estados bloqueados. Una observación incierta mantiene `INFRA_LOCK`. RDD: pendiente.
