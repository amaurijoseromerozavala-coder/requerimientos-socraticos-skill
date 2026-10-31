# Corrección documental R3-001

Estado: IMPLEMENTED_AND_TESTED_DOCUMENTARY_CHECKS; nuevo RDD nativo pendiente. No es implementación del supervisor.

## Cambio

El comprobador exige un único manejador global para revocation_accepted, prioridad BEFORE_LOCAL_TRANSITION, cobertura exacta de los nueve estados del alcance revisado y rechazo predeterminado. El oráculo fija el alcance independientemente de la FSM bajo prueba. Los efectos en prosa y el orden temporal no se ejecutan ni se certifican.

La importación no ejecuta verificaciones ni reescribe archivos. La CLI emite el resultado por stdout; ya no sobrescribe green.json histórico. Las 23 decisiones humanas y la FSM permanecen intactas.

## Evidencia

Antes de corregir: 19 fallos en la suite (mutaciones aceptadas, diagnóstico ajeno y efectos de importación). Después: 3 tests OK, incluyendo 18 controles negativos. El control negativo se acepta como prueba solo cuando falla con GLOBAL_REVOCATION_CONTRACT, no por un error ajeno. Las 128 valoraciones booleanas originales siguen verificadas.

Revisor independiente reprodujo los checks y no encontró hallazgos bloqueantes. Logs originales: red.stderr, green.stderr; salida del modelo: model-green.json. Interrogación real registrada en interview.json.

## Próximo incremento y restricciones

Completar contratos de la primera ejecución QA local: admisión y reserva durable, identidad del proceso, captura acotada, terminación/reconciliación, tipado de resultados y persistencia de recibos. La proyección de incorporación no sustituye esa FSM. Antes de un supervisor operativo se requiere contrastar su composición y las ventanas de recuperación; no se anuncia ya implementado.

Calibración i3/WSL: NOT_RUN. CI y producción no habilitados. No se modifican los recibos del candidato anterior ni se extiende su aprobación a esta corrección.
