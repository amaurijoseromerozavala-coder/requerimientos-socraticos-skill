# Registro real de interrogatorio — supervisor local

Interrogador: /root/supervisor_interrogator. Respondedor: /root. Humano decide política.

## 001

Q-SUP-001 | Destinatario: ASSISTANT_RESPONDER (/root) | Dimensión: contratos/dependencias | Estado: WAITING_ASSISTANT. ¿Qué evidencia existente define el contrato observable entre el supervisor y QA0.1.3 para distinguir una evaluación válida de una terminación sin stdout, en particular la precedencia entre código de salida (0/2/3), JSON disponible y cobertura parcial NOT_ASSESSED? Indica fuente y fragmento comprobable, o UNKNOWN donde el contrato no esté definido. No propongo una política nueva.


A-SUP-001: FACT: skills/qa-inquisidor/scripts/validate_report.py main retorna 0 tras validate_report y JSON, 2 para ValueError con document_validation INVALID y REJECT_INPUT, 3 para OSError/MemoryError/RecursionError con NOT_ASSESSED y evento/veredicto null. Todas las salidas JSON declaran execution_authorized false. observe_failure_declarations produce PARTIAL y NOT_ASSESSED si el prefijo de128 no contiene FAIL y hay más registros; es observación independiente, no veredicto. SKILL.md Resultado del proceso0.1.1: «Exit0 indica evaluación completada, no éxito del sistema» y «Un invocador debe registrar exit/señal/stdout/stderr y tratar ausencia de resultado como ejecución no acreditada». FACT de límite: no existe supervisor externo en este alpha. UNKNOWN: contrato externo exacto de validación de salida, precedencia frente a señal/JSON contradictorio, persistencia y escalada. PROPOSED: observación de terminación y protocolo íntegro prevalece para admisión del resultado; señal, timeout, salida faltante/inválida o incoherencia exit/JSON -> resultado no aceptado sin juicio semántico. PARTIAL nunca equivale a ausencia de fallos. Mantener autorización false independiente de todo resultado. Esto es propuesta para el PRD, no implementación ni decisión humana de alertas.


Contraste: INCOMPLETE. No cierra dimensión.

## 002

Q-SUP-002 | Destinatario ASSISTANT_RESPONDER (/root) | Dimensión fronteras/actores | Estado WAITING_ASSISTANT: ¿Qué instrucción humana o requisito existente determina si este supervisor local inicia QA0.1.3 y gobierna su proceso, o únicamente recibe evidencias de una ejecución iniciada por otro actor? Cita fuente literal y actor responsable de iniciar/terminar; si no está decidido, devuelve UNKNOWN para remitir esa frontera al HUMAN_OWNER. Esta distinción condiciona timeout, señales y atribución de ausencia de stdout.


A-SUP-002: UNKNOWN como decisión humana explícita. El humano pidió literalmente «Prepara el PRD» tras recomendación de supervisor local, manteniendo CI/producción fuera. Esa instrucción autoriza documentos, no ejecución ni resuelve quién inicia el checker. PROPOSED: supervisor como invocador local exclusivo del comprobador QA, con proceso hijo propio, plazo y salida acotados, sin comandos arbitrarios ni ensayos de aplicación. Alternativa: receptor de recibos; no controla el proceso ni puede inferir señal o ausencia de salida sin observador de confianza. La elección de frontera se escala al humano antes de canonicalizar requisitos de lanzamiento/parada.


Contraste: ESCALATE_USER. No cierra dimensión.

## Pregunta humana pendiente

Para el PRD, ¿el supervisor debe iniciar y controlar únicamente el comprobador QA local, o solo analizar resultados generados por otra herramienta? Esto define si podrá gestionar plazos, terminación y captura de salida. La decisión no autoriza implementación ni ejecución ahora.

Respuesta: pendiente.

## Respuesta humana a Q-HUMAN-SUP-001

Literal: «Ok Únicamente con el qa local».
Contexto: explicación de invocador local frente a receptor externo. Confirmada frontera del invocador local; no implementación ni presupuestos/alertas. La mención previa de respuesta pendiente es histórica.

