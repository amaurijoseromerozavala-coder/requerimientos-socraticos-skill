# RS3-WU-AUTHORITY-BOUNDARY-001

## Decisión humana

El maintainer escogió para RS3-D05 una **cuenta local separada** como sede
objetivo del servicio y las claves de confirmación humana. Pi/Codex podrán
presentar propuestas y verificar recibos públicos, pero no leer secretos,
modificar el registro de autoridad ni emitir confirmaciones humanas. RS3-D04
(método de autenticación) y D03 (cuándo exigirlo) siguen abiertas.

## Alcance y falsadores

Esta WU registra un contrato de arquitectura y una política fail-closed. No
crea usuarios en el host cloud, no instala un servicio de autenticación y no
declara que el aislamiento se haya probado en el i3/WSL del propietario.

- El registro estructurado debe fijar `SEPARATE_LOCAL_ACCOUNT`, permisos
  negativos de Pi/Codex, y `runtime_enforcement=NOT_IMPLEMENTED`.
- Una variante que conceda al agente lectura de clave, escritura del almacén o
  emisión de `HUMAN_CONFIRMED` debe fallar el control documental.
- El diseño debe exigir verificación de UID distinto, acceso efectivo, ausencia
  de elevación del agente, propiedad/permisos de clave y estado de recuperación;
  UID distinto por sí solo no basta.
- Ante cualquier comprobación necesaria ausente o adversa, el gate real se
  mantiene `SECURITY_BOUNDARY_UNMET`; el análisis documental puede continuar.

## Proceso

ODD → RED documental → registro y ADR → GREEN/regresiones → RDD del candidato
exacto → respaldo normal. D04/D03 no se anticipan ni se inventan credenciales.
