# WU-RS3-PRIVATE-INTERROGATION-CUSTODY-031

## Objetivo y precedencias

Continuar WU-030. Guardar localmente el historial propuesto fuera de Git,
entregar la pregunta a una TTY y registrar que los bytes se escribieron en
ese canal. Después, guardar la respuesta retransmitida sin autoridad. No
afirmar que una persona vio la TTY ni que escribió la respuesta.

## Alcance y límites

POSIX local. Raíz de custodia preexistente, propiedad del UID actual, modo
0700, fuera de cualquier worktree Git visible. Archivos 0600, nombres
generados por el programa, escritura atómica del historial actualizado y
sin sobreescritura de recibos. Bloqueo local entre operaciones concurrentes.
El usuario debe escoger una raíz sin sincronización externa: el programa
no puede comprobar toda la topología de sincronización ni protegerse de
otro proceso comprometido con el mismo UID. No crea cuentas ni credenciales.

Entrega observable significa solamente TTY_WRITE_COMPLETED: bytes concretos
escritos al descriptor de salida con plazo acotado. Ni screenshot ni recibo
prueban percepción humana. La respuesta sigue UNVERIFIED_RELAY. El CLI no
imprime texto de respuesta en errores ni publica el historial.

## Oráculos RED congelados

1. Crear un historial bajo raíz privada 0700 produce archivo 0600 y recibo
sin texto; TTY real acotada recibe pregunta, y el recibo de entrega liga el
hash de los bytes escritos.
2. Una raíz dentro de Git, con permisos excesivos, o symlink se rechaza sin
persistencia; entrega sin TTY y respuesta antes de entrega se rechazan.
3. Respuesta posterior conserva texto literal como UNVERIFIED_RELAY y
INTERPRETATION_REVIEW; una segunda respuesta y escrituras concurrentes
no silencian el estado anterior.
4. Fallo o plazo de escritura no crea recibo de entrega ni estado de éxito.

RED focal → GREEN/regresión → RDD exacto → respaldo Git.

## Evidencia

RED inicial: importación de `private_interrogation_store` inexistente,
exit 1. GREEN inicial: 4 tests, exit 0, tras corregir el rechazo previo a
entrega sin recibo. RED adversarial: historial con `false` sustituido por
`0` y recibo con campo de autoridad extra fueron admitidos (2 fallos,
exit 1); GREEN de 5 tests tras tipar el booleano y cerrar el recibo.
RED de presentación Unicode: control bidi no escapado (1 fallo, exit 1),
GREEN de 7 tests tras escaparlo. RED adicional: un marcador Git dañado
evitaba el detector y un reemplazo fallido dejaba temporal huérfano
(2 fallos, exit 1); GREEN de 8 tests. Flujo CLI real con pseudo-TTY:
9 tests, exit 0. RED de FIFO en archivo de sesión: lectura bloqueada hasta
timeout de prueba (exit 1); GREEN de 10 tests al abrir en modo no bloqueante.

La primera regresión integral falló en un test preexistente del supervisor:
`test_two_real_runs_reuse_only_after_durable_receipts` devolvía
`STOPPED/GROUP_CLEANUP` por el techo de 4.096 entradas `/proc` ante más de
4.100 zombis ajenos. Se abrió la unidad independiente WU-032 con su propio
RED/GREEN/RDD y respaldo. Tras incorporarla, regresión integral final
`ci/run_quality.sh`: exit 0; CI 55, supervisor 133, QA 62 y requisitos
401 tests. Hardware i3/WSL: NOT_RUN.

RDD inicial del candidato `sha256:4335d4b957c8e2f1289b94e8f7779e450c36bc1e4fe586db5325ea6955567231`
fue aprobado con dos advertencias R3-001/R4-001 sobre apertura bloqueante
del recibo de entrega sustituido por FIFO. No se publicó ese candidato.
RED adicional: el test de FIFO de entrega agotó su plazo de 1 s (exit 1).
GREEN focal posterior: 11 tests, exit 0, al comprobar existencia mediante
`stat(..., follow_symlinks=False)` sin abrir el objeto. Nueva regresión
integral final `ci/run_quality.sh`: exit 0; CI 55, supervisor 133,
QA 62 y requisitos 402 tests. Segundo RDD del candidato corregido
`sha256:c3b8e5f7e33c5c757c3be82521428220c0a25ab1f136f009d162b981df2b8e98`
aprobado con R3-001/R4-001: faltaba probar backpressure y un corte entre
crear y completar el recibo final podía bloquear la sesión. No se publicó.
RED de publicación: se esperaba fallo al enlazar el recibo, pero el código
ya había creado el nombre final (1 fallo, exit 1). GREEN focal: 13 tests,
exit 0, al escribir y sincronizar una etapa antes del enlace exclusivo;
se ensayó además escritura parcial y presión controlada en la TTY.
Regresión integral final `ci/run_quality.sh`: exit 0; CI 55,
supervisor 133, QA 62 y requisitos 404 tests. RDD final pendiente.

Tercer RDD del candidato `sha256:3593d5b692b3628570a98314cdf384286115c4551d147c1e5b8bb9297a0de385`
marcó `correction_required`: R3-001 y R4-001 comprobaron que un corte
entre el enlace y la retirada de la etapa dejaba `st_nlink=2` y bloqueaba
la respuesta. Se registró el plan de corrección en el runtime (90 líneas).
RED de dos puntos de interrupción: respuesta rechazada con dos enlaces y
etapa parcial no retirada (2 fallos, exit 1). GREEN focal: 15 tests, exit 0,
al usar un nombre de etapa por sesión y reconciliarlo bajo el lock antes de
entregar o leer el recibo. Regresión integral final `ci/run_quality.sh`:
exit 0; CI 55, supervisor 133, QA 62 y requisitos 406 tests.
Validación RDD pendiente.
