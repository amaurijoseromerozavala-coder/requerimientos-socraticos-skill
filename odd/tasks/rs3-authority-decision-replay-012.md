# WU-RS3-AUTHORITY-DECISION-REPLAY-012

## Objetivo y precedencias

Depende del auditor PBKDF2 y del registro RS3 ya existentes. Evitar que una
comprobación correcta para el mismo `proposal_id`, snapshot y texto de decisión
se registre como aceptada otra vez usando un nonce nuevo. Es una defensa
documental del backend local; no acredita identidad humana ni resuelve por sí
sola el aislamiento D05.

## Contrato y alcance

El registro evalúa duplicidad del `subject_sha256` de un evento
`PASSWORD_CHECK_ACCEPTED` bajo el mismo bloqueo de archivo que su escritura.
Un intento fallido anterior no consume la decisión; el primer acierto sí.
Repetir el nonce continúa bloqueado. La salida y el disco nunca contienen
contraseña o texto de decisión. Los fallos cierran sin devolver un acierto.
La captura de `/dev/tty`, cuenta real, sudo/interop WSL y producción quedan
fuera de esta unidad. Solo se usan credenciales sintéticas.

## Oráculos RED congelados

1. Tras un acierto, repetir el mismo contenido con nonce diferente bloquea y
   no añade un segundo evento aceptado.
2. Tras un fallo, un acierto del mismo contenido con nonce distinto se permite.
3. Cambiar el snapshot o el texto crea un sujeto distinto, conservando la
   vinculación sin conceder autoridad.
4. Los controles de permisos, corrupción, duplicidad de nonce y coste PBKDF2
   existentes siguen pasando.

RED → implementación mínima → GREEN/regresiones → RDD exacto → respaldo Git.

## Evidencia RED/GREEN local

- RED: `test_success_cannot_be_replayed_with_a_fresh_nonce` terminó exit 1: no se lanzó `PasswordAuditBlocked`.
- RED concurrente: `test_concurrent_successes_admit_only_one_subject` terminó exit 1: ambos intentos fueron aceptados.
- GREEN focalizado: 9 tests de `test_rs3_password_auditor` y 7 de `test_rs3_audit_log` terminaron OK. La verificación amplia se registra antes de RDD.
- Regresión: `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh` terminó exit 0: 55 tests CI, 122 supervisor, 62 QA y 338 requisitos.
