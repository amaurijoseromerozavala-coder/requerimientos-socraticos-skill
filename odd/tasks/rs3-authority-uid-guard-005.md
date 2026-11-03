# WU-RS3-AUTHORITY-UID-GUARD-005

## Objetivo y evidencia

El maintainer pidió continuar hacia un backend que vincule una contraseña a
su decisión. La selección D05 exige una cuenta local separada, todavía no
verificada en el i3/WSL. La implementación actual permite dar de alta una
contraseña bajo cualquier UID; esta unidad cierra ese uso accidental bajo el
UID declarado del agente y vincula el verificador a las identidades locales.

## Contrato

- Alta requiere el UID del agente y rechaza si coincide con UID real/efectivo
  del proceso. Rechaza también ejecución con UID real y efectivo distintos.
- El almacén conserva `agent_uid` y `authority_uid` junto al verificador. Una
  comprobación futura rechaza si el UID actual no coincide con el propietario
  declarado o si vuelve a coincidir con el agente.
- La CLI exige `--agent-uid` en alta; no ofrece ruta implícita que permita
  omitir la comparación. Solo valores sintéticos se usan en pruebas.
- Esta comprobación es una guarda local, no prueba que el UID declarado sea el
  verdadero UID de Pi, ni ausencia de sudo, interop WSL o control del host.
  `authority_verification=NOT_ESTABLISHED` y D05 sigue bloqueado.

## Oráculos TDD

1. RED: alta con UID agente igual al actual, UID real/efectivo distintos o
   argumento omitido no debe crear verificador.
2. RED: comprobar desde otro UID o con configuración de identidad incoherente
   no debe producir coincidencia ni evento aceptado.
3. GREEN y regresiones; RDD del candidato exacto antes de commit/push.

## Estado

RED observado: tres casos fallaron por ausencia del parámetro y la vinculación
de UID; el control documental falló por campo ausente. GREEN dirigido: 4
controles de UID y 15 controles del backend/CLI. Regresiones: 120 del
supervisor, 314 de requisitos y 45 de CI. RDD pendiente.
Ensayo en WSL: NOT_RUN.
