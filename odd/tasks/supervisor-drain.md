# WU-SUP-CORE-002 — Captura durante terminación (R4-1)

Solicitud: «continua el desarrolo». Resolver primero R4-1 del RDD anterior.
Alcance: núcleo Linux existente; no integración QA, diario durable ni hardware.

## Oráculo y aceptación

Un hijo real que emite diagnósticos al recibir SIGTERM debe poder terminar con
exit 0 sin SIGKILL si cumple el plazo de gracia. Sus bytes deben conservarse por
canal hasta los límites. Si emite más, seguir drenando y descartando el exceso,
marcando truncado sin aumentar retención ni reiniciar plazos. Preservar el motivo
original de parada. Confirmar recolección independientemente de EOF de las tuberías;
un canal sin EOF al vencer el presupuesto debe declararse captura incompleta.

Pruebas RED: cierre con stdout/stderr y volumen superior a capacidad de pipe pero
acotado (<=512 KiB por caso). GREEN y regresión del núcleo; fallos simulados de
wait continúan bloqueando la instancia. Sin cargas de memoria/swap ni CPU intensiva.

RDD exacto antes de publicar. Mantener recibo y observación anteriores históricos;
no declarar resolución global, integración QA ni aislamiento de descendientes.

## Log
RED: tres fallos de diagnóstico/escalada innecesaria. GREEN: trece pruebas iniciales; añadida regresión de escritura activa sin extensión del plazo, catorce finales OK. Lectura acotada/descartes/EOF separados de recolección. Observaciones y logs conservados; RDD pendiente.
