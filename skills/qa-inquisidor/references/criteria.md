# Criterios delegados 0.1

Fuente humana: «Delegas esos juicios técnicos a la skill dentro de criterios
explícitos; las excepciones vuelven a ti.» No autoriza ensayos ni políticas nuevas.

- K1 Alcance: inventario de todo el sistema conocido y sus contratos, método de
  descubrimiento y fronteras trazados. El inventario trazado no demuestra
  completitud del mundo real. Componente conocido omitido implica GAP.
- K2 Materialidad: UNKNOWN se conserva como requerido. Una fuente pendiente no
  se convierte en NOT_APPLICABLE. Exclusión dudosa o que contradice la intención
  humana se consulta y mantiene pendiente.
- K3 Suficiencia: cada caso requerido tiene oráculo previo y evidencia vigente
  del tipo exigido y del mismo contexto. Análisis no demuestra comportamiento
  físico. Evidencia parcial, contradictoria, STALE o NOT_RUN no produce éxito.
- K4 Vigencia: criterios fijados antes del juicio y ligados a assessment,
  snapshot, versiones, entorno y alcance. Registrar actor real, razones y
  fuentes. Secuencia declarada o hash no autentican por sí solos un actor.
  Cambios materiales requieren invalidación y nuevo juicio, sin aprobación retroactiva.
- K5 Cierre: rechazo estructural antes de derivar eventos; luego fallo vigente,
  pendientes y finalmente éxito. FAIL conserva gaps. Entrega no implica PASS
  ni autorización de ejecutar. Toda excepción a K1–K5 requiere decisión humana.

El comprobador implementa consistencia estructural y de identidad de los datos,
no certifica la verdad de observaciones, materialidad o completitud. El asistente
debe justificar esos juicios usando fuentes autorizadas y declarar límites.
