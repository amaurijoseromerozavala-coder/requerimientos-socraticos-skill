# WU-TARGET-SMOKE-005 — registro previo a RDD

Se incorporó la medición del propietario correspondiente al commit `6ca7fe48ecd730cbe58e3872bdeff00c45631a61`. Según el informe recibido, todas las condiciones previas pasaron; la suite del supervisor devolvió exit 0, 62 pruebas OK, 16,343 s de tiempo total, 12,515 s reportados por unittest y pico RSS de 31.636 KiB bajo `ulimit -v 524288` y plazo de 90 s. PSI I/O `full avg10` fue 0,01 % y 0,00 % antes, y 0,06 % después. No se atribuye causalidad a la diferencia de memoria Windows ni PSI.

La fuente es un resumen estructurado del propietario; no llegaron logs crudos ni hubo reproducción independiente. La observación prueba solo una corrida acotada en el equipo declarado. No demuestra estabilidad bajo saturación, ausencia de fallos, disponibilidad continua ni autorización de producción. `observation.json` conserva el alcance y la procedencia.

RED documental: evidencia ausente y README obsoleto. GREEN: `DOCUMENTARY_CONTRACT_OK`. Controles negativos: tres mutaciones de conteo, autorización y procedencia fueron rechazadas. No se cambiaron componentes ejecutables. RDD del candidato documental pendiente.
