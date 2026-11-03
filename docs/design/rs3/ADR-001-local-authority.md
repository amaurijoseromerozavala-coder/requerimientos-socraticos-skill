# ADR-001 — Autoridad RS3 en cuenta local separada

**Estado:** decisión de arquitectura D05 confirmada por el maintainer;
implementación y comprobación material pendientes. El [registro estructurado](authority-boundary-decision.json)
mantiene `runtime_enforcement=NOT_IMPLEMENTED`, `human_confirmation_enabled=false`
y `real_authority_gate=SECURITY_BOUNDARY_UNMET`.

La guarda local de UID exige al dar de alta el UID declarado del agente, lo
rechaza si coincide con la cuenta actual y fija ambos UID en el verificador.
La comprobación posterior exige que UID real y efectivo coincidan con el UID
de autoridad guardado. Esto previene un alta accidental bajo la misma cuenta;
no prueba que el UID declarado sea realmente el de Pi/Codex ni descarta sudo,
interop WSL o control del host. El formato del verificador es v2 y rechaza
almacenes v1 sin migrarlos automáticamente.

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
contenido decidido. El origen elegido es un verificador local PBKDF2-HMAC-SHA256:
`supervisor/rs3_password_auditor.py` implementa alta única y comprobación
acotada con evento persistido antes de devolver el resultado. Solo guarda sal
y derivado; el evento contiene el digest de la decisión, nonce y resultado, sin
contraseña ni texto. Sigue pendiente un canal de entrada humana confiable y
la comprobación de D05 en el equipo objetivo. El núcleo
`supervisor/rs3_audit_log.py` guarda eventos documentales y de comprobación
con referencias y digests, y rechaza eventos que pretendan confirmación humana.
El adaptador `supervisor/rs3_password_cli.py` lee una decisión acotada una sola
vez, la muestra y pide la contraseña directamente en `/dev/tty` sin eco. Esto
elimina los argumentos y stdin como canales de contraseña; no demuestra que el
agente no controle la sesión terminal en el equipo objetivo. Hasta probar esa
frontera, su resultado conserva `authority_verification=NOT_ESTABLISHED`.
No se debe dar de alta una contraseña real en una cuenta accesible a Pi/Codex:
el agente podría leer el derivado y fabricar registros desde ese UID. Los
ensayos actuales usan únicamente contraseñas sintéticas en directorios temporales.
Su cadena de hashes detecta inconsistencias de bytes,
pero no autentica al escritor ni protege frente al mismo UID. Tampoco detecta
la pérdida de registros finales completos sin un anclaje externo. Una coincidencia
de contraseña demuestra uso de la credencial, no identidad física absoluta.
D03 sigue abierta para decidir qué confirmaciones necesitarían un mecanismo
futuro. Aquí no se crean cuentas, claves de firma, servicios ni recibos de autoridad, y ninguna salida RS3
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
