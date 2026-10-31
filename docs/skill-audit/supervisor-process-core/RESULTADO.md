# WU-SUP-CORE-001 — Núcleo ejecutable local

Implementado y probado localmente; RDD pendiente. No habilita producción.

Biblioteca Linux para un hijo directo confiable. Captura acotada, RLIMIT_AS y CPU
aplicados por launcher antes de exec, reloj monotónico, SIGTERM/gracia/SIGKILL,
espera acotada y bloqueo de la instancia ante recolección no confirmada.
La señal observada no se convierte automáticamente en diagnóstico OOM.

## Evidencia

RED inicial: módulo inexistente (no se atribuye cobertura conductual a ese fallo).
La revisión independiente encontró una reapertura indebida tras interrupción de
wait; RED de regresión: dos fallos. Tras corrección: 10 tests pasan en ~1 segundo.
La versión final añade controles de creación interrumpida y concurrencia; son
regresiones adicionales, no RED inventado. Logs final-green.stdout contienen
PID, returncode, solicitudes de señal, cleanup, duración y salidas hexadecimales.
final-green.stderr identifica los casos y su resultado.

Casos reales: salida normal, límite virtual observado desde hijo, espera que
ignora SIGTERM y termina con -9, señal externa con causa NOT_DETERMINED,
truncado de salida y exclusión por instancia. Casos inyectados: fallos e
interrupciones de wait y creación. Todos los hijos de prueba se limpian; no se
simuló que esos casos fueran estados físicos D del kernel.

## Límites y siguiente unidad

El bloqueo es de una instancia viva, no durable ni global. Faltan diario,
reconciliación tras reinicio, adaptación QA, cuotas compartidas, admisión de
resultados y políticas de autoridad/incorporación. No es sandbox ni contención
de descendientes arbitrarios. Procesos/kernel no prometen respuesta en tiempo
real; RLIMIT_AS no reserva RAM ni garantiza ausencia de swap. El launcher puede
fallar antes de ejecutar el comando; su código de salida no acredita evaluación QA.

Revisor independiente: parcial por cuota agotada después de F1. Reconfirmación de
la corrección pendiente. El siguiente paso inmediato es RDD nativo del candidato
exacto; publicación solo tras cierre aprobado. No calibración del i3/WSL.
