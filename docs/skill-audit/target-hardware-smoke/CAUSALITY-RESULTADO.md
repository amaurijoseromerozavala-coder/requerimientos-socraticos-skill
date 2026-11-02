# WU-TARGET-CAUSALITY-006

Se cerró la observación documental R3-1: el comprobador ahora exige el vocabulario exacto de las cinco limitaciones aprobadas del informe `observation.json`. Una atribución causal añadida o sustituida ya no pasa el chequeo de este informe cerrado.

El control negativo falló antes de la corrección (`CAUSAL_ATTRIBUTION_ACCEPTED_UNEXPECTED`, exit 1) y pasó después (`CAUSAL_ATTRIBUTION_REJECTED_EXPECTED`, exit 0). El informe original conservó `DOCUMENTARY_CONTRACT_OK`. Cuatro mutaciones adicionales de conteo, autoridad, procedencia y limitación extra fueron rechazadas. Las salidas están en este directorio.

El control no interpreta lenguaje natural arbitrario, no autentica las mediciones comunicadas por el usuario y no prueba comportamiento bajo carga del hardware. RDD del candidato exacto: pendiente.
