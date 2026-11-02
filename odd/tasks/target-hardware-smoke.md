# WU-TARGET-SMOKE-005 — evidencia acotada del i3/WSL

## Fuente y alcance

El propietario entregó el resultado de una ejecución local sobre el commit `6ca7fe48ecd730cbe58e3872bdeff00c45631a61`: 62 pruebas del supervisor OK bajo controles previos de memoria, disco e I/O. Se registra como evidencia **USER_REPORTED**; no se recibieron stdout/stderr crudos, medición independiente ni trazas del sistema operativo. Esta unidad actualiza el estado documental del hardware objetivo sin modificar producto, CI, permisos ni comportamiento de admisión.

## Criterios de aceptación

- El registro conserva HEAD exacto, comando, límites, gates, exit, duración total, duración unittest, pico RSS y observaciones posteriores, distinguiendo fuentes Windows/WSL.
- El README deja de decir que no hubo ninguna ejecución en el hardware objetivo, pero no presenta esta corrida como calibración bajo saturación ni aprobación de producción.
- El control documental rechaza un registro sin procedencia, con resultado distinto de 62 OK o con atribución de causa a los cambios de memoria/PSI. También rechaza un README que proclame READY para producción.
- Ningún dato privado o `.update.log` se incorpora.

## Tareas

1. RED documental sobre README/evidencia todavía ausente.
2. Crear registro estructurado y actualizar README; GREEN y control negativo con mutaciones en memoria; verificar regresión documental.
3. RDD nativo Gentle AI del candidato exacto; reconocer recibo y publicar solo después de aprobación.

## Registro

- 2026-11-01 (hora cliente): ODD abierto antes de editar la evidencia y README.
- 2026-11-01 (hora cliente): RED 1 rechazó evidencia ausente; RED 2 rechazó README todavía desactualizado. GREEN documental OK. Tres mutaciones en memoria (conteo, autoridad, procedencia de logs) fueron rechazadas. `git diff --check` sin errores. No se ejecutaron de nuevo las pruebas en el i3; se registró el reporte entregado por el propietario.
