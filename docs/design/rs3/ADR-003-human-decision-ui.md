# ADR-003 — UI de selección y retorno de respuestas personalizadas

**Estado:** diseño confirmado para la ruta de respuesta personalizada;
implementación no iniciada. El [contrato FSM](human-decision-ui-contract.json)
mantiene `authority_verification=NOT_ESTABLISHED` y
`execution_authorized=false`.

## Decisión humana confirmada

El humano puede seleccionar una opción formulada en lenguaje natural o escribir
una respuesta personalizada. La respuesta personalizada regresa al agente como
material de entrevista. Puede conservarse en el historial del interrogatorio,
pero no se registra en el Git de autoridad, no solicita ni consume código de
tarjeta y no produce recibo. El agente la interpreta como nueva propuesta; el
humano debe ver una pregunta replanteada con opciones, nuevo snapshot, nuevos
digests calculados por el guardián y nuevo enlace antes de cualquier selección
confirmable. Ninguna interpretación del agente se acepta por silencio.

Para una opción seleccionada, la UI presenta el texto completo de pregunta,
opciones y opción elegida junto con un digest visible de identificación. El
guardián, no el LLM, calcula los digests desde bytes canónicos. Solo después
de mostrar la selección exacta se solicita un código. La eventual verificación
de código, consumo único y commit Git son una transición indivisible desde la
perspectiva de admisión: ante caída o incertidumbre no se emite recibo válido.
La decisión posterior del maintainer sustituyó PBKDF2 como mecanismo objetivo
por códigos impresos y recibos ligados a la selección exacta. La tarjeta
continúa sin implementación; formato de impresión, custodia y recuperación
requieren pruebas y decisiones de operación. Véase [ADR-004](ADR-004-printed-code-authority.md).

## Origen y prueba de presentación

El guardián independiente crea el enlace de presentación. El agente solo lo
transporta y no puede elegir origen, contenido o token. El enlace sirve para
abrir una pregunta pendiente y no autoriza nada por sí mismo. Antes de crear
una UI operativa hay que fijar y probar un origen reconocible que el agente no
pueda suplantar, así como expiración y consumo de enlaces. Abrir un URL
arbitrario entregado por el agente no cumple esa condición. El modo remoto para
teléfono no está diseñado ni verificado; el prototipo local tampoco está
implementado.

QA compara un manifiesto de presentación canónica (pregunta, opciones, orden,
identidades, snapshot y versión de UI) con el recibo Git de la opción elegida.
Una captura de pantalla vinculada al manifiesto es evidencia auxiliar: su hash
protege sus bytes, pero la captura no demuestra que el navegador mostrara esos
píxeles al humano ni que este los leyera. Distintos navegadores pueden renderizar
imágenes diferentes sin alterar el texto canónico. Una discrepancia entre
contenido, opción, snapshot y recibo bloquea; ninguna similitud visual otorga
autoridad por sí sola.

## Falsadores pendientes para implementación

- Enviar respuesta personalizada y observar solicitud de código, consumo de
  coordenada o escritura en Git de autoridad: falla.
- Reusar enlace, token o código, o presentar una opción de un snapshot anterior:
  falla.
- Cambiar un byte de la pregunta, opción u orden después de generar el enlace
  y obtener recibo del snapshot anterior: falla.
- Abrir un origen suplantado o permitir que el agente altere la UI y aun así
  aceptar el recibo: falla.
- Afirmar que una imagen prueba percepción humana o que un SHA autentica al
  decisor: falla epistemológica.

Estas son obligaciones de pruebas futuras; este ADR solo fija el contrato.
