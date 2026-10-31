> Política vigente: stdout/stderr acotados, 32 MiB compartidos, eliminación manual. Supersede la selección histórica de recibos mínimos.

# PRD — Supervisor local QA, candidato de cierre

**REVIEWING_DOCUMENTS; aún sin aprobación RDD final.** Solo especificación. No implementación, CI ni producción.

## Decisiones confirmadas

Supervisor invocador únicamente del checker QA local. Retención vigente: stdout/stderr acotados y recibos separados, acceso del propietario, máximo100ejecuciones y32MiB compartidos, eliminación manual y bloqueo cuando falta capacidad.

## Contratos normativos

- closure-proposal.json: recursos provisionales, captura, retención, canal local y cero reintentos automáticos.
- recovery-contract.json: orden durable, identidad más allá del PID y recuperación conservadora; pérdida de evidencia mantiene INFRA_LOCK. Eliminar recibos no desbloquea.
- checker-output.schema.json, protocol-contract.json y checker-binding.json: protocolo estricto ligado a versión/bytes, sin autoridad otorgada por hashes.
- fsm-propuesta.json y tabla-decision.json: modelo finito; no prueba de los mecanismos del SO ni progreso incondicional.

## Requisitos EARS

### SUP-001

El supervisor no deberá autorizar ejecución de aplicaciones, CI ni producción a partir de resultados del comprobador.

Falsador: Resultado favorable provoca ejecución de aplicación.

### SUP-002

Cuando termine una evaluación, el supervisor deberá conservar por separado terminación, admisión del protocolo, admisión documental y observación de declaraciones.

Falsador: Exit0 convierte una declaración no verificada en fallo confirmado.

### SUP-003

Cuando clasifique una ejecución, el supervisor deberá distinguir REJECT_INPUT, INFRA_FAILURE y PROTOCOL_FAILURE; ninguna clase autoriza ejecución ni establece automáticamente causa raíz.

Falsador: Un timeout se clasifica como documento inválido o una salida incoherente acredita evaluación.

### SUP-004

Si la exploración es parcial o no evaluada, el supervisor deberá conservar la incertidumbre sin concluir ausencia de fallos.

Falsador: PARTIAL con contador0 se transforma en comprobación completa.

### SUP-005

Cuando aparezcan declaraciones FAIL no verificadas, el supervisor deberá conservar su estado no verificado aun si el documento se rechaza.

Falsador: Se pierde la señal al registrar REJECT_INPUT.

### SUP-006

El supervisor deberá iniciar y controlar únicamente el comprobador QA local; se propone identificarlo de forma explícita, usar argumentos tipados y excluir shell y comandos arbitrarios.

Falsador: Un campo del reporte selecciona un ejecutable.

### SUP-007

Si no puede confirmar terminación del checker propio dentro del plazo de limpieza, el supervisor deberá entrar en INFRA_LOCK e impedir todo nuevo lanzamiento local hasta reconciliar la terminación del proceso correspondiente.

Falsador: Una segunda solicitud inicia otro checker sin confirmar terminación del anterior.

### SUP-008

Cuando observe una señal sin evidencia causal suficiente, el supervisor deberá conservar NOT_DETERMINED; podrá consultar diagnóstico del SO autorizado, acotado y correlacionado, sin elevar privilegios.

Falsador: Se atribuye OOM solo por -9/137, o un registro de otro proceso se acepta como causa.

### SUP-009

Si no puede persistir un recibo, el supervisor deberá declarar entrega no acreditada y no informar evidencia durable.

Falsador: Permiso denegado al escribir termina como registro persistido.

### SUP-010

Si cambia el candidato, la política, los datos o la versión de protocolo, el supervisor deberá invalidar la aplicabilidad de resultados anteriores.

Falsador: Se reutiliza resultado de otro snapshot.

### SUP-011

El supervisor deberá mantener separados el entorno local observado y el hardware objetivo declarado no medido.

Falsador: Un ensayo cloud se presenta como calibración del i3/WSL.

### SUP-012

Cuando una situación exceda los criterios delegados, el supervisor deberá devolver una decisión pendiente para el humano sin autoautorizar una excepción.

Falsador: Estado desconocido se convierte en permiso.

### SUP-013

Al iniciar o reiniciar el supervisor, si no puede reconciliar la existencia y terminación de ejecuciones anteriores bajo su control, deberá mantener INFRA_LOCK antes de admitir trabajo; un PID aislado o un reconocimiento humano no bastarán.

Falsador: Reiniciar el supervisor borra la incertidumbre y permite lanzar otro checker.

### SUP-014

Mientras registre una ejecución, el supervisor deberá conservar stdout/stderr acotados en archivos separados del recibo estructurado, con acceso exclusivo del propietario y eliminación únicamente manual.

Falsador: Se borra automáticamente una salida, se mezcla salida cruda con el recibo o se elimina el diario al limpiar salidas.

### SUP-015

Antes de lanzar un checker, el supervisor deberá reservar 335872 bytes y una plaza sin exceder 100 ejecuciones ni 33554432 bytes compartidos entre recibos, stdout/stderr y archivos parciales; si falta capacidad o contabilidad fiable, deberá bloquear nuevas ejecuciones sin borrar automáticamente.

Falsador: Con almacén lleno, reserva concurrente no contabilizada o archivos parciales ignorados se inicia un proceso o se borra una ejecución anterior.

### SUP-016

Mientras supervise el checker, deberá aplicar los presupuestos de closure-proposal.json y registrar límites prospectivos frente a aplicados; si faltan controles requeridos deberá rechazar admisión.

Falsador: El supervisor eleva su presupuesto automáticamente tras un timeout.

### SUP-017

Cuando lea la salida, deberá validar el esquema y reglas de protocol-contract.json antes de admitir una evaluación, manteniendo separados el código observado y el contenido declarado.

Falsador: Código declarado dentro del JSON reemplaza el código observado del proceso.

## Verificación y límites

Ensayos de implementación, caída de procesos y calibración i3/WSL: NOT_RUN. Los límites son decisiones conservadoras de diseño y no cuotas RSS ni garantía de éxito. El supervisor puede bloquear indefinidamente si no hay evidencia de terminación. No reinicia el host automáticamente.

Cierre exige contraste de entrevista, verificación documental y revisión independiente/nativa del candidato exacto. Recibos e historial en registro-skill-asistente.md y verification/.
