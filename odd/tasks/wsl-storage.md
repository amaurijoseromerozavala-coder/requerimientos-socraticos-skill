# WU-WSL-STORAGE-001 — Capacidad visible y anfitrión

Usuario pide incorporar evidencia WSL y actualizar la skill en un clon verificable.
Hechos aportados por consola (históricos, no medición de este ejecutor): WSL RAM6GB,
swap0, sin zRAM observada; ext4 878GiB libres; distribuciónUbuntu alojada en C:
con 14.59GiB libres en la mediciónWindows. No incorporar identidad/ruta personal.

Criterios: diferenciar filesystem visible y volumen anfitrión; no autorizar expansión
por disk_usage ni reutilizar dato humano como dato vivo. Solicitud explícita de bytes
con anfitrión UNKNOWN bloquea; memoria y entrevista se distinguen de capacidaddisco.
Este incremento no implementa recolector Windows ni reserva de disco física.

Instalación: clon oficial /workspace/publicacion-proyecto-integrado verificado.
Registros actuales .agents/.codex apuntan a antigua réplica. Preparar enlace al clon
oficial tras RDD, sin destruir pendientes ni efectuar pulls automáticos. Verificar
origen, raíz y versión cada activación; si copia/clon desconocido, no afirmar clon.

RED antes de implementar; GREEN regresión de preflight/schema. Interrogación
independiente Q-WSL-001. RDD exacto antes de actualizar registros y publicar.

## Log
RED/GREEN guardados:7tests nuevos,8regresiones. Schema1.1.0 y dos invocacionesreales validadas. Interrogación Q-WSL-001 contrastada. Observaciones de esquema y premise dememoriaREADY corregidas. Instalación pendiente deRDD; no cambio físico al i3.

Revisión independiente: resolver P2 de existencia/tipo commit y consistencia de
estados schema. RED4fallos observados, GREEN9tests. RDD nativo aún pendiente.
