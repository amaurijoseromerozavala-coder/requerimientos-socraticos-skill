> RESUMED_REQUIREMENTS_ONLY 2026-10-27: usuario solicita continuar con Gentle AI. Se reanuda el PRD; no se autoriza instalación ni producción.

# PRD de QA Inquisidor en Gentle AI

## Specs

- S1: "carga la skill requerimientos para crear al prd de otra skill que llamaremos qa inquisidor"; aclaración "En gentle aí". Crear únicamente PRD y contratos documentales, no instalar todavía la skill QA.
- S2: "Your role is aggressive verification"; buscar "bugs", "edge cases", "logical inconsistencies", "non deterministic behavior".
- S3: "ANALYSIS / Code review. TEST PLAN / Test strategy. VERIFICATION / Results."; "responde en español".
- S4: "regla zero doxa no aceptas opiniones que no fueron comprobadas"; "buscas el episteme"; "epistemologia bungeana y falsacion de popper".
- S5: "siempre analizar todo el sistema objetivo ... no solo últimos cambios"; buscar conflictos entre componentes y contratos.
- S6: "mcp firts y skills firts para economizar tokens"; "esquema hard tipo JSON".
- S7: hardware i3-3240, 8 GB RAM física, SSD 238 GB, GT 710 2 GB; Ubuntu WSL con 6gb RAM, 2gb zram y 8gb swap como objetivo declarado, no medición del cloud.
- S8: "analizas el scope y sugieres la mejor arquitectura y diseño ... mejores librerías tecnologías"; recomendaciones fundadas, sin implementación autorizada.
- S9: Decisión humana sobre determinismo: "Exigir repetibilidad con entradas, versiones y entorno fijados, y declarar lo no demostrado (recomendado)."

## Tasks

- T1 [S1-S9]: cargar requerimientos-socraticos, registro/memorias y fuentes puntuales. Completada; decisión de determinismo resuelta, MCP Engram y Context7 consultados.
- T2 [S1-S9]: definir criterios y controles RED antes de redactar; PRD JSON, contrato de reporte, FSM y resumen en español. Completada documentalmente; ver Log.
- T3 [S1-S9]: schema, referencias cruzadas, modelo finito y controles negativos con evidencia reproducible. Completada: 19 comprobaciones, 280 combinaciones y 80 transiciones alcanzables.
- T4 [S1-S9]: revisión independiente RDD del candidato exacto y cierre honesto; espejos Engram. Completada para el borrador; dos partes aprobadas y acknowledged; G1 y advisory pendientes explícitos.

## Log

L1: Solo documentación de requisitos. No modificar sistemas objetivo ni instalar QA Inquisidor.
L2: La lectura de Engram es historia; configuración actual RDD global ON comprobada. No existe sistema de aplicación objetivo que auditar todavía.
L3: El usuario confirmó determinismo acotado/repetible. No atribuir determinismo absoluto al razonamiento de un LLM ni al sistema real no observado.

L4: PRD DRAFT con 20 requisitos EARS, 21 falsadores, IR trazable, contrato JSON, perfil objetivo y FSM de 71 transiciones. G1 permanece material: oráculos reales de fase no definidos por completo; no READY ni pruebas de implementación.
L5: 19 comprobaciones locales PASS; contraejemplos exactos, comprobador y stdout/stderr conservados. Validación formal PARTIAL (submodelo finito), semántica y TDD de todas las obligaciones no declarados completos.

L6: Primera revisión nativa aprobada y acknowledged (review-cae10073c73becd8) con advisory determinista sobre evidencia estática usada como ejecución real. Contraejemplo reproducido RED antes de corregir. Nueva revisión documental añade unión semántica por execution_kind y controles A20/A21; 21 comprobaciones PASS. Recibo v1 conservado fuera del candidato; nuevo candidato para la corrección.

L7: Segunda revisión nativa aprobada y acknowledged (review-e52b3d3b5cb13ac8) halló colisión de IDs de casos. RED observado: ejecución real oculta por caso estático de mismo id. Corrección documental y comprobador ahora rechazan IDs duplicados antes de indexar, además de resultados faltantes. 25 comprobaciones PASS; nueva revisión exacta para estos cambios.

