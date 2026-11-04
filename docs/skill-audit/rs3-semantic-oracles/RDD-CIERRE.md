# RDD — WU-RS3-SEMANTIC-ORACLES-005

Gentle AI revisó el candidato `sha256:52698748fd21281bf42502cb72b9494534bb2634024e22b367e7ec5bc9865692` bajo lineage `review-e4f2d24d98f89b33`. El runtime registró `approved` y `acknowledged`; la lente `review-reliability` no reportó hallazgos.

El revisor inspeccionó siete parches sin ejecutar comandos. En las pruebas locales, RED produjo ocho errores por ausencia de `semantic_fidelity`; GREEN posterior pasó 320 tests de Requerimientos Socráticos y 52 de CI, con una omisión CI explícita por falta del ZIP externo. La primera ejecución completa tras introducir el oráculo descubrió fixtures EARS incoherentes: cambiaban clase lógica o sujeto sin actualizar la frase. Se corrigieron sus textos manteniendo las aserciones del AST y del alcance documental.

El oráculo cubre solo cuatro plantillas sintéticas españolas. Fuera de ellas devuelve `NEEDS_CLARIFICATION`; no autentica procedencia del texto, intención humana ni concede autoridad o producción. Este recibo es posterior al candidato revisado.
