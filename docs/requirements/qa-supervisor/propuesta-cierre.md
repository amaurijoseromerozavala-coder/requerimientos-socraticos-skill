# Propuesta concreta de cierre

Solo supervisor invocador QA local, una ejecución simultánea, sin reintentos
automáticos ni autorización de aplicaciones/CI/producción. Linux/WSL con controles
requeridos; otra plataforma o capacidad ausente devuelve no soportado.

Presupuesto provisional de diseño:30s de ejecución,2s de gracia y2s de observación
tras parada; stdout256KiB, stderr64KiB; espacio virtual worker256MiB y supervisor128MiB.
No son RSS ni garantías de disponibilidad física, rendimiento o tiempo real.
Si no alcanza el presupuesto, falla/refusa sin expandirlo automáticamente.

Diario persistido antes de lanzamiento y reconciliación de identidad de ejecución;
incertidumbre al reiniciar mantiene INFRA_LOCK. PID aislado no basta.
Clasificación y notificación local separadas, sin equiparar incompleto con fallo
confirmado. Protocolo estricto vinculado a bytes/versiones del checker.

## Retención vigente

El humano sustituye recibos mínimos por conservación acotada de stdout/stderr:
32 MiB compartidos, eliminación manual, sin plazo de caducidad. Acceso del
propietario; hasta100ejecuciones; stdout256KiB, stderr64KiB, recibo8KiB.
Se reservan335872bytes y una plaza antes del lanzamiento. Se contabilizan archivos
parciales y reservas. Si no hay capacidad, no se inicia otra ejecución ni se borra
ninguna anterior. El diario permanece separado y su bloqueo no se libera al borrar.

Los recibos estructurados siguen separados de las salidas crudas. No se guardan
logs crudos del SO. Estos límites son de bytes lógicos, no una cuota física del SSD.

PRD DRAFT pendiente de revisión exacta del nuevo candidato. La aprobación RDD
anterior es histórica. Implementación, calibración, CI y producción no autorizadas.