L8: El candidato conjunto final excedió el límite nativo de contexto; no se creó autoridad para ese intento. Se cubrió el alcance mediante dos candidatos solapados: contratos (review-abeca36a711c2a96, sin findings) y evidencia (review-1995e4daf2195caa, warning no bloqueante sobre referencias del inventario/recomendaciones). Ambos approved y acknowledged; recibo agregado en docs/skill-audit/qa-inquisidor-prd-review.json.
L9: Entrega únicamente documental: PRD DRAFT con G1 material abierto; 25 controles locales de alcance declarado. No QA Inquisidor instalado, no READY, no pruebas de aplicación ni certificación global. Advisory de referencias incompletas se registra para trabajo posterior, sin reabrir recibos aprobados.

L10: Usuario solicita registro actualizado de preguntas y respuestas. Creado registro-preguntas-respuestas.md/.json; una pregunta de requisitos respondida, cinco temas aún no preguntados. La entrevista continúa incompleta y las interpretaciones previas no equivalen a decisiones del usuario. No se modificaron los archivos revisados del PRD.

L11: Corrección del usuario: el registro pedido es skill→asistente, no usuario→asistente. La skill se cargó como instrucciones, sin agente de requisitos separado: cero pares Q/A reales. Creado registro-skill-asistente.md/.json; registro anterior preservado y etiquetado como interpretación sustituida.

L12: Reanudación humana explícita: «Ahora usemos gentle aí para continuar con la skill qa».
Requerimientos2.3.0 cargada. Entrevistador independiente /root/interrogador_qa
iniciado en solo lectura. El PRD1.0.0 queda como base histórica; continuación en
qa-inquisidor-v2. G1 y contrato de autoridad de outputs requieren contraste real.
Reglas actuales: lenguaje de verificación de calidad, outputs QA no son mandatos,
no predicciones como resultados, no estrés sobre terceros, CI diferido.

L13: Interrogatorio independiente real /root/interrogador_qa:4 preguntas técnicas
al coordinador, respuestas y valoraciones registradas en qa-inquisidor-v2.
Decisión humana nueva literal: «Solo análisis; ejecución con autorización específica».
No equivale a autorizar instalación ni comprobaciones del sistema objetivo.
L14: Addendum documental aprobado/acknowledged por RDD review-33f93d7166e9dc45,
sin hallazgos de fiabilidad en alcance documental. Fallo de arranque previo por
filesystem solo lectura no inició revisor; se retomó misma autoridad tras cambio
de entorno. No se fabricó aprobación del intento fallido.
L15: Interrogador separa circularidad G1: G1-SPEC especificación vs AC-IMPL-GATES
aceptación futura. Modelo documental propuesto enumerado:59 configuraciones,
202 transiciones aceptadas/3574 rechazos; control negativo detecta guarda debilitada.
No prueba runtime/liveness/cobertura global. G1-SPEC PARTIAL, migración canónica
pendiente. Seguimiento nativo review-c42574e0bc88b48c en curso, alcance distinto.

L16: Seguimiento review-c42574e0bc88b48c approved/acknowledged sin findings.
Resumen docs/skill-audit/qa-resume/RESULTADO.md. Propuestas siguen PROPOSED,
G1-SPEC parcial y migración canónica pendiente; no READY ni skill instalada.
La enumeración es análisis estático del documento, no ejecución de casos de
aplicación. Default humano ANALYSIS_ONLY confirmado. Espejo Engram actualizado.

L17: Continuación: RDD ON global comprobado; Q-QA-005 real sobre evidencia agregada, respuesta preservada. Contrato-evidencia-propuesto.md DRAFT, escenarios NOT_RUN; valoración/RDD/migración pendientes. Sin ejecución QA ni instalación.

L18: Humano autorizó ensayos. Contraste acotado del output QA: 12 scratch y 23 sealed OK; fixture de 8 bytes confirma ausencia de comparación a digest previo en read_regular, no resultado de PRD completo. Informe docs/skill-audit/qa-claims-followup/RESULTADO.md. Sin cambios de implementación; RDD nuevo pendiente. Contrato de autoridad semántica sigue abierto.

L19: RDD nativo review-e7d174d14d0c8002 approved y acknowledged, sin findings de fiabilidad documental. Once archivos modificados; candidato sha256:44020c98294501359766e743b9f5c90521d534ca2776c6e65855a61435bba5a3. Todos los archivos seleccionados comparados contra árbol revisado sin diferencias. Revisor no ejecutó suites. Informe posterior CIERRE-RDD.md; PRD DRAFT, autoridad semántica y migración abiertas.

