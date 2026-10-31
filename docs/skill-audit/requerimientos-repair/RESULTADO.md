# Reparación de requerimientos-socraticos — resultado

Versión instalada: **2.0.1**. QA Inquisidor: **PAUSED_BY_USER**, 19 archivos sin cambios.

## Fallos corregidos

- Rol explícito de arquitecto y científico del software senior, con perfil Codex de solo lectura.
- Interrogatorio real: pregunta → respuesta → contraste → siguiente gap; cierre por cobertura, no por cantidad de preguntas.
- Registro separado de entrevistador, asistente respondedor y humano decisor; no diálogo ficticio ni decisiones inventadas.
- MCP y skills pertinentes primero, exploración web primaria y propuestas con alternativas, criterios, tradeoffs y falsadores.
- Gates documentales: preguntas/respuestas pendientes, fuentes inexistentes, duplicados, recibos alterados, exclusiones de alcance sin autoridad y versiones ajenas impiden cierre válido.
- Coherencia de aplicabilidad, misma dimensión en seguimientos y enlace de requisitos/topics del mismo proyecto.
- PRD v1 conserva lectura como borrador; no puede usar READY sin la entrevista v2. No se migró ningún PRD QA pausado.

## Evidencia

- 43 pruebas locales aprobadas: `tests-green.stderr`.
- Interrogatorio real con dos preguntas: `smoke/registro-skill-asistente.md` y `smoke/interview.json`.
- Propuesta emitida por el arquitecto: `smoke/propuestas-arquitecto.md`. Es EVIDENCE_PENDING, no una decisión humana ni un cambio aplicado.
- RDD nativo: `rdd-final-receipt.json`; paquete completo aprobado tras corrección acotada y ajuste posterior aprobado sin findings.
- QA íntegro: `qa-integrity-final.json`.

## Límites

La prueba real es acotada a la reparación; no se presenta como interrogatorio de QA ni garantía de obediencia universal de un LLM. Los validadores comprueban registros declarados, coherencia y recibos, no autentican de forma independiente toda afirmación humana ni prueban semántica natural universal. Los fixtures con metadatos RDD sintéticos son únicamente controles de tests.

El proceso fallido de propuestas durante el reinicio del entorno quedó registrado con un solo reintento; no se citó como resultado hasta obtener el artefacto real. Las preguntas/respuestas anteriores y su observación histórica de 34 pruebas no se reescribieron: el conjunto final aumentó después a 43.

`skills/requerimientos-socraticos/validation.json` es la evidencia congelada antes de revisión; el recibo externo contiene su estado RDD posterior. No se alteraron archivos revisados para insertar su propio recibo.
