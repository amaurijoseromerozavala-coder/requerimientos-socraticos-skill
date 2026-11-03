# WU-RS3-PBKDF2-AUDITOR-003

## Origen y alcance

El maintainer eligió PBKDF2 como origen de la credencial para D04. Implementar
un núcleo local que compruebe una contraseña propia, vincule cada comprobación
a una decisión y conserve solo el resultado auditable. Esta unidad no crea la
cuenta local D05 ni una interfaz confiable de entrada humana; por tanto no
emite `HUMAN_CONFIRMED` ni habilita despliegue.

## Contrato

- Alta única en almacén privado: sal aleatoria, PBKDF2-HMAC-SHA256 con coste
  fijo y comparación de tiempo constante. No persistir la contraseña.
- Comprobación sobre contenido legible acotado y snapshot identificado; digest
  calculado desde los bytes recibidos, no desde un hash declarado por el agente.
- Cada intento usa un nonce único y produce antes de responder un evento
  `PASSWORD_CHECK_ACCEPTED` o `PASSWORD_CHECK_REJECTED` sin texto ni secreto.
- Contraseña incorrecta, nonce reutilizado, registro no escribible, almacén
  incompleto o permisos inseguros cierran el paso sin confirmación.
- Salida siempre `authority_verification=NOT_ESTABLISHED` y
  `execution_authorized=false` hasta verificar D05 en el hardware objetivo.
  Un acierto demuestra coincidencia de credencial, no identidad física.
- Almacén acotado, sin recuperación automática ni declaración de integridad
  frente a quien controle la cuenta. Un registro lleno bloquea el intento.

## Oráculos TDD

1. RED: alta y acierto/fallo PBKDF2 vinculados al contenido, sin secreto en log.
2. RED: nonce reutilizado, entrada alterada y almacén no privado rechazados.
3. GREEN y regresiones afectadas; revisión RDD del candidato exacto.
4. Solo después de RDD aprobado/reconocido: commit y respaldo remoto.

## Estado

RED observado: el test dirigido falló por módulo ausente. GREEN dirigido:
14 pruebas del verificador y registro; regresiones: 111 de supervisor, 314 de
requisitos, 45 de CI. La entrada humana confiable y la separación D05 son
unidades posteriores. No usar contraseña real bajo el UID del agente. RDD
pendiente.
