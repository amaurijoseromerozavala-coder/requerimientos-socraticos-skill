# WU-RS3-CANDIDATE-RESERVATION-BINDING-037

## Objetivo y precedencias

Integrar los componentes sintéticos WU-034 (identidad de desafío), WU-035
(registro de coordenadas) y WU-036 (comparación y gasto) mediante una ruta
acotada que derive siempre el digest del desafío de la presentación, opción
y metadatos completos. El registro no recibirá un digest libre del llamador
por esta ruta. La petición humana «Procede» continúa la construcción local.

## Alcance y límites

`CandidateCodeFlow.reserve` recompone el desafío y comprueba tarjeta y
coordenada con el registro antes de reservar. `check_and_spend` recompone el
mismo desafío y solo compara el código si el registro conserva PENDING para
esa identidad. Su salida conserva `authority_verification=NOT_ESTABLISHED` y
`execution_authorized=false`, incluso si hay coincidencia. Solo se usan
fixtures sintéticos; ninguna cuenta, UI, tarjeta real, recibo, Git de autoridad
o permiso operativo. La identidad de entrada sigue siendo una propuesta del
llamador: no demuestra procedencia humana ni custodia D05. `expiry` queda
vinculado como dato, sin afirmación de verificación temporal.
Antes de reservar se comprueba que el verificador privado existe y es íntegro.
Esa lectura previa no forma una transacción con la reserva: un actor del mismo
UID aún puede alterar el archivo entre ambas llamadas. No se promete
recuperación automática de PENDING bajo esa carrera.

## Oráculos RED congelados

1. Una reserva exacta devuelve PENDING y la identidad derivada; comprobarla
   con el código correcto gasta la coordenada y sigue sin autoridad.
2. Cambiar después de reservar pregunta, orden, opción, categoría, snapshot,
   audiencia, política, nonce o expiración impide devolver coincidencia y
   conserva PENDING. Dos opciones con igual texto e IDs distintos no comparten
   identidad.
3. Tarjeta o coordenada ajena, manifiesto manipulado, digest libre y metadatos
   desconocidos se rechazan; ninguna respuesta revela código ni crea recibo.
4. Un segundo intento, desafío distinto, etapa pendiente, verificador incierto
   o gasto no confirmado nunca devuelve éxito; los componentes mantienen sus
   fallos cerrados y sus límites de recursos.
5. Verificador ausente, corrupto o con provisión pendiente bloquea **antes**
   de reservar; AVAILABLE no se consume por una ruta sin verificador.

## Proceso

ODD → RED observado → implementación mínima → GREEN y regresión → revisión
independiente y RDD nativo del candidato exacto → respaldo Git. i3/WSL y
separación real de cuentas: NOT_RUN. D03/D05 y producción permanecen bloqueados.

## Evidencia RED/GREEN focal

RED inicial: `python3 -B -m unittest
supervisor.tests.test_rs3_candidate_code_flow -q` falló con
`ModuleNotFoundError: supervisor.rs3_candidate_code_flow` (módulo ausente).
Después de la primera implementación, cuatro pruebas pasaron. La revisión
independiente reprodujo otra brecha: reservar sin `verifiers.json` dejaba
PENDING y el aprovisionamiento posterior fallaba. El nuevo falsador RED
`test_missing_or_unconfirmed_verifier_blocks_before_reservation` falló con
`AssertionError: CandidateFlowBlocked not raised`. GREEN tras exigir
verificador íntegro: seis pruebas iniciales de la unidad y nueve del
verificador, `Ran 15 tests ... OK`, exit 0. Después, el control documental
dio RED con `KeyError: candidate_reservation_binding`; al registrar el estado
no autoritativo en el contrato, ocho pruebas finales de la unidad pasaron.
La suite focal de los cuatro componentes terminó con 29 pruebas `OK`.

Regresión completa: `PATH=/tmp/rs3-wu037-venv/bin:$PATH
REQUIREMENTS_PYTHON=/tmp/rs3-wu037-venv/bin/python bash ci/run_quality.sh`,
exit 0: 55 pruebas CI, 162 supervisor, 62 QA y 409 requisitos, todas `OK`.
La revisión independiente no halló bloqueo crítico de código en el alcance
sintético; señaló la carrera del mismo UID, demostrada por prueba y conservada
como brecha D05. RDD nativo y hardware objetivo: pendientes en este punto.
