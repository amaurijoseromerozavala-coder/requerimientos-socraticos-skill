# WU-RS3-MANUAL-PASSWORD-CHANNEL-004

## Origen y alcance

El maintainer requiere que el backend compruebe que una contraseña se introdujo
para una decisión. PBKDF2 fue elegido y el núcleo ya existe. Esta unidad agrega
una entrada manual por terminal local, sin admitir secretos por argumento,
stdin o variable de entorno. No configura la cuenta separada D05 ni habilita
`HUMAN_CONFIRMED`.

## Contrato

- Leer un archivo de decisión regular, sin symlink, con límite estricto y JSON
  de esquema cerrado; conservar en memoria los mismos bytes para mostrar y
  comprobar, sin releer después de la revisión humana.
- Mostrar en el terminal directo el contenido y el snapshot. Pedir la
  contraseña por `/dev/tty` con eco deshabilitado; restaurar el estado del
  terminal al terminar. Sin terminal directo, bloquear.
- Generar un nonce nuevo por intento en el proceso del backend. Solo el núcleo
  PBKDF2 decide coincidencia y registra el intento antes de devolver resultado.
- El resultado mantiene `authority_verification=NOT_ESTABLISHED` y
  `execution_authorized=false`; contraseña acertada no equivale a identidad
  física ni permiso operativo. Una cuenta accesible al agente invalida el uso
  con contraseña real.

## Oráculos TDD

1. RED: JSON inválido, duplicado, symlink, tamaño excesivo o ausencia de TTY
   bloquean antes de cualquier comprobación.
2. RED: entrada por terminal falsa de prueba sintética llega al núcleo,
   vinculada a la decisión mostrada; stdout no revela contraseña.
3. GREEN, regresiones afectadas y RDD del candidato exacto.
4. Tras revisión reconocida: commit y push normal; el i3/WSL permanece NOT_RUN.

## Estado

RED observado: falta del adaptador. GREEN inicial: 4 pruebas, incluida entrada
en pseudo terminal sin eco y restauración del modo.
El RDD inicial señaló que la comparación de contraseñas Unicode lanzaba
`TypeError`; RED dirigido reproducido. Se corrigió comparando bytes UTF-8.
GREEN corregido: 5 pruebas dirigidas; regresiones 116 de supervisor, 314 de
requisitos y 45 de CI. Validación RDD del candidato corregido pendiente.