## Q-SUP-003

Q-SUP-003 | Destinatario: ASSISTANT_RESPONDER (/root) | Dimensión: seguridad/fallos/recuperación | Estado: WAITING_ASSISTANT. ¿Qué evidencia y criterios técnicos delegados permiten especificar una finalización verificable del checker cuando vence el plazo o se alcanza el límite de salida, incluyendo limpieza del proceso y tratamiento del resultado si no puede confirmarse su terminación? Distingue capacidades demostradas, propuestas y UNKNOWN; necesitamos un falsador observable de cualquier afirmación «ejecución terminada».

A-SUP-003: EXTERNAL_FACT: receipts/python-subprocess.txt, documentación primaria Python: communicate puede almacenar salida en memoria; timeout de communicate no termina al hijo; returncode negativo -N indica señal en POSIX. Estos contratos no demuestran implementación del supervisor. FACT: checker0.1.3 no inicia procesos de aplicación según fuente actual; no existe supervisor QA implementado. PROPOSED dentro frontera confirmada: controlar solo el hijo propio con captura concurrente acotada y plazos monotónicos; al exceder límite, registrar motivo, solicitar parada, esperar plazo de limpieza acotado y observar terminación mediante API de espera del proceso. Solo resultado de wait/poll que confirma fin del hijo permite cleanup CONFIRMED. Enviar señal o vencer plazo no prueba fin. Si no hay confirmación, cleanup UNCONFIRMED, no aceptar evaluación, no reintento ni segunda ejecución automática; escalar la situación. Señal sin evidencia adicional: causa NOT_DETERMINED. Se conservan por separado bytes capturados/truncados y recepción completa; no aceptar JSON parcial. UNKNOWN: presupuestos numéricos, cobertura por SO, persistencia ante muerte del supervisor, procesos descendientes futuros. No prometer limpieza universal ni tiempo real. Falsador: ante un observador de proceso que nunca confirma terminación, recibo declara cleanup CONFIRMED o inicia un reemplazo; eso refuta la regla. Ensayo futuro con proceso controlado y límites, NOT_RUN hoy. Propuesta no exige ensayos físicos ni modificación del host.

Contraste independiente: ANSWERED como criterio de diseño, no capacidad demostrada.

## Q-SUP-004 pendiente

Q-SUP-004 | Destinatario: HUMAN_OWNER, mediante coordinador | Dimensión: datos/ciclo de vida | Estado: WAITING_USER. ¿Qué política debe tener el PRD para stdout/stderr del checker: mantenerlos solo durante la ejecución y guardar un recibo mínimo sin su contenido, o conservar además su contenido acotado en disco para diagnóstico? Recomiendo la primera como propuesta inicial; la segunda requiere que fijes cuánto tiempo conservarlo. No hay evidencia aportada que autorice escoger retención persistente de salida por delegación técnica.

Respuesta humana pendiente.

## Respuesta humana Q-SUP-004

Literal: «1». Opción1 descrita previamente: solo recibos mínimos; sin stdout/stderr completos; acceso propietario, máximo100recibos/1MiB; bloquear al llenarse, sin eliminación automática.

## Q-SUP-005

Q-SUP-005 | Destinatario ASSISTANT_RESPONDER | Dimensión contratos/dependencias | WAITING_ASSISTANT: ¿Qué artefacto concreto y verificación del candidato fijan ahora la admisión exhaustiva para cada salida real de QA0.1.3 (exit0/2/3 y failure_observation tipada), y demuestran rechazo de contradicciones, JSON truncado y campos no admitidos sin convertir PARTIAL/NOT_ASSESSED en ausencia de fallos? closure-proposal.json todavía declara pendiente el esquema; aporta rutas, correspondencia con el checker y resultados o UNKNOWN. Esta respuesta puede resolver la precedencia externa pendiente de Q-SUP-001 si cubre la misma dimensión.

