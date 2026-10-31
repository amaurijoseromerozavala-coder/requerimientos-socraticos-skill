# Revisión documental independiente — supervisor QA

Fecha: 2026-10-29. Alcance: PRD draft-2, FSM propuesta y tabla de decisión. Revisor independiente delegado; sin aprobación nativa RDD. Estado: **REVIEWED / DRAFT**, cuatro hallazgos corregidos documentalmente. No READY.

## Evidencia y comprobaciones

Se leyeron los cuatro artefactos, AGENTS.md y las pautas de cumplimiento aplicables. Se ejecutó únicamente un programa Python pequeño sobre JSON: sintaxis válida; 13 identificadores de requisitos únicos; cobertura de las 16 combinaciones abstractas sin duplicados; clasificación conforme a la precedencia declarada; autorización falsa en todas las filas; referencias de estados válidas y transiciones deterministas por par estado/evento; inicio en RECONCILING; única salida nominal del estado INFRA_LOCK mediante termination_reconciled. Resultado: PASS documental para esas propiedades enumeradas, no validación semántica integral ni ejecución del supervisor.

La tabla distingue REJECT_INPUT, INFRA_FAILURE y PROTOCOL_FAILURE. Un fallo de ejecución observado prevalece sobre cualquier payload. Sin fallo observado, un payload incoherente conduce a PROTOCOL_FAILURE; exit3 coherente conduce a INFRA_FAILURE. La combinación OTHER/coherent=true es una combinación abstracta conservadora, no prueba de que exista un código desconocido válido en el protocolo.

SUP-007 y SUP-013, el contrato cleanup_contract y la condición inicial de FSM expresan el bloqueo ante terminación desconocida, incluidos reinicios. El reconocimiento humano no desbloquea. No se encontró autorización de aplicaciones, CI o producción. El diagnóstico SO queda opcional, autorizado, acotado y sin elevación; los registros brutos no se persisten mientras siga abierta la política de retención. No se atribuye OOM a una señal aislada.

## Hallazgos concretos

1. **FSM incompleta para fallo de lanzamiento.** El PRD incluye launch error en INFRA_FAILURE, pero la FSM pasa de ADMISSION a RUNNING con admitted y desde RUNNING solo admite exit_observed o limit_or_cancel. Si la creación del proceso falla y no hay proceso que termine, no existe evento que clasifique ese error. La regla por defecto conserva el estado y rechaza el evento. Propuesta: explicitar launch_failed hacia CLASSIFYING, con limpieza no aplicable y sin afirmar que se lanzó un proceso.
2. **Recibos durante bloqueo descritos, pero no modelados.** Los invariantes permiten generación/notificación mientras el latch INFRA_LOCK permanece activo; las transiciones de INFRA_LOCK solo permiten bucles o salida tras termination_reconciled. Con terminación todavía desconocida no hay ruta de persistencia/entrega. La nota orthogonal_gate expresa la intención pero no define el producto de estados ni los eventos de la dimensión de recibo. Propuesta: modelar explícitamente estado transaccional y latch independiente, o declarar la FSM parcial y añadir transiciones/acciones de recibo que conserven el latch.
3. **Guarda de reconciliación menos completa en FSM que en PRD.** cleanup_contract.unlock_guard exige terminación ligada a identidad y reconciliación satisfactoria de admisión. La guarda termination_reconciled solo menciona la primera. El destino CLASSIFYING no prueba que se haya reconciliado la admisión. La guarda admitted sí impide iniciar con ejecuciones pendientes, por lo que no se demuestra un lanzamiento inseguro; queda sin formalizar cuándo se libera el latch. Propuesta: exigir ambas condiciones o mantener expresamente el latch hasta una reconciliación posterior.
4. **Lógica SUP-003 abreviada.** Su campo logic no incluye exit3 coherente ni el resultado EVALUATED_RECORD, aunque sí aparecen definidos correctamente en result_contract y tabla. No cambia la intención en prosa, pero impide tratar esa fórmula aislada como clasificador total. Propuesta: remitir expresamente a la tabla exhaustiva o completar la expresión.

## Revisión de correcciones

Los hallazgos originales 1–3 quedan **RESUELTOS DOCUMENTALMENTE** tras releer la FSM corregida y ejecutar comprobaciones pequeñas adicionales:

- launch_failed_no_child lleva RUNNING a CLASSIFYING solo con ausencia acreditada de hijo; launch_outcome_unknown lleva a INFRA_LOCK. RUNNING ahora incluye el intento de lanzamiento.
- record_created, write_confirmed y write_failed tienen bucles explícitos en INFRA_LOCK; actualizan el recibo conservando el bloqueo de admisión.
- termination_reconciled exige terminación ligada a identidad **y** reconciliación completa de admisión.

Estas transiciones existen, conservan determinismo por estado/evento y mantienen el bloqueo en los tres eventos de recibo comprobados. PASS para estas propiedades documentales. La observación 4 queda también **RESUELTA DOCUMENTALMENTE**: SUP-003.logic ahora incluye exit3 coherente, exit0 coherente y fallback de protocolo, en el orden de precedencia de la tabla. No se demuestra recuperación o persistencia reales.

## Límites y decisiones abiertas

No se ejecutaron procesos de producto, pruebas de carga, diagnóstico SO, señales, reinicios ni ensayos sobre hardware. Comportamiento real de limpieza, persistencia, identidad, recuperación, consumo y compatibilidad: NOT_RUN. Tampoco se garantiza control del kernel/host ni entrega si muere el supervisor.

No se cerraron retención, presupuestos, esquema/versionado de salida, identidad durable ni política de urgencia. La tabla prueba cobertura solo del dominio booleano/exit_class elegido; no acredita que cada observación real pueda traducirse correctamente a esos predicados. La seguridad de reinicio depende de un mecanismo pendiente, y los efectos del latch deberán concretarse en un diseño posterior. No se concede aprobación RDD ni permiso de implementación.

## Instantánea final revisada (SHA-256)

- `prd-draft.json`: `7b191143181ce85bd4bc31aa5ccb79b0591333d0536d878405a52d94f45a6511`
- `PRD.md`: `c3e42a99a354b9ab18e49b85f85831c2b1d09969af79c9189f23132cfa8649bc`
- `fsm-propuesta.json`: `751bc3b89ff31448794f59b1782ace04669a771ebeab0b1f2f899fae0ab9ca92`
- `tabla-decision.json`: `0cab1f33310d73e292b19b20327d2e08de6163e1057016307921e87a8d169584`
