# WU-RS3-WINDOWS-SID-AUTHORITY-043

## Decisión humana y alcance

El maintainer aprobó el perfil D05: Pi/Codex en WSL iniciado por una cuenta
Windows estándar y restringida; guardián y entrada humana bajo otra cuenta
Windows. La separación de UID dentro de una distribución WSL del mismo usuario
Windows queda como defensa operativa, no como prueba de D05.

Esta unidad alinea contratos y ADR. No crea cuentas, secretos, servicios, UI,
credenciales ni recibos; no migra distribuciones ni habilita autoridad.

## Oráculos congelados antes de editar contratos

1. El perfil seleccionado exige SID Windows de agente y guardián distintos;
   dos UID WSL bajo el mismo SID no satisfacen D05.
2. El agente carece de administración Windows, credencial de publicación,
   código/verificador, clave de recibo y escritura en el registro privado.
3. El guardián congela bytes de la propuesta, recomputa desafío y muestra
   decisión y snapshot en una UI iniciada en su sesión; un enlace del agente
   solo localiza una solicitud.
4. Una respuesta personalizada vuelve a propuesta sin gastar código. Cada
   confirmación aceptada consume un código impreso y liga un recibo auténtico
   a la decisión exacta. Git/SHA sin autenticación no bastan.
5. Una operación protegida no puede ejecutarse con los permisos del agente;
   el guardián o un ejecutor separado la realiza tras un gate independiente.
6. Perfil ausente, SID iguales, canal humano no probado, recibo no autenticado,
   revocación incierta o prueba material ausente mantienen
   `SECURITY_BOUNDARY_UNMET` y `execution_authorized=false`.

## Método y límites

ODD → test documental RED contra contratos actuales → edición mínima → GREEN y
regresión → RDD del candidato exacto → respaldo Git. Las pruebas Windows reales
y la ejecución de Pi/Codex bajo el SID restringido quedan NOT_RUN. La evidencia
de UID/GID, sudo y permisos Linux del bootstrap anterior sigue siendo útil para
defensa en profundidad, sin promover D05.

La primera unidad material posterior inventariará cuentas Windows, ACL,
credenciales y viabilidad de iniciar WSL desde el SID restringido. No se
creará una cuenta hasta contar con un plan concreto y su gate aplicable.