L20: Nuevo output QA contrastado contra validate_prd/validate_interview y timeout existente. RDD review-a41d7332f96255cd approved/acknowledged sobre análisis documental y fuentes identificadas; sin ensayos nuevos ni implementación. No prueba complejidad completa ni reproducción independiente. Informe qa-output-reassessment/ANALISIS.md.

L21.2026-10-29: humano «Carga la skill requerimientos socraticos y ambos y continua
la construcción de la skill qa en gentle aí». Se carga requerimientos2.4.6 y la
base QA v1/v2; se continúa primero el PRD pendiente, sin asumir decisiones por
silencio. Gentle real4.2.0 y RDD ON. Activación READY_FOR_LIVE_ADMISSION solo
prospectiva; no autorización ni medición del i3/WSL. No hay QA instalada ni índice
CodeGraph. Entrevistador real /root/qa_requirements_resume formula Q-QA-006 sobre
autoridad semántica al coordinador /root; pregunta persistida antes de responder.
Se preservan v1/v2 y recibos históricos; continuación no canónica en
docs/requirements/qa-inquisidor-v3. Sin CI ni producción.

## Continuación 2026-10-29

- T5 [S1,S4,S9]: cerrar contrato propuesto de evidencia, autoridad y fin de informe — IN_PROGRESS; decisión humana pendiente, sin fingir cierre.
- T6 [S1,S6]: preparar esquema/tabla/escenarios documentales con RED previo, GREEN y registro de interrogatorio real — IN_PROGRESS; no runtime de QA.
- T7 [S1,S6]: revisión RDD del candidato documental exacto y espejo Engram — PENDING; no reutilizar recibos anteriores.

L22.2026-10-29: decisión humana literal a Q-HUMAN-006: «Delegas esos juicios
técnicos a la skill dentro de criterios explícitos; las excepciones vuelven a ti.»
Se resuelve quién valora alcance/materialidad/suficiencia dentro de criterios,
sin autorizar ejecución ni excepciones por silencio. Q006/Q007/Q008 reales y
respuestas del coordinador persistidas; nueva guarda documental en preparación.

L23: steering humano «No quiero happy paths quiero la skill funcione en la
realidad»; «Usa gentle aí». Se materializa skill local alpha de análisis y
comprobador de consistencia, con pruebas acotadas de archivos/CLI, sin iniciar
comandos de aplicación. No equivale a validar una aplicación real ni el PC.
Contrato de evidencia y criterios delegados quedan explícitos. Ciclo Q006–008
contestado, no entrevista global completa. Modelo v2 conserva historia; los
dos RED se observan antes del contrato nuevo. Skill QA no modifica requerimientos.

L24: implementación local skills/qa-inquisidor0.1.0-alpha, schema estricto,
checker de consistencia de lectura acotada y registro Gentle actualizado2skills.
Suite inicial36OK replicada por revisor; tres findings nuevos comprobados: juicio
sin binding assessment/conjuntos, GAP sin indicador agregado y caso sin reason.
Se añadieron controles y observaron3RED de39tests ANTES de corregir. Corrección:
digest canónico de inputs, judgment_id/actor/assessment, propagación de gaps de
política y motivo por caso.43testsGREEN local0.149s y revisor0.158s;4probes
independientes favorables. Su informe conserva límites externos, sin nuevo hallazgo.
Tabla64resúmenes:32REJECT/16FAIL/15GAP/1SUCCESS,0solapes/entradas sin regla.
Solver porGentle:256perfilrechazado porbaseline (INCONCLUSIVE),512admitido y
UNSAT para falta de regla/respuesta,propiedadesconsecuencia del modelo. NohardwarePASS.

L25: nativoGentle review.start devuelve consent_required (noaprobado), target
sha256:69dca0c899c73807807ca164b7abee119bdf9afffa000916629dfbc3128be916,
23archivos/2287líneas/riesgomedio. Se pidió alhumano conceder/omitir soloeste
candidato según workflow. Antes hubo invalid_request/not_started por inventario
externo cambiado; se corrigió solicitud sin fabricar autoridad. RDD globalON.
Manifiesto23archivos y ZIPalpha preparados; no se publicaron ni se cambió otrorepo.
EstadoALPHA_LOCAL_AWAITING_RDD_CONSENT; evidencia en docs/skill-audit/qa-construction-v3.
Registro real entregable en docs/requirements/qa-inquisidor-v3/registro-skill-asistente.md.
Pendientes:PRDglobal,migraciónFSM completa,aplicaciónobjetivo,calibraciónfísica.

