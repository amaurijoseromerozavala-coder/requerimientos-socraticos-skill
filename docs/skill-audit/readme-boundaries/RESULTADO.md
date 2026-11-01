# WU-README-BOUNDARIES-001 — candidato para RDD

Cierra observación review-644ca171b5b73b87/R3-001. El checker existente daba
PASS a un README modificado en copia temporal que afirmaba recuperación y
lanzamiento completos para la reserva. RED: el control exigía rechazo, pero
el checker imprimió README_COMPONENT_STATES_OK y el control terminó con error.

GREEN: el checker localiza las filas y exige literalmente que la reserva no esté
conectada al lanzamiento y que el sistema completo siga no implementado. El
mismo control negativo ahora detecta README_FALSE_RESERVATION_SCOPE. El control
positivo y el negativo anterior de fila omitida siguen pasando.

Son garantías de redacción acotadas a frases del README, no verificación formal
de arquitectura ni comportamiento físico. XERJ CLI/MCP se usó en la unidad
precedente para localizar los componentes; no se reindexó el proyecto por este
test. No se modificó README ni código de producción. RDD pendiente.
