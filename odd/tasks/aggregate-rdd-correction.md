# WU-SEC-AGGREGATE-RDD-001

## Objetivo

Resolver los hallazgos de la revisión RDD conjunta de los cambios de captura y
verificación del historial saneado, sin ampliar la capacidad del producto.

## Alcance y oráculos

1. Un comando de revisión en un string JSON con guiones codificados mediante
   escapes Unicode debe detectar y sanear su valor sensible antes de persistir
   o admitir evidencia pública. Un cambio Git con esa forma debe bloquearse.
2. El registro de captura debe conservar los metadatos de un argumento
   reconocido y no sensible, como `target`, sin bloquear la instancia.
3. Una clave `token` independiente, un argumento de ese nombre y cualquier
   estructura ambigua deben continuar saneándose o rechazándose.
4. Las pruebas negativas usan únicamente valores sintéticos. RED se observa
   antes de implementar; GREEN y regresiones se observan después.
5. El candidato corregido requiere RDD nativo aprobado y reconocido antes de
   commit y respaldo remoto. La verificación de historia no revela valores.
6. Una salida JSON ordinaria dentro del límite de bytes no debe bloquearse
   por número de elementos si no contiene marcadores sensibles.
7. Un comando sensible seguido de espacio escapado en JSON debe sanearse
   tras decodificarlo, conservando el resto del documento.

## Límites

No se infiere validez de tokens históricos, cierre de alertas externas ni
eliminación de copias remotas no alcanzables desde la rama actual.
