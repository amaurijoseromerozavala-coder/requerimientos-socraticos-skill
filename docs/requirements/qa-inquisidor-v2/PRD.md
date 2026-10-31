# QA Inquisidor — continuación del PRD

Estado **DRAFT**, no instalado ni READY. Base histórica v1 conservada sin cambios.

Decisión humana vigente: **Solo análisis; ejecución con autorización específica**.
No se propone plazo predeterminado ni se ejecutan pruebas del sistema objetivo.
El alcance sigue siendo el sistema completo, con cobertura visible y límites;
no basta revisar el último cambio para afirmar evaluación integral.

Se mantienen ANALYSIS, TEST PLAN, VERIFICATION en español, vocabulario de
verificación de calidad y determinismo, respeto a normas OpenAI/terceros y
recursos autorizados. Ningún output QA impone mandatos al humano o al asistente.
Repetibilidad exige entradas/versiones/entorno fijados; no perfección universal.

## Avance real

Interrogatorio independiente inicial de cuatro dimensiones técnicas: oráculos de fase,
autoridad/recursos, evidencia/cierre y coherencia de FSM. Las preguntas, respuestas
literales y valoraciones se conservan en registro-skill-asistente.md/.json.
La decisión humana llegó durante Q2 y se preserva como actualización posterior.

Hallazgo material: DONE del modelo antiguo mezcla reporte terminado con evidencia
completa. Se propone REPORT_DELIVERED, separado de report_complete,
obligations_verified y verdict. Entregar un informe con pendientes no significa
PASS ni autoriza ejecutar. Las propuestas siguen PROPOSED, no implementación.

## Oráculos documentales propuestos

- ANALYSIS→TEST_PLAN: objetivo/snapshot, inventario y clasificación trazados.
- TEST_PLAN→VERIFICATION: autorización específica humana suficiente por caso,
  recursos observados y oráculo previo; no inferencia desde recomendación QA.
- Solo análisis→informe: casos de ejecución quedan NOT_RUN con motivo.
- REPORTABLE: documento completo en registros y limitaciones, aunque existan
  resultados INCONCLUSIVE/BLOCKED. PASS exige evidencia vigente por obligación.
- REPORT_DELIVERED: artefacto entregado, sin equivalencia con aprobación.

propuesta-prd.json fija delta R21-R28, guardas e invariantes propuestos. Ocho
casos negativos documentales quedan especificados, **NOT_RUN**: no se declara
prueba formal ni resultado de una skill todavía inexistente.

## Pendientes

G1-SPEC parcial: modelo finito compilado y analizado; falta contrato preciso de
entradas, correspondencia semántica y migración. AC-IMPL-GATES es aceptación
futura del runtime, pendiente de autorización, no condición circular del PRD. Migración canónica2.0 de PRD,
entrevista y propuestas pendiente; este addendum no pasa por PRD canónico completo.
No hay sistema de aplicación objetivo ni ensayo físico i3/WSL.

Investigación: skill/metodología y borrador leídos antes de modificar; MCP cloud
consultado y fuente primaria NASA Appendix C abierta para requisitos verificables.
No hay índice CodeGraph, se omitió según AGENTS.md. No se invocó Context7 ni Engram
como si estuvieran disponibles directamente en aquella fase; el espejo se actualizó
posteriormente según el recibo conservado en docs/skill-audit/qa-resume. No CI ni instalación ni producción.

## Análisis estático adicional del modelo documental

El interrogador recomendó separar G1-SPEC de AC-IMPL-GATES para no exigir el
producto implementado antes del PRD. Se compiló fsm-propuesta.json:59
configuraciones alcanzables,202 transiciones aceptadas y3574 rechazos. Control
negativo de guarda debilitada rechazado por evento de ejecución abstracto sin
autorización; modelo no modificado conserva los invariantes comprobados. Hay
trazas abstractas de entrega con PASS/FAIL/INCONCLUSIVE/BLOCKED. No se ejecutó
ninguna aplicación ni la futura skill; son cálculos sobre un documento finito.

Las ocho comprobaciones de contrato originales siguen NOT_RUN: esta enumeración
no sustituye sus oráculos de integración. Tampoco prueba liveness, descubrimiento
completo del sistema o verdad de los resúmenes externos que alimentan las guardas.
No se modifica ni se reabre la aprobación del addendum anterior: este análisis
es un candidato documental posterior que requiere su propia revisión.

## Continuación: correspondencia de evidencia

Q-QA-005 y su respuesta real constan en el registro. Véase contrato-evidencia-propuesto.md: éxito agregado exige todas las obligaciones materiales, sin pendientes ni éxito por conjunto vacío. Propuesta sin implementar; escenarios NOT_RUN y RDD nuevo pendiente. La valoración independiente mantiene G1-SPEC PARTIAL por tipos/correspondencia y autoridad semántica. Las aprobaciones anteriores no cubren estos cambios.

## Autorización posterior de ensayos

El humano autorizó ensayos locales; se conserva el default de la futura skill de análisis con ejecución específicamente autorizada. Evidencia y contraste en ../../skill-audit/qa-claims-followup/RESULTADO.md. No se acredita hardware físico, no se instala QA ni se acepta automáticamente el mandato del output QA. Autoridad semántica y migración siguen pendientes.
