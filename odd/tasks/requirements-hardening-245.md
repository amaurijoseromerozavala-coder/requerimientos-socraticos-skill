# Requerimientos socráticos 2.4.5 — activación y preflight

Mantenimiento autorizado del tooling local de la skill. No CI ni producción;
no medición ni réplica del PC físico, sin ensayos de saturación.

## Specs

S1. Usuario: «Entonces crea un módulo que al activar la skill escanee el hardware donde está hospedado lo identifique y corra un prefitgh para salvaguardar esos límites que falta comprobar y a partir de allí exponga límites para la ejecución de la skill».

S2. Criterios técnicos derivados de S1: sondeo local de solo lectura y tamaño
acotado; identificar características visibles sin identificadores personales.
Separar invitado/host desconocido, observación/política provisional y capacidad
no calibrada. No inferir rendimiento ni cobertura de la marca del procesador.

S3. Exponer preflight JSON y comandos activate/preflight en la extensión local
Gentle AI; ejecutar evaluación viva previa en entradas públicas de workers.
Seleccionar límite conservador de memoria compatible con límites existentes,
sin elevar hard heredado ni alterar caller API. Unknown crítico o perfil excesivo
bloquean workers; documentación sigue disponible. No aceptar informes editables
como autorización. Mantener admisión compartida y supervisión existentes.

S4. Mantener 0600, CI diferido, BLOCKED_GLOBAL_ENFORCEMENT, límites lógicos y
documentales. La activación del agente es contractual, no un hook universal del
LLM. El módulo no prueba temperatura, presión Windows ni capacidad física.
RED/GREEN, regresión, verificador independiente por cambio de guardas y revisión
nativa del candidato exacto, si disponible y con consentimiento exigible.

## Tasks

- T1 [S1,S2] inline: especificación y límites — DONE; sin commits autorizados.
- T2 [S1,S2,S3] delegado: módulo e integración pública con RED/GREEN — DONE;234tests finalGREEN independiente.
- T3 [S2,S3,S4] inline: contrato/activación/schema y documentación — DONE; schema validado en13casos y2comandosreales.
- T4 [S3,S4] delegado: verificación independiente de guardas — DONE;234tests/9casospropios ysinfallosconfirmadospendientes.
- T5 [S4] inline: RDD, informe y exportación — DONE; RDD aprobado/acknowledged, informe y exports actualizados.

## Log

L1.2026-10-28: «Entonces crea un módulo que al activar la skill escanee el hardware donde está hospedado lo identifique y corra un prefitgh para salvaguardar esos límites que falta comprobar y a partir de allí exponga límites para la ejecución de la skill».

L2. Perfil de activación propuesto conservador hasta512MiB, mínimo256, no
calibración. La selección depende de disponibilidad visible y límites heredados;
el gate de admisión vuelve a medir. Riesgo: item2 guardas y item3 contratos
compartidos; requiere verificador independiente. El código de producto no cambia.

L3. Primer candidato229testsGREEN (7nuevos). Verificador independiente reprodujo
RED propio: reporteREADY con hard128MiB y perfil512; reporteREADY con baseline
CLI100MiB y caller32MiB; argumentos0/520 producen traceback; etiquetaenforced
prospectiva. Se reabreT2 para comprobar límites porrol, baseline soloCLI, errores
JSON y distinción PENDING/aplicado. No se ejecutó estrés ni se aprobó este candidato.

L4. Correcciones verificadas independientemente en9casos propios pequeños:
hard128Git256/lógica bloqueada; hard384lógica432/solver378; baseline100own
bloqueado/APIexterno sinmutación; activateREADY→métricaUNKNOWN bloquea ambas
entradaspúblicas sinworker. Primerharnessdelrevisor asumía status obligatorio
en resultado lógico exitoso preexistente; se corrigióharness, no producto.
Regresión233tests con7fallos de fixturesOWNED: mock local de baseline no cubre
nuevo punto de observación del preflight. Repro determinista confirma rechazo
correcto65>64, no un fallo de contención. Se ajustan fixtures coherentes y campo
soft_unlimited desconocido para que UNKNOWN no se presente como ilimitado.

L5. Fix fixturesOWNED mantieneaserciones ypropagabaselinecoherente,19testsGREEN.
Fix tri-state UNKNOWN/soft_unlimitedNULL conREDprevio,8testsGREEN. Regresión
finalindependiente234tests7.747s; revisiónfinal/schema pendiente al instante de anotación.

L6. VerificadorcerróS1-S4favorableenalcancelocal:234tests,9casospropios,13schema/parser.
Padreejecutówrapperrealactivate y analyze secuenciales:JSONschemaPASS, perfil512;
PENDINGstandalone/APPLIEDintegrado. Son medicionescloud0.027/0.136s,noi3/WSL.
Evidenciaoriginal audit/requirements-hardening-245 copiada sinmodificara docs/skill-audit.
Validation.jsoncongeladoPRE_REVIEW; registroGentleAIactualizado. RDDpendiente.

L7.98archivos coincidenconárbol e01bc80fe4bee58c5ceec372423a7c1f34698fc2;
candidato sha256:43be837abe970455604de70e08c2c25a7dbf1cc2cff667c64b6f6aa42c2bcfec.
GentleAI4.2.0 globalRDDON devuelve consent_required:14archivos/1031líneas,
riesgoalto/4lentes. Consentimiento solicitadoalhumano víaUI, no inferido ni
aceptadoautomáticamente. Noautoridadcreada ni aprobaciónnativaatribuida.
PrimerSTATUSconlentesantesselecciónretornóinvalid_request; se conservó nota
yseacotóinventariosinlentes, selecciónreallentes4válida. No cambiomodoRDD.
JSON61fuentes yZIPverificados, móduloactivo cloud; físicodelPC sigueNOT_RUN.

L8.2026-10-28: usuario «Quiero rdd». Autoriza continuar la revisión del candidato
pendiente2.4.5;98fuentes verificadas sin cambios antes de aplicar la opción nativa
granted. No se modifica el modo global ni se extiende a otro candidato.

L9. RDD4lentes ejecutadasconcurrentementeenorden nativo;20.635s grupo.
Aprobado enúltimoevento, acknowledgementexactoadmitido/authorityburned.
Lineage review-f33ed053a4836d37, candidato sha256:43be837abe970455604de70e08c2c25a7dbf1cc2cff667c64b6f6aa42c2bcfec.
98archivos sin cambios después de acknowledgement. ObservaciónR2-001 no
bloqueante sobreduplicaciónproporcionesderecursos, mejora futura sin discrepancia
actual demostrada; noabre corrección. No se cambiaron fuentes ni rerun234tests.
Revisiónfuentes != ejecuciónindependiente. CI/PCfísico/global siguenbloqueados.
Validation.jsonconservado congelado, recibofinalexterno.
