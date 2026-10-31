# Revisión independiente del candidato de cierre

Fecha: 2026-10-30. Estado: REVIEWED; observaciones cerradas documentalmente. Alcance documental; no READY ni aprobación nativa RDD. Informe separado de la revisión histórica draft-2.

## Verificación realizada

Se revisaron checker-output.schema.json, protocol-contract.json, checker-binding.json, recovery-contract.json, closure-proposal.json, prd-draft.json y fsm-propuesta.json. Se ejecutaron check-output-contract.py y check-document-model.py mediante el Python disponible con jsonschema instalado. Resultado: 12/12 casos de output y 9/9 aserciones documentales satisfactorias; el control negativo demuestra que el esquema permisivo admite el campo desconocido que rechaza el contrato estricto. El primer script llama helpers del checker con archivos sintéticos pequeños y un OSError simulado; no lanza un supervisor ni realiza ensayos de procesos/hardware. Reescribe output-contract-results.json como efecto previsto. Los cuatro digests de checker-binding.json coinciden con los archivos locales.

El esquema distingue las envolturas observadas exit0/2/3, no admite autorización de ejecución y conserva el carácter no verificado de las declaraciones. La validación requiere también los predicados del contrato: el esquema aislado no verifica relaciones entre contadores, unicidad de identificadores o subconjuntos. Los 12 casos no comprueban todas las reglas de decodificación UTF-8, claves duplicadas, profundidad y captura; implementación y pruebas de esas reglas siguen NOT_RUN.

Retención elegida: captura acotada solo en memoria, recibos mínimos sin texto libre ni logs SO, acceso del propietario, reserva de 8192 bytes y un puesto antes de lanzar, capacidad 100 recibos/1 MiB y sin borrado automático. La reserva resulta conservadora y no contradice los topes. El journal separado de 64 KiB no se borra al limpiar recibos; no hay desbloqueo por reconocimiento humano o mera eliminación de recibos.

La recuperación cubre expresamente la ventana RESERVED antes de identidad completa: queda bloqueada en el mismo arranque, incluso si no se llegó a crear un hijo. Evidencia de espera del hijo exacto, observación de identidad/ausencia concluyente o un arranque nuevo no restaurado se distinguen de PID aislado y errores de permisos. No se autoriza reiniciar el host. El contrato limita la confianza al supervisor cooperante y checker fijado; no promete exclusividad de toda la cuenta ni control de descendientes arbitrarios.

Los presupuestos son provisionales y no calibrados; ausencia de controles bloquea admisión. Los límites de tiempo no se presentan como garantía ante creación de procesos u operaciones no interrumpibles. Diagnóstico SO opcional, desactivado por defecto, con fuente autorizada, 1 s/64 KiB y sin privilegios adicionales.

## Observaciones notificadas

1. **Ciclo de solicitudes no expresado inicialmente.** DELIVERED, UNCONFIRMED y BLOCKED carecen de transiciones de solicitud fresca pese a la política que permite una solicitud nueva después de corregir/reconciliar condiciones. Con default de rechazo de eventos no especificados, una FSM literal no permite repetir la transacción. Se recomienda regresar explícitamente a RECONCILING, manteniendo el latch si sigue bloqueado. Es una omisión de disponibilidad/especificación, no prueba de lanzamiento inseguro.
2. **INCONCLUSIVE sin causa de incertidumbre admitido inicialmente.** Un payload exit0 con proposed_event=RECORD_GAP_OR_STALE/verdict=INCONCLUSIVE, required_obligations=[r1], sin gaps/failure_cases/gap_reasons, material_gap=false, all_success/delegation_current/scope_supported=true satisface esquema y predicados actuales. Se verificó la aceptación de ese ejemplo con jsonschema. Puede ser una política conservadora intencional, pero no expresa la coherencia exhaustiva del evento. Debe exigirse alguna condición de gap/stale o documentarse expresamente que la clasificación más conservadora se permite. No eleva un resultado a éxito ni autoriza ejecución.

## Revisión final de correcciones

Ambas observaciones quedan **RESUELTAS DOCUMENTALMENTE**. La FSM incorpora fresh_request desde DELIVERED/UNCONFIRMED/BLOCKED hacia RECONCILING, conserva journal/latch y exige petición explícita. Se verificaron estas tres aristas, determinismo por estado/evento y que INFRA_LOCK sigue sin salida distinta de termination_reconciled.

La rama GAP/INCONCLUSIVE exige ahora material_gap=true o alguna condición all_success/delegation_current/scope_supported=false. Se volvió a ejecutar check-output-contract.py con /home/agent/.local/share/requerimientos-socraticos/venv/bin/python: **13/13 PASS**, incluido gap_without_gap que rechaza el contraejemplo inicial; control negativo conservado. check-document-model.py volvió a dar **9/9 PASS**. Los resultados de 12 casos descritos arriba corresponden a la lectura inicial y quedan reemplazados por esta ejecución final de 13.

Se revisó temporal_contract: reloj monotónico; t0 anterior a creación tras RESERVED durable; plazo de 30 s que incluye intento de creación/captura; 2 s de gracia y 2 s de observación tras solicitud forzada; preservación del motivo original; identidad desconocida lleva a bloqueo sin apuntar a PID arbitrario. La suma nominal no garantiza 34 s de tiempo real, y recuperar control tras sobrepasar plazo no convierte salida tardía favorable en éxito. No se detectó contradicción con los presupuestos y la FSM abstracta.

## Límites

No se ejecutaron implementación del supervisor, señales reales, reinicios, cargas, ensayos de memoria ni diagnóstico del SO. La revisión no acredita recuperación durable, carreras, permisos reales o consumo físico. Las pruebas de crash windows siguen siendo requisitos de aceptación pendientes. Los checks verdes son evidencia de casos/modelo, no certificación semántica total. Revisión nativa RDD y cierre del interrogatorio corresponden al coordinador y no se simulan aquí.

## Instantánea final revisada (SHA-256)

- `checker-output.schema.json`: `3530bc8b7ea8bb3ec968f0c44cd9b23389d534383f1215e75e92de29a6ba8c6d`
- `protocol-contract.json`: `e51d73ff670989427f9e7cb73cfacde7da32d943aeff6658d17f43728cafdef0`
- `checker-binding.json`: `008a580be2695136c08c0d4881c5812593cd74f5fe94afc6138f579fcde18f10`
- `recovery-contract.json`: `b685e7f9185449bf103e8a60660ce43951262cdd8fdb031d890b368959b5ad48`
- `closure-proposal.json`: `b2cb65ac34b3f035d34bb2069dd0eb55c0454dc0e5bf12a3e6d3297c59246cf0`
- `prd-draft.json`: `f84e866ba2648690d881aaaba444f2ed599aba7d9e0ce98f26b320e0a3df0837`
- `fsm-propuesta.json`: `41af7c588bead037ac433dfbd4f69347cd7a9f400acc72826c3e6918f5249cba`
