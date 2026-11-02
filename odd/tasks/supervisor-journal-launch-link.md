# WU-SUP-JOURNAL-LINK-004 — reserva durable y lanzamiento real

## Fuente y alcance

El propietario pidió continuar el desarrollo hacia producción. `docs/requirements/qa-supervisor/recovery-contract.json` exige RESERVED durable antes de `spawn`, ACTIVE con PID e identidad de inicio después, STOPPING antes de solicitar término y CONFIRMED_TERMINATED solo tras evidencia del hijo exacto. El núcleo y el journal existen pero no están conectados. Esta unidad implementa la conexión **optativa** para un llamador confiable que ya mantiene abierto el journal; no conecta aún `QASupervisor` ni habilita producción.

## Reglas de aceptación

- Sin journal, el núcleo conserva el comportamiento previo y sus pruebas.
- Con journal, `reserve(identity)` ocurre antes del intento de `Popen`. Si falla la reserva, no se lanza nada. Si falla el lanzamiento o se interrumpe la identidad tras el lanzamiento, la reserva no se borra ni se atribuye éxito.
- Tras lanzar, se observa PID y starttime de `/proc/<pid>/stat` mientras el hijo directo aún no ha sido recolectado y se registra ACTIVE. Una identidad no legible bloquea el resultado.
- Antes de solicitar término al hijo vivo, se intenta persistir STOPPING. Un fallo de escritura no omite la limpieza del proceso, pero bloquea admisión posterior.
- Solo si la recolección del hijo y la observación del grupo terminan favorablemente se registra CONFIRMED_TERMINATED. Se mantiene no-IDLE, pendiente de reconciliación e incorporación. No hay reset automático ni nueva ejecución en esa instancia.
- Las pruebas usan procesos pequeños, plazos breves y stores temporales; no saturan recursos ni simulan la calibración del i3/WSL.
- El README distingue enlace optativo del núcleo de una integración QA todavía ausente, e identifica CONFIRMED_TERMINATED como estado pendiente de reconciliación.

## Falsadores

- El constructor permite un journal sin identidad o viceversa.
- Se observa `Popen` antes de RESERVED.
- Una falla entre spawn y ACTIVE devuelve un resultado admisible o borra la reserva.
- Una nueva ejecución se lanza con estado CONFIRMED_TERMINATED no reconciliado.
- El registro acepta CONFIRMED_TERMINATED con PID/starttime distintos o desde RESERVED.

## Tareas

1. RED: pruebas de integración y control de transiciones fallan contra las APIs aún ausentes.
2. GREEN: introducir enlace optativo y estado terminal conservador; ejecutar suite del supervisor.
3. Revisar límites, cerrar candidato, RDD nativo Gentle AI y, solo con recibo aprobado, publicar y verificar SHA remoto.

## Registro

- 2026-11-01 (hora cliente): unidad abierta antes de modificar producción.
- 2026-11-01 (hora cliente): RED de enlace: 5 pruebas fallaron por ausencia de `journal=` y `record_terminated`. RED documental: README no describía enlace ni estado terminal. GREEN focal: 11 pruebas, incluido `os._exit` después de RESERVED y antes de Popen. La primera regresión local identificó dos controles históricos que requerían alinearse con el nuevo contrato; regresión final: 62 pruebas OK. Sin ensayo en el equipo i3/WSL.
