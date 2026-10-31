# WU-SUP-CORE-001 — Núcleo ejecutable de procesos

Solicitud: «Continua el proceso», tras delimitar primera unidad ejecutable del
supervisor local. ODD/TDD/RDD y respaldo posterior son obligatorios.

## Alcance

Biblioteca Linux para un hijo directo de comando confiable fijado por el llamador,
sin shell ni evaluación QA. Un trabajo por instancia, plazos monotónicos, salida
acotada, límite virtual del hijo, SIGTERM/gracia/SIGKILL/espera acotada, registro
separado del motivo de parada y causa de señal. Incertidumbre de limpieza bloquea
la instancia sin mecanismo automático de desbloqueo. No CLI de evaluación integral.

No implementa aún diario durable, contabilidad de recibos, admisión QA, adaptadores,
incorporación, revocación de autoridad ni recuperación entre reinicios. No ofrece
sandbox ni control de descendientes arbitrarios. La muerte del padre se vincula
al hijo directo en Linux; no se promete captura de cualquier fallo kernel.
La integración permanece DRAFT, sin afirmar cumplimiento de todo el PRD.

## Aceptación y ensayos acotados

- Proceso real normal: capturar stdout/stderr/returncode y recolectar.
- Hijo real ignora SIGTERM, espera sin consumo intensivo: deadline corto, escalada
  a SIGKILL y returncode=-9 observado con cleanup=CONFIRMED.
- SIGKILL externo real: causa NOT_DETERMINED; no inferir OOM o timeout.
- Fallo simulado de espera: cleanup=UNCONFIRMED, INFRA_LOCK y segundo lanzamiento
  denegado. Recolectar realmente el fixture en teardown.
- Salida excesiva y argumentos inválidos: truncado acotado/rechazo previo.
- Observar RLIMIT_AS desde hijo, sin consumir el límite.
- Prueba exterior limita duración total; no estrés RAM/swap ni calibración i3.
- README debe distinguir núcleo implementado de supervisor completo pendiente y
  corregir el estado histórico de R3-001, con control previo RED.

## Secuencia

Registrar RED antes de implementación; GREEN y revisión independiente después.
RDD nativo exacto antes de commit/push. No cambiar controles globales ni credenciales.

## Log
RED módulo ausente conservado. Ocho tests iniciales GREEN. Revisor independiente encontró F1 en interrupción de wait; dos casos RED reproducidos. Corregido latch conservador antes de cleanup y creación incierta; diez tests finales GREEN. Revisión independiente de corrección bloqueada por cuota; RDD nativo pendiente. No publicación antes de cierre.
