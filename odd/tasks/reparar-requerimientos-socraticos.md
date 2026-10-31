# Reparación de requerimientos-socraticos en Gentle AI

## Specs

- S1: "detén el avance de la skill qa". Mantener íntegros los artefactos QA; solo registrar pausa en metadatos externos.
- S2: "la skill ... debe hacer un interrogatorio socrático". Ciclo real de pregunta, respuesta, crítica y siguiente pregunta, con espera explícita y cobertura material. Una pregunta por intercambio, no una sola pregunta total.
- S3: "debe asumir rol de arquitecto y científico del software senior". Rol operacional: arquitectura de sistemas, epistemología, hipótesis, alternativas, evidencia, experimentos, límites y falsación.
- S4: "preguntas ... que te hizo la skill y las respuestas que tú diste". Distinguir interlocutores y registrar intercambios reales; preguntas técnicas al asistente respondedor y decisiones de negocio al humano. Sin diálogo ficticio.
- S5: "Debe sugerir mejoras al diseño consultar mcps y skills firts realizar exploración web". Investigación pertinente MCP/skills primero, fuentes web primarias, mejoras con alternativas y falsadores.
- S6: "repara los fallos ... usando gentle-ai". Auditoría skill-improver, criterios RED antes de modificar, cambios acotados a la skill, validación reproducible, registro y RDD nativo del candidato exacto.

## Tasks

- T1 [S1-S6]: detener QA y conservar hashes; auditar contrato y definir regresiones. Completada.
- T2 [S2-S5]: reparar rol, protocolo de interrogatorio, registro, cobertura, investigación y propuestas; contratos JSON compatibles con separación de autoridad. Completada.
- T3 [S2-S6]: pruebas negativas y sesión real independiente entrevistador→asistente, sin ejecutar QA; conservar preguntas/respuestas observables. Completada: 34 tests y 2 preguntas reales.
- T4 [S1,S6]: revisar con RDD, refrescar registro e instalaciones enlazadas, comprobar QA íntegro, espejar Engram y entregar. Completada.

## Log

L1: Peticiones literales del usuario preservadas en Specs. No retomar ni implementar QA Inquisidor. La reparación de instrucciones no equivale a demostrar obediencia autónoma del LLM en todos los casos.
L2: Defectos iniciales: rol no explícito; bucle de interrogatorio insuficientemente obligatorio; ausencia de interlocutores/registro verificable; promoción de interpretación a significado confirmado sin gate; propuestas arquitectónicas e investigación sin contrato observable.

L3: Reproducido RED: schema anterior aceptaba READY sintético sin registro. V2 mantiene lectura de DRAFT v1, rechaza READY v1 y liga PRD v2 a entrevista y propuestas mediante hashes.
L4: 34 pruebas PASS y diálogo real de dos preguntas; valoración final nativa limita resultado al smoke test. No afirma cumplimiento universal del LLM. Error de hash en fixture durante tests CLI conservado como depuración, corregido antes del resultado final.
L5: Rol requirements-interrogator registrado para Codex en los tres directorios configurados; MCP existentes y límites de concurrencia preservados. 19 archivos QA y su inventario permanecen idénticos. Fuentes primarias NASA/SEI consultadas, memoria Engram #9 con conflictos históricos explícitos.

L6: La revisión de contratos aislados encontró dependencia faltante en el candidato. Recuperación nativa automática scope_changed conservó el antecesor e incluyó el paquete completo, sin fabricar autorización ni reiniciar el mismo intento.
L7: RDD completo detectó bypass de aplicabilidad; plan de 160 líneas, RED observado (4 fallos genuinos), corrección de 42 líneas y 40 tests PASS. Validación dirigida aprobó el arreglo.
L8: Ajuste posterior 2.0.1 resuelve dos advisories (misma dimensión y referencias PRD/topics). RED reproducido, 43 tests PASS; revisión por overlay contra snapshot aprobado de 76 líneas; cuatro lentes sin findings, approved y acknowledged.
L9: Rol y symlinks comprobados, registro Gentle AI refrescado, 19 archivos QA íntegros. Resultado y registro real en docs/skill-audit/requerimientos-repair/RESULTADO.md. No reanudar QA sin instrucción humana.
