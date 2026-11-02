# WU-CI-RDD-008 — resultado previo a revisión

Se añadió un cierre posterior y acotado del RDD de WU-SUP-PRE-REAP-007. El verificador de CI comprueba la correspondencia del commit `3656381`, su árbol, la identidad de revisión y los bytes del marcador local publicado. El cierre declara su procedencia como transcripción del agente y deja explícito que la autenticidad externa del revisor no está establecida. El expediente original permanece intacto como registro previo a aquel RDD.

Se añadió un workflow GitHub Actions con token de solo lectura, una ejecución por referencia, Python 3.12, dependencias fijadas, plazo de 5 minutos y suites secuenciales acotadas. RED: ausencia inicial del verificador/workflow, estado público contradictorio, salida normal de 518537 bytes frente a una cota de 16384 y un control negativo que detectó la pérdida del código de fallo. GREEN local: 7 pruebas de contrato, 64 del supervisor, 62 de QA y 256 de Requerimientos; exit 0 y 193 bytes de stdout. Los artefactos pequeños están en este directorio.

El CI remoto aún no ha corrido en el commit de esta unidad. La API de permisos de Actions devolvió 403 para la integración disponible, por lo que su configuración administrativa permanece **NO_VERIFICADA** hasta observar el workflow en GitHub. La protección obligatoria de `main` y producción quedan fuera de esta unidad. RDD del candidato exacto: pendiente.
