# Interrogatorio real: reparación de requerimientos-socraticos

Solo prueba de la reparación. QA Inquisidor permanece PAUSED. Preguntas y respuestas literales; sin razonamiento interno ni diálogo reconstruido.

## Q1 — arquitecto interrogador → asistente

ASSISTANT_RESPONDER: What recorded before-and-after evidence supports that the paused QA Inquisidor artifacts stayed unchanged during the skill repair, including which artifacts were compared and when? Cite existing records; report UNKNOWN for missing evidence without accessing the paused task.

**Respuesta literal del asistente:**

La evidencia es una comparación SHA-256 de solo lectura de 19 archivos del directorio docs/requirements/qa-inquisidor. El inventario y hashes iniciales están en qa-paused.json, registrados al pausar (20261026T165542Z). La comparación posterior está en qa-integrity-after.json (2026-10-26T17:11:50.119230+00:00); todos los hashes coinciden y el resultado es IDENTICAL. Ambos registros enumeran los archivos comparados. La lectura se limitó a verificar integridad: no modifiqué, migré ni avancé esos requisitos. Esto prueba igualdad de contenido de los archivos enumerados entre ambas observaciones, no ausencia de cualquier evento intermedio ni archivos fuera de ese inventario.

## Q2 — arquitecto interrogador → asistente

ASSISTANT_RESPONDER: ¿Qué evidencia existente demuestra que el paso a READY se rechaza cuando el registro de interrogación está incompleto o sin contrastar? Cita la condición de validación y resultados reales de pruebas negativas que vinculen el registro evaluado con el rechazo; declara UNKNOWN donde falte evidencia.

**Respuesta literal del asistente:**

La condición observable está en scripts/validate_prd.py: después de verificar hashes y ejecutar validate(interview) y validate_design(), un PRD declarado READY exige entrevista COMPLETE y diseño REVIEWED; si no, emite INTERROGATION_INCOMPLETE y exit 1. El schema además rechaza READY v1 sin entrevista. La ejecución de tests/test_interview.py quedó en tests-green.stderr: 34 pruebas OK, incluidas test_cli_rejects_ready_with_paused_interview (PRD v2 sintético, entrevista PAUSED, rechazo exacto por CLI) y test_cli_complete_record_is_positive_integrity_control (mismos contratos, entrevista COMPLETE, aceptación de integridad). También rechazan una sola respuesta con otra dimensión abierta, preguntas sin respuesta, UNKNOWN aceptado como hecho y respuestas sin contraste. Estas pruebas demuestran gates documentales del validador y su oráculo específico; los metadatos RDD sintéticos de los fixtures no son recibos reales. No demuestran que cualquier LLM invoque obligatoriamente el script ni que el motor general de Gentle AI impida todos los saltos: ese comportamiento universal sigue NOT_PROVEN. La skill obliga a usar el comprobador y RDD nativo, con evidencia separada.
Nota de ejecución: el primer intento de los dos tests CLI detectó un hash obsoleto en el fixture sintético después de cambiar sus falsadores; se conserva en tests-fixture-debug.stderr. Se corrigió el fixture, se recalculó su hash y la ejecución posterior completa terminó 34 tests OK. No se trató el rechazo por hash como si fuera el rechazo por entrevista esperado.


## Valoración final literal del interrogador

Q1 ANSWERED: los registros suministrados contienen los mismos 19 archivos y hashes SHA-256 entre 20261026T165542Z y 2026-10-26T17:11:50.119230+00:00. Respaldan igualdad de contenido entre esas observaciones; no prueban ausencia de cambios intermedios ni integridad de archivos ajenos al inventario. Q2 ANSWERED dentro del alcance documental: el código suministrado valida las dependencias y el registro antes de aceptar READY, y exige entrevista COMPLETE y diseño REVIEWED mediante INTERROGATION_INCOMPLETE. La salida registra 34 pruebas satisfactorias, incluidas la negativa CLI con entrevista PAUSED, su control positivo y casos de cobertura incompleta, respuestas pendientes y UNKNOWN. El fallo inicial por hash se distingue del rechazo esperado y no se usa como prueba de este. Ambas cuestiones acotadas quedan resueltas con la evidencia suministrada. Esto no certifica recibos RDD reales, invocación obligatoria del validador por cualquier LLM ni cumplimiento universal del runtime; esas garantías siguen NOT_PROVEN.

Estado: COMPLETE solo para las dos cuestiones acotadas de esta prueba. No equivale a cierre de QA ni garantía universal.