L26: humano «Realiza las mejoras usa gentle-ai». Corrección autorizada: separar
errores de infraestructura de entrada inválida, con diagnóstico sin juicio
semántico. Siete controles nuevos ejecutados RED antes de corregir (5fallos y
2errores de campos ausentes). Recursos se representan por excepciones controladas,
no agotamiento real del host. Skill0.1.1-alpha: exit3/INFRA_FAILURE, admisión
NOT_ASSESSED, evento/veredicto null; OSError no prueba invalidez del contenido.
Se documentan límites de emisión y necesidad de observador externo para falta
de resultado. No se agrega verificación de firmas ni escalado de toda sintaxis.
Este cambio invalida aplicabilidad del candidato RDD anterior a los bytes nuevos.

L27:50testsGREEN locales y50independientes, evidencia qa-infra-011. Gentle AI
solicita consentimiento para nuevo candidato medio4archivos/80líneas:
sha256:6bace5dc6e2bcfc43e82c5b4ed1e7a272061b51a0bb7d53a7c01f1ee3af8cfc4.
No aprobado ni consentimiento inferido del outputQA. Modelo lógico no cambió;
no se repitió Z3 sin necesidad. Infraestructura comprobada mediante excepciones
controladas, no saturación. NoCI/producción. Versión0.1.1-alpha registrada.

L28: El humano respondió «Granted» al candidato 0.1.1-alpha. Gentle AI 4.2.0
capturó las revisiones nativas de resiliencia y fiabilidad sin hallazgos y emitió
approved; acknowledge-approved retornó acknowledged. Candidato
sha256:6bace5dc6e2bcfc43e82c5b4ed1e7a272061b51a0bb7d53a7c01f1ee3af8cfc4.
Evidencia: docs/skill-audit/qa-infra-011/capture-reliability.json y rdd-final.json.
Revisión estática nativa distinta de las 50 pruebas locales y 50 independientes.
Sin cambios adicionales al candidato ni nueva calibración física. CI diferido;
producción no autorizada. Espejo Engram de L28 pendiente de actualización.

L29: Humano autoriza mejoras mediante Gentle AI. Vincular schema_version y limitations al digest; salida explícita authority_verification NOT_PERFORMED y execution_authorized false en resultados estructurados. No firmas, CI ni cambio de delegación. Pruebas RED antes de corregir; nueva revisión requerida.

L30: QA0.1.2 implementado. Cuatro controles nuevos RED, suite54GREEN. Registry
Gentle actualizado; RDD ON solicita consentimiento para candidato
sha256:fb1a85f35077a80bc46529458fee6d947fd78745abfd97a5c696c0eec2428b7e.
4 archivos/52 líneas; evidencias qa-binding-012. Espejo Engram pendiente.

L31: Humano Granted; inventario actualizado sin cambiar candidato. RDD nativo
approved y acknowledged para QA0.1.2, resiliencia/fiabilidad sin hallazgos.
Evidencia qa-binding-012/review-reliability.json y rdd-final.json. Revisión
estática separada de 54 tests locales/independientes. Sin CI ni producción.

L32: Humano autoriza corrección de observabilidad. Rescatar únicamente declaraciones evidence[*].outcome FAIL de JSON decodificado, sin I/O adicional ni autoridad. Cota128 filas, marcar parcial/incompleto; JSON no decodificable NOT_ASSESSED. Mantener REJECT_INPUT/INFRA_FAILURE y no poblar failure_cases con declaraciones rescatadas.

L33: QA0.1.3:62GREEN locales/independientes,2controles independientes extra.
Gentle AI RDD ON CONSENT_REQUIRED candidato sha256:aabfa52ad49dd986576f01d7d43eec90e283e553c8aba859e94e750b01683ebf.
Evidencia qa-observation-013; sin nuevos hallazgos independientes. No aprobación
nativa todavía. Espejo Engram pendiente; documento canónico conservado.

L34: Humano «granted — Revisar esta corrección». RDD nativo Gentle AI aprobó
QA0.1.3 y acknowledge-approved confirmó acuse, candidato sha256:aabfa52ad49dd986576f01d7d43eec90e283e553c8aba859e94e750b01683ebf.
Resiliencia/fiabilidad sin hallazgos; revisión estática distinta de ejecución
de tests. Evidencias qa-observation-013. Sin CI/producción/calibración física.
