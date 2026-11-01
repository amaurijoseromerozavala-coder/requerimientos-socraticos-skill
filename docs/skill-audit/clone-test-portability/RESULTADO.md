# WU-CLONE-TEST-001 — candidato para RDD

Resuelve review-1065b747da56ecf9/R3-1. Solo pruebas y evidencia.
RED: exportación temporal sin .git, fallo único de positivo dependiente del origin.
GREEN:10tests en la misma exportación y10en clon real. Son dos ejecuciones de
la misma suite, no20casos distintos. El positivo ahora usa respuestas Git
controladas, verifica comandos exactos y OID40/64. Nuevo negativo rechaza origin
no listado. No cambia política de clon, worker, almacenamiento ni versión2.4.8.
Mocks verifican contrato de llamadas; no sustituyen observación real del clon.
Reproducción: ejecutar check_export.py con intérprete que tenga jsonschema.
No cambios al remoto real ni acceso al i3. RDD pendiente; retained-pipe excluido.
