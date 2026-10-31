# Resultado RDD del primer candidato integrado

Gentle AI 4.2.0 completó las revisiones de resiliencia y fiabilidad del candidato autorizado. Estado: APPROVED_AND_ACKNOWLEDGED. Los 13 archivos conservan los hashes del manifiesto.

Candidato: `sha256:551a7a33c412f242c3c2c69437f46ef72ce992dec5ebed848af5af28f98384c2`.

## Observación R3-001

No bloqueante y pendiente como trabajo posterior: el comprobador documental verifica transiciones locales, pero no comprueba el manejador global de revocación. Se requieren aserciones sobre cobertura y prioridad y un control negativo que retire ese manejador y falle. El modelo sí contiene el manejador; la carencia está en su verificación automatizada. No se alteró el candidato aprobado.

## Alcance y límites

23 requisitos derivados de decisiones, 128 valoraciones booleanas y FSM parcial de 9 estados/13 aristas. La revisión nativa inspeccionó los parches; no ejecutó los tests ni verificó físicamente el sistema. El PRD sigue DRAFT: faltan presupuestos concretos, contratos de adaptadores, control de recursos, terminación, durabilidad y garantías de incorporación. No habilita implementación ni producción.

Recibos: `capture-reliability.json` contiene los dictámenes completos; `rdd-final.json` registra el cierre reconocido.
