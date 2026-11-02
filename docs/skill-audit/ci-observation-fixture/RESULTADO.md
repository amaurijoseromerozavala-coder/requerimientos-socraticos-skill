# WU-CI-OBSERVATION-009 — resultado previo a RDD

El run remoto `41396305785` del commit `2c597d4` falló porque el test de observación de grupo asumía que un proceso auxiliar seguía visible cuando se inyectaba un error de lectura de `/proc`. Ese supuesto dependía de la planificación del runner. Los extractos y la identidad del run están en este directorio.

El test ahora inyecta un `OSError` directamente en la observación que debe bloquear la instancia y comprueba una segunda ejecución rechazada. Una prueba separada verifica que una lectura fallida de `/proc`, una vez observado un miembro, se trata como incertidumbre. No se modificó el código de producción. El recorrido local completo terminó con exit 0: 7 pruebas de CI, 65 del supervisor, 62 de QA y 256 de Requerimientos.

La ejecución remota del nuevo candidato y su RDD siguen pendientes. Esta unidad no calibra el hardware i3/WSL ni habilita producción.
