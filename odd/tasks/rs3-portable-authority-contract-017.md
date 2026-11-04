# WU-RS3-PORTABLE-AUTHORITY-CONTRACT-017

## Objetivo y precedencias

Diseñar una frontera de autoridad portable para D03/D05 sin afirmar que exista
una autenticación universal ni sustituir la decisión ratificada de cuenta local
separada. Depende de WU-013, WU-014 y WU-016. Solicitud humana: buscar un método
que sirva en varios entornos y hardware; el equipo objetivo no está disponible.

## Alcance y criterios de aceptación

Solo contrato documental y pruebas de contrato. El protocolo común debe ligar
categoría, propuesta, snapshot, bytes canónicos, nonce de un solo uso, audiencia
y política; separar aceptación semántica de permiso operativo; exigir prueba de
frontera independiente y verificación de recibo antes de cualquier promoción.
Los perfiles locales, TOTP, tarjeta y autenticación de plataforma son adaptadores
posibles, no garantías intercambiables. D03 conserva PBKDF2 por cada confirmación
en el perfil elegido; D05 conserva la cuenta local separada para Linux/WSL.
Entorno no soportado, reloj desconocido, credencial accesible al agente o
evidencia incompleta bloquean. La evaluación real y el hardware i3 quedan
NOT_IMPLEMENTED/NOT_RUN.

## Oráculos RED congelados

1. Existe contrato de protocolo que enumera todos los campos de vinculación,
   obliga a validarlos juntos y separa los dos tipos de autoridad.
2. Un perfil desconocido o incompleto conduce a `BLOCK`; ninguna entrada
   documental concede `HUMAN_CONFIRMED` ni `execution_authorized=true`.
3. La cuenta local ratificada permanece como perfil pendiente de verificación;
   TOTP y tarjeta no se promueven por conveniencia y no sustituyen aislamiento.
4. Los riesgos de pérdida/replay, reloj, privilegios, host y recuperación se
   explicitan; pruebas materiales por plataforma permanecen pendientes.

RED → documentación mínima → GREEN/regresión → Gentle AI RDD exacto → Git.

## Evidencia local

- RED: los cuatro controles terminaron con `FileNotFoundError` para el contrato
  de portabilidad ausente, exit 1, antes de añadirlo.
- GREEN focalizado: cuatro controles, exit 0.
- Regresión final: `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh`,
  exit 0; 55 CI, 130 supervisor, 62 QA, 346 requisitos. Este runner cloud no es
  el equipo objetivo; ninguna comprobación de aislamiento físico se ejecutó.
