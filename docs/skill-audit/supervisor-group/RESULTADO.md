# WU-SUP-GROUP-001 — resultado local previo a RDD

La prueba RED observó que el descendiente del mismo grupo seguía en ejecución tras el plazo; `red.stderr` registra el fallo específico. La implementación dirige SIGTERM y SIGKILL al grupo solo mientras verifica que el hijo vivo conserva el PGID esperado. La prueba específica pasó en GREEN y la suite completa del supervisor terminó con 47 pruebas OK.

Este cambio no aísla todos los descendientes, no recolecta nietos y no recupera un registro persistente. Si el hijo directo termina antes de la limpieza, no se atribuye a esta unidad el control de cualquier grupo restante. `cleanup=CONFIRMED` sigue refiriéndose al hijo directo. No se ejecutaron cargas intensivas ni calibración del i3/WSL. El candidato aún requiere RDD; este resultado no declara aprobación.