A-SUP-005: FACT documental: checker-output.schema.json fija envoltorio observado returncode/payload con ramas estrictas0/2/3 y failure_observation tipada. protocol-contract.json fija decodificación completa UTF8 sin duplicados/no finitos/JSON truncado y predicados posteriores como contador<=filas; checker-binding.json conserva hashes de las cuatro dependencias fuente. verification/output-contract-results.json:12 controles PASS,5 salidas del checker actual con archivos sintéticos (normal, contradicción, entrada JSON inválida, OSError controlado y prefijo parcial),7 mutaciones rechazadas. Un esquema mutante permisivo acepta campo extra; contrato estricto lo rechaza. El esquema rechaza exit incompatible, veredicto incompatible, campos extra/ausentes, authorization true y PARTIAL presentado como ausencia. Límite: no prueba exhaustividad de toda ejecución real; reglas de transporte (bytes/UTF8/duplicados/profundidad) son requisitos futuros del adaptador, no implementados como supervisor. El checker no recibe versión de protocolo nueva: el adaptador fija versión0.1.3 por manifiesto, sin interpretar automáticamente cambios. Propuesta de precedencia externa en tabla-decision.json: fallo de ejecución observado -> INFRA_FAILURE; sin tal observación, salida incompleta/no admitida/incoherente -> PROTOCOL_FAILURE; protocolo coherente exit3 -> INFRA_FAILURE, exit2 -> REJECT_INPUT, exit0 -> EVALUATED_RECORD. EVALUATED_RECORD no es PASS; execution_authorized siempre false. Fuente de autoridad: correcciones explícitamente autorizadas por humano, no un hash por sí solo. Contrato documental cubre casos tipados; adaptación al SO y proceso sigue NOT_RUN.

Contraste real: ANSWERED para el contrato, no ejecución física.

## Q-SUP-006

Q-SUP-006 | Destinatario ASSISTANT_RESPONDER | Dimensión seguridad/fallos/recuperación | WAITING_ASSISTANT: ¿Qué contrato documental verificable resuelve la ventana de caída entre persistir RESERVED, crear el hijo y registrar PID+identidad de inicio, de modo que una recuperación nunca libere INFRA_LOCK con un hijo huérfano o un PID reutilizado? Explicita evidencia necesaria para desbloquear y qué ocurre cuando esa evidencia es irrecuperable, con casos de falsación y resultados documentales; el recibo mínimo y su eliminación humana no deben servir por sí solos de prueba de ausencia.

A-SUP-006: recovery-contract.json fija orden durable RESERVED antes de spawn, luego ACTIVE con run_id/boot/namespace/owner/PID/start identity y manifiestos. Diario separado de recibos; eliminar recibos no elimina diario. RESERVED sin identidad completa tras caída en mismo boot permanece INFRA_LOCK aunque quizá nunca se lanzó hijo. No se despeja por timeout, PID ausente, búsqueda por nombre ni reconocimiento humano. Fin observado por padre vivo sobre objeto hijo exacto permite confirmar; recuperación de ACTIVE requiere identidad completa y observación autorizada concluyente (no permission denied). Cambio de boot solo califica si se prueba mismo ámbito guest no restaurado; namespace/migración/snapshot ambiguos bloquean. Evidencia irrecuperable mantiene bloqueo indefinido local, sin reinicio automático ni disponibilidad garantizada. checker actual no crea descendientes de aplicación; cambio de ese contrato invalida adaptador. Casos documentados: caída antes RESERVED (spawn prohibido), después RESERVED/antes spawn y después spawn/antes ACTIVE (bloqueo conservador), después ACTIVE (identidad), después wait antes escritura (no reconstruir prueba perdida), borrado recibo (sin efecto en gate). Pruebas de ejecución siguen NOT_RUN. verification/model-results.json ya comprueba que no hay salida del lock sin reconciliación; no demuestra verdad de sus guardas. Falsadores de implementación precisos en recovery-contract.json. Esta respuesta especifica fallo seguro acotado, no elimina físicamente todas las ventanas de caída.

Contraste real: ANSWERED para el contrato, no ejecución física.

## Q-SUP-007

