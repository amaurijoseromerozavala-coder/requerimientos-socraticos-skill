# Contrato de evidencia — propuesta pendiente de revisión

Estado: DRAFT / PROPOSED. No implementado, no comprobado ni aceptado como política humana.
Origen: intercambio real Q-QA-005, registro-skill-asistente.json.

## Entrada y correspondencia

La evaluación identifica assessment_id, target_snapshot_id, environment_ref,
versions_ref y scope_ref. El inventario contiene obligation_id únicos,
aplicabilidad y materialidad justificadas con sus fuentes. Cada obligación
material aplicable enlaza case_ref, oracle_ref previo y required_evidence_kind.
La evidencia identifica sus bytes mediante hash, su fuente y snapshot, entorno,
versiones, resultado observado y valoración semántica identificada.
El hash identifica contenido: no acredita veracidad, autoridad ni suficiencia.

## Reglas de derivación propuestas

| Situación | Tratamiento |
| --- | --- |
| Todas las obligaciones materiales aplicables respaldadas favorablemente, identidad y tipo concordantes y juicios justificados | Puede derivarse RECORD_CURRENT_SUCCESS |
| Solo una parte respaldada, o NOT_RUN/UNKNOWN/juicio pendiente | RECORD_GAP_OR_STALE; no borrar pendientes |
| Snapshot distinto | Conservar evidencia histórica STALE; no usar como éxito vigente |
| IDs duplicados, referencias ambiguas o entrada malformada | Rechazar entrada sin transición; registrar diagnóstico |
| Conjunto vacío o aplicabilidad sin justificar | No derivar éxito por vacuidad |
| Contraejemplo vigente ligado a oráculo y obligación | Puede derivarse RECORD_CURRENT_FAILURE; no implica cobertura completa |
| Cambio material de entradas | INVALIDATE de conclusiones dependientes; conservar historial |

SUCCESS exige cuantificación sobre TODO el conjunto material aplicable, nunca
unión parcial que sobrescriba los pendientes. La identidad del entorno debe
corresponder al tipo de afirmación: análisis estático no acredita ensayo físico.

## Escenarios RED especificados antes de implementar

1. Dos obligaciones materiales, una favorable y otra NOT_RUN: rechazar SUCCESS.
2. Recibo favorable de otro snapshot: STALE, rechazar SUCCESS.
3. obligation_id duplicado: rechazar entrada antes de indexarla.
4. Inventario vacío: no producir éxito por cuantificación vacía.
5. Valoración semántica sin autoridad justificada: mantener pendiente.

Todos los escenarios están NOT_RUN. No se añade comprobador ni runtime de QA.
El modelo finito anterior y sus recibos no validan este contrato nuevo.

## Gaps preservados

Falta definir y aceptar quién valora la suficiencia semántica y el alcance,
el formato canónico de los registros y la correspondencia completa entre este
contrato y el modelo. RDD de este documento pendiente; migración canónica pendiente.
G1-SPEC permanece PARTIAL. CI diferido, hardware objetivo no medido.
