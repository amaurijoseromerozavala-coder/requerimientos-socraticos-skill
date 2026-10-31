# Correcciones PRD supervisor — borrador 2

Alcance autorizado: documentos/modelos. Gentle AI requirements activate ejecutado;
RDD global ON. No implementación ni ensayos de procesos ni estrés físico.

- Frontera confirmada: invocador solo del comprobador QA local.
- INFRA_LOCK bloquea lanzamientos hasta confirmar terminación ligada a identidad
  y reconciliar admisión. Reinicio/reconocimiento humano no bastan.
- Rechazos tipados y prioridad de observación de ejecución, sin atribuir culpa.
- Diagnóstico SO opcional, autorizado/acotado, sin elevación ni OOM inferido.
- Revisión independiente detectó tres huecos FSM: lanzamiento fallido, recibos
  durante bloqueo y guarda de desbloqueo. Se corrigieron; véase independent.md.

Verificación:9 controles documentales (antes2 aprobados/7 fallidos, después9
aprobados),16 combinaciones abstractas; desde INFRA_LOCK ningún evento distinto
de reconciliación permite salir del bloqueo. No demuestra verdad de guardas,
persistencia durable, rendimiento ni ejecución del producto.

Entrevista y recibos: PASS_WITHIN_DECLARED_RECORD, WAITING_USER Q-SUP-004.
Pendientes: retención stdout/stderr, parámetros de recursos, protocolo exacto y
mecanismo durable de reconciliación. PRD no READY; RDD nativo del candidato final
no iniciado mientras esos requisitos materiales sigan abiertos.
