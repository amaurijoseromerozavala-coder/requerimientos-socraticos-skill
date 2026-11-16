# ADR-005 — Guardián bajo una cuenta Windows distinta

Estado: diseño ratificado; frontera material `NOT_ESTABLISHED`.

## Decisión y motivo

El agente Pi/Codex se iniciará en WSL desde una cuenta Windows estándar y
restringida. El guardián y la interfaz humana operarán bajo otra cuenta
Windows, con SID distinto. Estas son cuentas Windows distintas. Dos UID Linux dentro de WSL del mismo usuario
Windows no constituyen por sí solos la frontera D05. La distribución
`rs3-agent` ya preparada es evidencia de controles Linux, pero aún no acredita
esta topología ni autoriza ejecutar decisiones reales.

## Flujo mínimo

1. El agente puede depositar una propuesta tipada en una bandeja acotada; no
   escribe el almacén privado ni controla la UI del guardián. Un enlace de un
   solo uso localiza una solicitud; no autentica persona ni decisión.
2. El guardián, desde su sesión Windows, valida y congela los bytes de la
   propuesta, recalcula el desafío y presenta pregunta, opciones, identidad
   de la decisión y snapshot en su propia UI. Rechaza enlaces o datos que no
   concuerdan con la solicitud congelada.
3. Una **respuesta personalizada** retorna al interrogatorio como propuesta;
   no solicita ni consume códigos impresos ni crea un recibo de autoridad.
4. Para cada confirmación, el humano introduce en la UI confiable un código
   impreso de un solo uso. El guardián verifica y consume el código de forma
   duradera; ante resultado incierto bloquea su reutilización. Emite un
   **recibo firmado** ligado a la decisión exacta, presentación, categoría,
   opción, nonce, política y snapshot. El hash o commit Git identifica bytes,
   pero no autentica al humano ni al guardián.
5. Solo un ejecutor protegido, fuera de las credenciales del agente, puede
   realizar una operación autorizada tras verificar recibo, vigencia y
   revocación. Aceptación semántica y permiso operativo tienen gates distintos.

El guardián custodia códigos, verificadores, clave de recibos y registro
privado bajo ACL de su SID; la protección de clave podrá usar DPAPI del usuario
guardián. La bandeja entre cuentas y la UI deberán ensayarse con controles
negativos antes de escoger mecanismo concreto. No se requiere un servicio
residente ni acceso a Google/Telegram para el flujo básico.

## Falsadores materiales y límite

Bloquear si el agente puede obtener token administrativo, leer códigos o clave,
alterar recibos o almacén, sustituir la UI, ejecutar una operación protegida,
reutilizar código, o si ambos procesos comparten SID Windows. Probar además
revocación, reinicio, pérdida de recibo y estado de consumo incierto. No basta
una prueba de UID/GID, `sudo` o permisos Linux. La cuenta Windows del agente
debe poder iniciar WSL sin acceso al perfil privado del guardián; esto sigue
`NOT_RUN`.

No se crearon cuentas Windows, claves reales, códigos ni UI en esta unidad.
Hasta superar esas pruebas en el equipo objetivo: D05 `NOT_ESTABLISHED`,
`SECURITY_BOUNDARY_UNMET`, `execution_authorized=false`. La confirmación desde
un teléfono, sin sesión independiente del guardián, permanece pendiente.
