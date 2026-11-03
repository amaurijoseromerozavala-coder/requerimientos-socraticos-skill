# WU-SEC-HISTORY-001 — saneamiento verificable del historial público

## Specs

El propietario autorizó reescribir el historial y coordinar la actualización.
El alcance remoto observado es una sola rama principal; no se han observado
PR abiertos ni forks declarados. Se preserva una copia forense privada de la
historia original y se trabaja sobre un clon separado.

El candidato debe retirar de todos los blobs alcanzables los valores de
autorización expuestos, sin registrarlos en comandos, logs o documentos.
La búsqueda posterior recorre todos los commits y objetos alcanzables, no solo
HEAD. El resultado nuevo se compara por estructura con el original y ejecuta
la suite pertinente. Los cambios en OID invalidan referencias históricas y
pueden exigir corregir verificadores de procedencia.

## Oráculos

1. RED: un repositorio sintético con un valor ficticio en dos commits debe
   conservar ese valor antes de filtrar.
2. GREEN: el filtro lo elimina de todos los blobs y conserva el resto del
   contenido y los límites de rama.
3. Regresión: cero valores identificados en todos los objetos alcanzables,
   ausencia de valores en el árbol propuesto, suite de calidad y comprobación
   de correspondencia de referencias. Los valores históricos originales
   quedan solo bajo custodia privada.
4. RDD del candidato y su evidencia exacta antes de publicar. Un bloqueo de
   revisión, CI o confidencialidad impide la actualización remota.

## Coordinación

La publicación exigiría una actualización de la rama remota con protección
contra cambios concurrentes y un aviso a quienes mantengan clones antiguos.
No se presume conocer todas las copias existentes ni poder borrarlas.
