# QA Inquisidor 0.1.3-alpha

Implementado: failure_observation separado de admisión. Recupera etiquetas FAIL
de evidence[*].outcome tras decodificación acotada, máximo128 registros y sin I/O
adicional. Declaraciones no verificadas; no se añaden a failure_cases ni autorizan
acciones. JSON no interpretable: NOT_ASSESSED. Exploración incompleta sin etiquetas
no declara ausencia. Mantiene REJECT_INPUT e INFRA_FAILURE.

TDD:8 nuevos tests RED,9 errores contando subtests; suite62GREEN.
Revisión independiente:62tests y2 controles adicionales; sin nuevos hallazgos.
Logs: red.log, green.log, independent.log; revisión: independent.md.

Gentle AI4.2.0 RDD ON; candidato de riesgo medio,4archivos/149líneas:
sha256:aabfa52ad49dd986576f01d7d43eec90e283e553c8aba859e94e750b01683ebf.
Estado APPROVED_AND_ACKNOWLEDGED tras consentimiento humano explícito.
Resiliencia y fiabilidad: sin hallazgos en los cuatro parches. La revisión nativa
fue estática; no ejecutó pruebas. Las 62 pruebas locales y las 62 independientes,
más dos controles independientes, están documentadas por separado.
Dictamen: review-reliability.json. Acuse nativo: rdd-final.json.
CI diferido; producción no autorizada; sin calibración física.
