# ADR-001 — Autoridad RS3 en cuenta local separada

**Estado:** decisión de arquitectura D05 confirmada por el maintainer;
implementación y comprobación material pendientes. El [registro estructurado](authority-boundary-decision.json)
mantiene `runtime_enforcement=NOT_IMPLEMENTED`, `human_confirmation_enabled=false`
y `real_authority_gate=SECURITY_BOUNDARY_UNMET`.

## Contexto y decisión

Las decisiones propuestas por Pi/Codex no pueden confirmarse por el texto del
agente ni por un hash sin autenticación. El servicio que custodie claves y el
registro de autoridad deberán residir bajo una **cuenta local distinta** de la
que ejecuta Pi/Codex. El agente podrá someter una propuesta identificada y
verificar un recibo público, pero no leer la clave, escribir el registro, actuar
como la cuenta de autoridad ni emitir `HUMAN_CONFIRMED`.

La confirmación semántica del humano y el permiso para una acción real son
gates distintos. La aclaración humana sobre D04 exige que un backend compruebe
la contraseña antes de aceptar cada decisión y vincule la comprobación al
contenido decidido. Esa función está `NOT_IMPLEMENTED`; sigue pendiente elegir
el origen de la credencial y el canal de entrada confiable. El núcleo ya
publicado `supervisor/rs3_audit_log.py` solo guarda eventos documentales con
referencias y digests, y rechaza eventos que pretendan confirmación humana.
Su cadena de hashes detecta inconsistencias de bytes,
pero no autentica al escritor ni protege frente al mismo UID. Tampoco detecta
la pérdida de registros finales completos sin un anclaje externo. Comprobar una
contraseña demostraría uso de la credencial, no identidad física absoluta. D03 sigue abierta
para decidir qué confirmaciones necesitarían un mecanismo futuro. No se crean
aquí cuentas, claves, servicios ni recibos de autoridad, y ninguna salida RS3
actual adquiere autoridad por este ADR.

## Condiciones observables antes de habilitar un gate real

En el hardware objetivo se debe comprobar el UID efectivo distinto de ambos
procesos, la imposibilidad del agente de elevarse a la cuenta de autoridad,
la propiedad y accesibilidad efectiva de la clave, la imposibilidad de escribir
el registro desde el agente y el procedimiento de recuperación/revocación.
También deben probarse operaciones negativas desde el contexto exacto de Pi y
Codex, con resultados y configuración ligados al snapshot. Un UID distinto o
un modo de archivo por sí solos no prueban aislamiento: sudo, pertenencia a
grupos, capacidades del proceso o control administrativo del host pueden
invalidarlo. En WSL, el administrador de Windows y el host siguen dentro del
ámbito de confianza; esta decisión no demuestra aislamiento frente a ellos.

Si falta una comprobación, falla una operación negativa, o el agente puede
obtener privilegios equivalentes, el gate permanece
`SECURITY_BOUNDARY_UNMET`. La entrevista y los análisis documentales pueden
continuar con `authority_verification=NOT_PERFORMED`; no se admiten recibos
humanos verificables ni operaciones autorizadas hasta resolver D03 y el
mecanismo de autenticación futuro,
implementar el servicio y validar la frontera en el equipo objetivo.
