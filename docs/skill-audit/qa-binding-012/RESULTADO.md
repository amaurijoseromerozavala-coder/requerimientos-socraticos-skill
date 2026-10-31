# QA Inquisidor 0.1.2-alpha

Implementado: schema_version y limitations participan en inputs_digest; digest
anterior no vigente. Toda salida JSON declara authority_verification NOT_PERFORMED
y execution_authorized false. No autentica al emisor ni autoriza ejecución.
Documentación aclara compatibilidad y ausencia de garantía RSS/OOM.

TDD: cuatro pruebas nuevas RED (3 fallos, 1 error); 54 GREEN tras corregir.
Evidencia: red.log, green.log; revisión independiente en independent.md/log.

Gentle AI 4.2.0, RDD ON. Candidato nuevo de riesgo medio, 4 archivos/52 líneas:
sha256:fb1a85f35077a80bc46529458fee6d947fd78745abfd97a5c696c0eec2428b7e.
Estado nativo APPROVED_AND_ACKNOWLEDGED tras consentimiento humano «Granted».
Resiliencia y fiabilidad: sin hallazgos en los parches revisados. Revisión nativa
estática, sin ejecutar tests; ejecución independiente: 54 tests y dos controles
adicionales. Dictamen: review-reliability.json; acuse: rdd-final.json.
Sin CI, producción ni calibración física. No se agregaron firmas.
