# WU-SUP-GROUP-002 — resultado local previo a RDD

Un ensayo acotado observó una salida `EXITED` con `returncode=0`, `cleanup=CONFIRMED`, canales completos y un descendiente vivo tras la recolección del hijo directo. Las pruebas RED del candidato reprodujeron el falso resultado admisible y el README desactualizado. El segundo control RED mostró que el caso de tubería retenida también exigía la nueva clasificación.

El núcleo ahora observa si el grupo conserva miembros no zombis después de recolectar al hijo. Si los hay, o si la observación falla, bloquea la instancia como `INFRA_LOCK` con limpieza no confirmada. No envía señales a un PGID cuyo hijo ya fue recolectado. El README distingue el registro implementado hasta STOPPING del enlace al lanzamiento aún ausente.

GREEN focal: 2 pruebas OK. Regresión final del supervisor: 49 pruebas OK. Un primer barrido de regresión detectó la necesidad de distinguir grupos con solo zombis; se observó en la sesión, pero su log fue sustituido al repetir la regresión. El escaneo de `/proc` y la comprobación del grupo son observaciones puntuales, no aislamiento de todos los descendientes ni garantía ante cambios concurrentes. Sin recuperación automática, conexión del journal, calibración física ni autorización de producción. RDD pendiente.
