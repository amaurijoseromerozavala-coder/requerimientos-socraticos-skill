# ADR-004 — Códigos impresos y recibos ligados a cada decisión

**Estado:** mecanismo objetivo decidido por el maintainer; contrato documental.
`runtime_enforcement=NOT_IMPLEMENTED`, `authority_verification=NOT_ESTABLISHED`,
`real_authority_gate=SECURITY_BOUNDARY_UNMET` y `execution_authorized=false`.

## Decisión y precedencia

Se sustituye el verificador PBKDF2 de D04 como mecanismo objetivo de
confirmación por una tarjeta impresa de códigos aleatorios de un solo uso.
D03 conserva **una verificación nueva para cada confirmación**: aceptación
semántica, aceptación de excepción y autorización de operación son categorías
separadas. D05 conserva el guardián bajo una cuenta local separada del agente.
El módulo PBKDF2 existente permanece como componente histórico sin autoridad;
no se ejecuta en paralelo como ruta alternativa de confirmación.

Una respuesta personalizada sigue siendo material de entrevista: no solicita
ni consume código, ni escribe en el Git de autoridad. Su interpretación crea
una propuesta nueva que debe presentarse otra vez. No se infiere aceptación
del silencio ni de mensajes del agente.

## Contrato del desafío y recibo

El guardián, fuera del alcance del agente, crea un desafío con codificación
canónica versionada que vincula categoría, digest de propuesta, digest de
snapshot, digest del manifiesto de presentación (pregunta completa, opciones
ordenadas y versión UI), identificador estable y digest tipado de la opción
seleccionada, digest de la decisión exacta, nonce, audiencia,
digest de política y expiración. También designa tarjeta y coordenada; el
código secreto nunca aparece en el enlace, desafío público, recibo, Git ni
logs del agente. El humano ve la selección completa y su identidad antes de
introducir el código por una interfaz cuyo origen y control deberán probarse.
Dos opciones con texto idéntico y distintos identificadores deben producir
desafíos y recibos distintos. La codificación del digest de opción debe incluir
su ID, texto y tipo, no solo el texto visible.

El guardián verifica el código contra su almacén privado, bajo un bloqueo de
consumo único, y registra el intento. Un código correcto no basta si cualquiera
de los campos del desafío difiere, expiró, fue revocado o ya se gastó. El
recibo debe referenciar la identidad completa del desafío, tarjeta,
coordenada y decisión; no revelar el código. La admisión solo se produce tras
verificar tanto el consumo duradero como un recibo auténtico del guardián.
Un commit Git por sí solo identifica una transición de repositorio, no autentica
al escritor ni demuestra percepción humana. La forma de autenticación del
recibo aún requiere especificación y pruebas.

La unidad WU-034 implementó **solo** la identidad propuesta de presentación,
opción y desafío. Usa JSON ASCII con claves ordenadas y separadores compactos,
sin normalización Unicode, precedido por dominio v1 y salto de línea para cada
SHA-256. Rechaza campos desconocidos, IDs de opción duplicados y controles de
texto, con cotas de tamaño. El guardián todavía debe calcular y verificar por
sí mismo esos bytes desde la fuente autorizada; el agente no puede entregar un
digest arbitrario como prueba. La codificación y autenticación del recibo,
el almacenamiento y consumo de códigos siguen pendientes.

WU-035 añadió un registro POSIX **sin códigos** que conserva
`AVAILABLE → PENDING → SPENT` bajo bloqueo y fsync. `PENDING` sobrevive al
reinicio; una etapa de escritura incompleta bloquea hasta reconciliar el
archivo principal, y reconciliar nunca libera una coordenada pendiente.
El registro acepta un digest propuesto, no comprueba que provenga del guardián;
su resultado sigue sin autoridad. Verificación del código, consumo auténtico,
recibo, separación D05 y pruebas en el equipo objetivo siguen pendientes.

WU-036 añadió un **verificador sintético no autoritativo** al registro local.
Provisiona hashes SHA-256 con sal por coordenada en un archivo privado y solo
compara un código para una reserva PENDING con digest de desafío coincidente.
Un intento correcto, incorrecto o malformado gasta la coordenada antes de
devolver el resultado; una etapa incierta bloquea. El aprovisionamiento rechaza
códigos duplicados y mantiene un marcador bloqueante hasta sincronizar el
archivo y el directorio. Una falla en esa sincronización deja la provisión
sin confirmar y exige reconciliación fuera de esta unidad. Si se pierde el
borrado del marcador tras un reinicio, este reaparece y bloquea la
disponibilidad; no se infiere que el aprovisionamiento terminó. Este hash es un verificador
de prueba: ni la longitud del código demuestra entropía, ni la sal mitiga por
sí sola códigos débiles. El mismo UID todavía controla almacén y proceso;
faltan emisión/custodia independiente, autenticación del desafío, recibo y la
frontera D05. Por ello, incluso `code_match=true` no confirma al humano ni
autoriza una operación.

WU-037 enlazó la propuesta completa del desafío con la reserva y la
comparación sintéticas. Recalcula la identidad desde la pregunta, opciones,
selección y metadatos, y comprueba que exista un verificador íntegro antes
de reservar. Un digest libre no es entrada de esta ruta. La comprobación de
verificador y la reserva aún son operaciones separadas: un actor del mismo
UID puede modificar el almacén entre ambas, dejar PENDING sin disponibilidad
de verificación y obligar a reconciliar. La lectura final bloquea el acierto
si falta el verificador; no demuestra procedencia humana, tiempo vigente,
custodia independiente ni autorización.

El almacén privado y Git no forman automáticamente una transacción atómica.
Ante caída entre consumo y commit, escritura parcial, pérdida de fsync o
incertidumbre de estado, el guardián bloquea la admisión y reconcilia antes
de cualquier reintento. Nunca reutiliza el mismo código para resolver una
transacción incierta. El recibo público no habilita una operación sin un gate
independiente que compruebe autoridad, categoría, vigencia y revocación.

## Límites materiales y decisiones de implementación pendientes

Cada código debe provenir de un generador criptográfico y aportar al menos
128 bits de entropía. El formato legible, número de códigos, proceso de
impresión, entrega, pérdida, reemplazo y revocación de tarjetas quedan
pendientes. No se crean códigos reales en esta unidad. El guardián debe limitar
intentos y evitar que el agente lea el verificador de códigos o escriba el
registro. La separación UID, elevación, control del terminal/navegador y
recuperación deben ensayarse en el entorno objetivo. Una UI o captura de
pantalla no demuestra que el humano leyó la decisión.

## Falsadores antes de habilitar autoridad

1. Alterar pregunta, orden de opciones, ID de opción elegida, snapshot, categoría,
   audiencia o política y obtener el recibo anterior: rechazo obligatorio.
   Esto incluye dos opciones de igual texto con identificadores distintos.
2. Presentar dos veces el mismo código o nonce, incluso concurrentemente:
   como máximo una admisión; estado incierto bloquea ambas hasta reconciliar.
3. Cortar el proceso entre consumo y commit y obtener éxito o reutilización:
   rechazo obligatorio.
4. Proponer respuesta personalizada y observar consumo o commit: rechazo.
5. Desde la cuenta real del agente, leer códigos/verificador, emitir recibo,
   alterar la UI o elevarse a la cuenta de autoridad: frontera D05 fallida.
6. Verificar el recibo sin anclaje independiente del guardián o aceptar un
   commit fabricado por el agente: rechazo.

El análisis de contrato y los tests sintéticos pueden avanzar. La autoridad
real y producción siguen bloqueadas hasta implementar y falsar esta frontera.
