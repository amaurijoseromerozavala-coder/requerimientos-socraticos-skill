# WU-RS3-PRINTED-CODE-AUTHORITY-CONTRACT-033

## Origen y objetivo

El maintainer decidió sustituir PBKDF2 como mecanismo objetivo de D03 por
códigos impresos de un solo uso y recibos vinculados a la decisión exacta.
Conservar D03 `EVERY_CONFIRMATION`, la separación D05, la distinción entre
aceptación semántica y permiso operativo, y el bloqueo de autoridad real.

## Alcance

Solo contratos documentales, ADR y tests de contrato. No crear tarjetas,
códigos reales, cuentas, servidor, enlaces, credenciales ni commits de
autoridad. El auditor PBKDF2 existente queda como componente histórico
no autoritativo; retirarlo requiere otra unidad. Ningún SHA o commit Git
demuestra por sí solo identidad humana.

## Oráculos RED congelados

1. `PRINTED_COORDINATES` es el mecanismo ratificado, con verificación fresca
   para cada categoría confirmable; PBKDF2 deja de ser el perfil objetivo.
2. El desafío y el recibo vinculan versión, categoría, propuesta, snapshot,
   manifiesto de presentación, opción/decisión, nonce, audiencia y política.
   Cualquier cambio invalida el recibo anterior.
3. El guardián consume el código atómicamente con el registro privado; replay,
   código agotado, fallo de persistencia o estado incierto bloquean. El agente
   no recibe códigos ni acceso al almacén de verificación.
4. La respuesta personalizada permanece solo en el historial de entrevista;
   no solicita código ni produce recibo hasta reformulación y selección.
5. Sin implementación y pruebas materiales D05, las salidas siguen
   `NOT_ESTABLISHED`, `SECURITY_BOUNDARY_UNMET` y `execution_authorized=false`.

## Secuencia

ODD → test de contrato RED → corrección documental mínima → GREEN y regresión
→ RDD Gentle AI del candidato exacto → respaldo Git solo tras aprobación.

## Límites y falsadores pendientes

Las pruebas documentales no demuestran control del origen UI, custodia física
de la tarjeta, separación UID, resistencia a elevación ni recuperación. Una
implementación posterior debe probar código incorrecto, doble consumo,
interrupción entre consumo y recibo, modificación de opción/snapshot y
suplantación desde la cuenta real del agente en el equipo objetivo.

## Evidencia observada

- RED: `python3 -B -m unittest skills/requerimientos-socraticos/tests/test_rs3_printed_code_authority_contract.py -q` terminó exit 1: faltaban `receipt_binding`, `credential_profile` y la UI aún declaraba el perfil anterior.
- GREEN focalizado: 14 tests de los contratos de D03, D05, UI y portabilidad terminaron exit 0.
- Regresión: con el intérprete base sin Z3, la suite integral terminó exit 1 por `SOLVER_UNAVAILABLE`/`ANALYZER_EXIT_FAILURE`; no fue GREEN del candidato.
- Regresión con dependencias declaradas: `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh` terminó exit 0: 55 CI, 133 supervisor, 62 QA y 409 requisitos. Esta corrida es del entorno cloud, no del i3/WSL.
- RDD del candidato exacto y respaldo: pendientes; ningún resultado documental habilita D03/D05.
- RDD inicial `review-d33fa690f4ca1ee2`: Gentle AI devolvió `approved`, pero la
  revisión independiente detectó que faltaba identificar la opción seleccionada
  cuando dos opciones tienen el mismo texto. No se reconoció ni publicó ese
  candidato. RED adicional focalizado: falta `selected_option_id`/
  `selected_option_sha256`. Se corrige y se exige revisión de nueva identidad.
