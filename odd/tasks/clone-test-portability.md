# WU-CLONE-TEST-001

Resolver observación no bloqueante review-1065b747da56ecf9/R3-1.
Objetivo: suite de almacenamiento ejecutable desde exportación sin .git o fork,
sin cambiar política de origins ni código de producción. El caso positivo debe
proveer metadatos Git controlados y comprobar llamadas; rechazo de origin no
admitido debe seguir verificado. No modificar remotos del clon real.

ODD → RED en exportación aislada → GREEN misma exportación + suite local → RDD.
Mantener pendiente retained-pipe separado. Publicar solo después del RDD.

## Evidencia
Exportación sin Git: RED1fallo pertinente, GREEN10tests. Clon local:GREEN10tests.
Positivo aislado y negativo de origin no listado; código de producción intacto.
