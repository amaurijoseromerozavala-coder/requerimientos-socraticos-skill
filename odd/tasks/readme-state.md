# WU-README-STATE-001 — Estado verificable del proyecto

Solicitud: corregir observaciones de QA comprobadas usando skill, XERJ y MCP.
Único hallazgo aplicable: README agrupa todo el supervisor como no implementado
y el apartado WU-SUP-CORE-001 aún dice que faltan integración QA y diario durable,
aunque existen componentes parciales. Criterio: tabla y detalle distinguen núcleo,
adaptador, reserva persistente y supervisor ampliado. No proclamar integración
completa, recuperación, calibración física, CI o producción.

Tres afirmaciones del informe sobre VWAP/Z3, token confirmo y colector SQLite
carecen de archivos/subsistemas en este repo. No cambiar arquitectura ni añadir
módulos por esas hipótesis. La FSM parcial es un diseño declarado, no una garantía
de ejecución.

ODD → RED checker documental → GREEN y control negativo → Gentle AI RDD exacto →
commit y push normal tras recibo. No modificar fuentes de producto.

## Evidencia
XERJ CLI y llamada MCP xerj_search consultaron índice supervisor. RED del estado
README observado; GREEN y control negativo pertinentes. Solo README/documentos,
RDD pendiente. Sin decisiones humanas nuevas ni subsistemas incorporados.
