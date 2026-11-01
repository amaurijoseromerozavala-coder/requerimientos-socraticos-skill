# WU-SUP-GROUP-003 — pruebas de la observación R3-001

Se añadieron dos pruebas: error controlado al leer `/proc` tras la salida del hijo, y observación sintética de un grupo compuesto solo por zombis. La primera exige `UNCONFIRMED`, `INFRA_LOCK` y bloqueo de una segunda ejecución; la segunda exige que la salida normal siga siendo admisible. El proceso descendiente de la primera prueba se detiene en `finally`.

El código de producción vigente ya cumplía ambos contratos. Para falsar las pruebas, se introdujeron temporalmente dos mutaciones en una copia de trabajo: convertir el error de lectura en ausencia de grupo y contar zombis como miembros activos. Ambas pruebas fallaron por su aserción específica (RED) y el archivo de producción se restauró sin diferencias. Sobre el código real, las dos pasaron (GREEN) y la suite completa del supervisor terminó con 51 pruebas OK.

La prueba zombi usa datos `/proc` simulados, no reproduce un zombi real del kernel. No se ejecutó estrés ni calibración del hardware objetivo. La cobertura de estas ramas no demuestra recuperación, contención de otros grupos ni integración del journal. RDD pendiente.