Q-SUP-007 | Destinatario ASSISTANT_RESPONDER | Dimensión calidad/recursos | WAITING_ASSISTANT. ¿Cuál es la secuencia temporal exacta que significan wall_deadline_seconds=30, cleanup_grace_seconds=2 y post_stop_observation_seconds=2: desde qué evento se mide cada plazo monotónico, qué transición provoca y qué significa excederlo durante creación no interrumpible? Fija si se suman y cuándo se declara INFRA_LOCK, sin prometer una cota real de 34 segundos ni convertir valores provisionales en mediciones. El artefacto actual enumera valores pero deja ambiguo el contrato temporal observable.

A-SUP-007: closure-proposal.json temporal_contract fija reloj monotónico. t0 inmediatamente antes de crear proceso, después de admisión y RESERVED durable; deadline t0+30 incluye creación, ejecución y captura. Creación que devuelve después: clasificar exceso y limpiar, no aceptar éxito tardío. Al primer plazo/límite de salida/cancelación comienza parada del hijo exacto, t_stop; gracia hasta t_stop+2. Fin confirmado: clasificar interrupción original. Si no termina, solicitar terminación forzada solo del hijo propio; t_force momento de esa solicitud, observación hasta t_force+2. Sin fin confirmado: INFRA_LOCK, sin lanzamiento nuevo. Identidad o resultado de creación desconocidos: INFRA_LOCK sin señalar PID arbitrario. Captura no reinicia reloj; límites tempranos comienzan parada antes de30. Los30+2+2 son presupuestos nominales, no cota física34s: creación, planificación y kernel pueden impedir observarlos a tiempo. Al recuperar control aplicar vencimientos, nunca éxito retrospectivo. Parámetros provisionales no medidos; falta de controles requeridos bloquea admisión. Ensayos temporales NOT_RUN; no garantía de progreso si el SO no responde.

Contraste real: ANSWERED para el contrato, no ejecución física.

## Q-SUP-008

Q-SUP-008 | Destinatario: ASSISTANT_RESPONDER (/root) | Dimensión: fronteras/actores | Estado: WAITING_ASSISTANT | Seguimiento de Q-SUP-002. ¿Qué respuesta humana registrada resuelve quién inicia y controla QA0.1.3, y cuál es exactamente la frontera confirmada? Cita el texto literal, el contexto de la opción presentada y la ruta del recibo para enlazar la resolución sin modificar la respuesta UNKNOWN ni la valoración histórica ESCALATE_USER de Q-SUP-002. Esta pregunta solicita evidencia de una decisión existente, no una política nueva.

A-SUP-008: USER_DECISION ya registrada: «Ok Únicamente con el qa local», recibo receipts/A-HUMAN-SUP-001.txt y contexto human-question.json. Respondió después de explicación que recomendó supervisor invocador que inicia/controla solo checker QA local frente a receptor de recibos externos. Frontera confirmada: inicia y supervisa únicamente comprobador local, no aplicación objetivo, comandos arbitrarios, CI ni producción. «Prepara el PRD» autoriza documentación, no implementación. Q002 UNKNOWN/ESCALATE se conserva histórico; esta fuente resuelve aquella dimensión.

Contraste real: ANSWERED; resuelve Q002 por fuente humana. Entrevista cerrada en cobertura documental condicionada; no demuestra implementación ni SO.

## Cambio humano posterior al RDD

El humano sustituye recibos mínimos por conservación de stdout/stderr. Plazo y borrado preguntados al humano; respuesta pendiente. La entrevista COMPLETE previa es histórica; cierre actual reabierto. No se atribuye fallo técnico probado a la política anterior.

## Resolución de retención

Humano corrigió «32 min» con «Mib» y «Mib corrigo»: capacidad32MiB, no plazo. A la pregunta de borrado respondió «Manual». Se adopta conservación de stdout/stderr local acotada, sin caducidad ni borrado automático; bloqueo por capacidad. Los topes de100ejecuciones y por flujo son límites técnicos conservadores. Historial anterior conservado, decisión mínima sustituida.
