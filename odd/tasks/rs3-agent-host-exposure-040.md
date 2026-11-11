# WU-RS3-AGENT-HOST-EXPOSURE-040

## Objetivo y alcance

La evidencia aportada por el operador en el equipo objetivo informa que WU039
instaló el runtime y la regresión terminó exit 0. Esa transcripción también
demuestra la necesidad de observar vías de control hacia el host y sockets de
servicios privilegiados. Es evidencia `USER_REPORTED`, no una prueba
independiente de que el agente haya alterado un futuro guardián. D05 sigue
`NOT_ESTABLISHED` y la cuenta guardián/UI aún no existen. Ampliar el sondeo
D05 para detectar pasivamente estas exposiciones
incluso sin UID/ruta de guardián. No invocar sudo, Docker ni binarios Windows;
no crear cuentas, cambiar host, emitir códigos o habilitar autoridad.

## Oráculos RED congelados

1. Un socket Docker de tipo socket con permiso de escritura se clasifica
   `EXPOSED`; mera pertenencia a un grupo o ruta inexistente no prueba acceso.
2. WSLInterop habilitado se clasifica `EXPOSED`. Un montaje Windows escribible
   es una exposición separada. Ausencia o error de lectura queda
   `NOT_ASSESSED`, no se transforma en aislamiento demostrado.
3. `--agent-only` opera sin guardian designado, no inspecciona almacenes ni
   ejecuta binarios externos, y nunca emite autoridad o permiso.
4. El sondeo completo conserva sus comprobaciones de UID/ruta, incorpora
   exposiciones observadas sin aceptar una topología peligrosa y sigue sin
   autorizar incluso cuando los controles locales simulados son favorables.
5. El contrato distingue exposición de bypass materialmente demostrado;
   no afirma que la UI, Git privado, nonce o recibos estén implementados.

## Gates

ODD → RED observado → implementación mínima → GREEN/regresión → revisión
independiente → RDD exacto → respaldo Git. Los ensayos en el equipo del usuario
siguen siendo `USER_REPORTED`; no ejecutar estrés ni alterar sus permisos.

## Evidencia de falsación local

- RED inicial: la suite focal falló por `ImportError` al importar el nuevo
  observador antes de implementarlo.
- Revisión independiente: señaló que el permiso de escritura, sin lectura,
  basta para conectar con un socket UNIX, y que un montaje Windows escribible
  debía reflejarse también en `windows_host_control`.
- RED de esos dos casos: `Ran 12 tests`, `FAILED (failures=2)`; el socket
  escribible se clasificaba `ACCESS_DENIED_OBSERVED` y el control de host
  quedaba `NOT_ASSESSED` pese al montaje escribible.
- GREEN focal tras la corrección: `Ran 12 tests`, `OK`.
- Regresión local con intérprete temporal Python 3.12, `z3-solver==4.15.4.0`
  y las dependencias del repositorio: `ci:55`, `supervisor:169`, `qa:62`,
  `requirements:429`, todos `OK` con `ci/run_quality.sh` (exit 0). El script
  fija 1 GiB de límite virtual interno. No se hicieron ensayos en el i3/WSL.
- Esta observación no prueba que una cuenta guardián futura pueda ser alterada
  desde el agente. D05 permanece bloqueado y no hay autoridad de ejecución.
