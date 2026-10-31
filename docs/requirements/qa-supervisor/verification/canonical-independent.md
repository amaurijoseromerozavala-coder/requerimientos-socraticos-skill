# Addendum independiente — candidato canónico

Fecha: 2026-10-30. Alcance: revisión documental exacta de prd.json esquema 2.0.0 y su correspondencia con anexos. Estado: REVIEWED_AS_DRAFT. No READY ni aprobación nativa RDD. No cambios a fuentes, implementación o ensayos de procesos/hardware.

## Correspondencia comprobada

- Los nueve anexos de candidate.sources existen y sus SHA-256 coinciden con los valores declarados.
- interview_ref y design_proposals_ref coinciden con los bytes actuales. Los documentos indican COMPLETE y REVIEWED respectivamente; estos estados no se interpretan como aprobación del producto.
- Los 17 requisitos mantienen exactamente sus textos EARS y lógica respecto a prd-draft.json. Se conservan restricciones de ejecución, incertidumbre, bloqueo/reinicio, diagnóstico opcional sin privilegios, retención mínima, reserva de capacidad y controles de recursos.
- Las 418 transiciones corresponden a 11 estados × 2 actores × 19 eventos, sin duplicados. Las transiciones explícitas del anexo para supervisor conservan destinos. El resto rechaza manteniendo estado y sin efectos. La condición inicial sigue RECONCILING.
- El digest candidate_sha256 coincide con la serialización JSON canónica con claves ordenadas, separadores compactos y UTF-8 sin escapes ASCII.

## Semántica y límites

El candidato conserva status=DRAFT y G-ASSURANCE material abierto. formal_status, checks y rdd permanecen NOT_RUN; la revisión presente no los cambia. Los falsadores de aceptación no se convierten en resultados ejecutados. La instrucción final exige autorización separada para implementar.

La FSM canónica abstrae únicamente eventos ya cualificados: guard_dnf=[{}] y effects={} no prueban por sí mismos identidad, captura, reloj, journal, conservación de latch o persistencia de recibo. environment_mapping remite expresamente a las guardas de fsm-propuesta.json y recovery-contract.json; abstraction_complete=false y la justificación declaran esa frontera. Por ello no se detecta degradación normativa respecto a los anexos, pero sí debe conservarse esa interpretación en cualquier revisión RDD: un ALLOW significa aceptar el evento de control dentro del modelo, nunca autorizar ejecución de aplicaciones/CI/producción.

Las listas invariants y variables vacías no acreditan invariantes del sistema completo. La tabla total verifica destinos de eventos enumerados, no que un adaptador real produzca solamente eventos válidos. Las propiedades físicas y temporales siguen fuera del modelo y pendientes de implementación/verificación autorizadas.

Los anexos hash-bound preservan la retención de recibos mínimos, límites provisionales, separación entre almacenamiento y journal, prohibición de desbloquear por PID/reconocimiento humano, recuperación conservadora y ausencia de garantía de disponibilidad. No hay hallazgos nuevos de incoherencia documental dentro del alcance revisado.

## Identidad revisada

- prd.json SHA-256 de archivo: `b2ca8750dfce4b257caaa0e085f0a3f5e10d76e798a5d1dd76cec87cebfd3cfd`.
- candidate_sha256: `f6ec6976acfe6b66dfc6358e734e1eeed16d8c4b9786328525058a11316152d5`.
