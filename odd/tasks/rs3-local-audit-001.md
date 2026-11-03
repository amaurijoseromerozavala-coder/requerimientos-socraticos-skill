# WU-RS3-LOCAL-AUDIT-001

## Solicitud y decisión

El maintainer eligió D04: «Logs para auditar», como backend local sencillo sin
Argon2id. D05 conserva una cuenta local separada como objetivo de autoridad;
esta unidad no la crea ni autentica decisiones humanas.

## Contrato observable

- Registrar únicamente eventos documentales de vocabulario cerrado, referencias
  opacas y digest SHA-256; nunca texto de requisitos, secretos ni valores libres.
- Cada evento persistido declara `authority_verification=NOT_PERFORMED` y
  `execution_authorized=false`. Rechazar tipos de confirmación o autorización.
- Almacén privado y acotado; un archivo íntegro permite lectura secuencial y
  comprobación de enlace entre registros. Corrupción detectable, línea final
  incompleta, permisos inseguros o límite agotado bloquean nuevas escrituras.
  Una pérdida de registros completos del final no puede detectarse sin un
  anclaje externo del último digest. El enlace de hashes no autentica a otro
  usuario del mismo UID.
- No crear cuenta, servicio, interfaz de confirmación ni gate de despliegue.
- Pruebas locales temporales; calibración en el i3/WSL: NOT_RUN.

## Tareas y oráculos TDD

1. RED: evento permitido se conserva y lee; evento de autoridad se rechaza.
2. RED: corrupción, límite de capacidad y ruta no privada se rechazan.
3. Control negativo: retirar un registro final completo produce un prefijo
   válido; documentar esta limitación, sin atribuir detección inexistente.
4. Implementar registro mínimo, observar GREEN y regresión afectada.
5. Revisar candidato exacto con RDD; solo tras aprobación y reconocimiento,
   commit y respaldo remoto de esta unidad.

## Estado

RED observado: `python3 -B -m unittest supervisor.tests.test_rs3_audit_log -q`
falló por ausencia del módulo. GREEN inicial: seis pruebas pasan. Revisión RDD
y regresiones pendientes.
