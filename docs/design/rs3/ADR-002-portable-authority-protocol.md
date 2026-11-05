# ADR-002 — Protocolo de autoridad portable, con fronteras verificadas por entorno

**Estado:** protocolo propuesto; el perfil de códigos impresos fue ratificado
posteriormente como objetivo D03, sin habilitar autoridad. D05 se conserva.
El [contrato estructurado](authority-portability-contract.json) permanece en
`PROPOSED_DESIGN_NOT_ENFORCED`. En el equipo objetivo no se ha probado ninguna
frontera. La persona está usando el teléfono, por lo que no se le exigen ahora
comandos en su PC.

## Decisión arquitectónica propuesta

La parte portable es un **protocolo de confirmación**, no una contraseña o un
dispositivo universal. El agente solo propone una decisión. Un emisor ajeno a
su control crea un desafío que vincula versión de protocolo, categoría D03,
digest de propuesta, digest de snapshot, digest del manifiesto de presentación,
digest de los bytes canónicos de la decisión, nonce, audiencia, digest de
política y vencimiento. El verificador
comprueba todos esos campos juntos, consume el nonce de forma atómica y emite
un recibo autenticado verificable por un componente independiente del agente.
Una alteración de cualquiera de esos campos exige otro desafío y otro recibo.
Definir y probar la codificación canónica, el formato del recibo, el reloj y el
almacén de consumo es trabajo posterior; un SHA-256 aislado solo identifica
bytes y no autentica a nadie.

La aceptación del significado de un requisito y la autorización de ejecutar
una operación son eventos distintos, con categoría, política y recibo propios.
D03 exige una comprobación nueva para **cada** aceptación semántica, excepción
aceptada o autorización operativa. No hay confirmación por silencio ni una
autenticación reutilizable durante toda la sesión. D05 eligió una cuenta local
separada como sede de autoridad en el perfil Linux/WSL; esa elección se conserva.
Los códigos impresos son ahora el perfil objetivo; PBKDF2 permanece como
componente previo no autoritativo. La implementación actual de PBKDF2
registra coincidencias sintéticas pero no prueba la separación ni puede emitir
`HUMAN_CONFIRMED`. Un entorno que no pueda demostrar una frontera fuera del
alcance del agente queda en `SECURITY_BOUNDARY_UNMET`.

## Adaptadores y consecuencias

| Perfil | Ventaja | Riesgo y requisito para considerarlo |
|---|---|---|
| Cuenta local separada + PBKDF2 | Componente previo, sin red | Ya no es el mecanismo objetivo; sus pruebas no habilitan D03/D05. |
| TOTP en teléfono | No requiere que el usuario esté frente al PC y suele funcionar sin red | El reloj, la semilla y el verificador deben estar fuera del agente; un código copiable no demuestra por sí solo qué decisión se aprobó, y exige anti-replay y rate limit. No adoptado. |
| Tarjeta de coordenadas impresa | Perfil objetivo sin red ni reloj para el código | Exige códigos aleatorios de alta entropía, custodia privada, consumo único, recuperación y recibo auténtico. Ratificado como diseño; no implementado. |
| Autenticador de plataforma con desafío | Puede proteger una clave privada en un dispositivo compatible y ligar un desafío | Depende de capacidades y origen/audiencia verificados; no es universal ni está integrado. No adoptado. |

El teléfono puede ser interfaz de preguntas y respuestas ahora, pero su canal
de chat no se trata como autenticación. Ningún adaptador queda aprobado solo
porque una prueba documental pasa. Tampoco se presume que TOTP o una tarjeta
resuelvan la separación del almacén de autoridad respecto del agente.

## Falsadores y condiciones de promoción

Para cada perfil, probar en el entorno real: agente intenta leer el secreto,
escribir el almacén, emitir un recibo, controlar la entrada humana y elevar
privilegios; alterar categoría, propuesta, snapshot, decisión, audiencia o
política; reutilizar nonce; retrasar o perder reloj; revocar y recuperar. Un
éxito en cualquiera de los intentos prohibidos bloquea el perfil. Salida
malformada, adaptador desconocido, observación incompleta o limpieza incierta
también bloquean. Los tests sintéticos prueban el contrato, no la frontera
material. No se registrarán credenciales reales ni se habilitará producción a
partir de esta propuesta.
