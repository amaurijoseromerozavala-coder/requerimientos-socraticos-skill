# WU-RS3-PROVIDER-TRACEABILITY-009

## Objetivo y precedencia

Actualizar la matriz RS3 tras WU-RS3-LOCAL-PROVIDER-ADAPTER-008,
revisada y respaldada en `43d6859b81004fb8e3d19e996b05284ae6805c29`.
Requiere el ZIP RS3 identificado y el recibo RDD existente.

## Alcance

Actualizar el HEAD observado y agregar una evidencia **parcial** para
RS3-REQ-070 y RS3-REQ-080, con pistas a código y tests reales. Ajustar el
conteo del resumen a la matriz. No adoptar propuestas del ZIP, probar
proveedores cloud, alterar autoridad o cambiar código de producto.

## Oráculos TDD

RED: HEAD anterior y falta de evento/enlaces del adaptador. GREEN: 107/50/52
IDs intactos; todos los requisitos NOT_VERIFIED_PER_REQUIREMENT; 52 casos
NOT_RUN_AS_PACKAGE_CASE; rutas y recibo existentes; resumen con conteos
derivados de matriz; reproducción byte a byte desde el ZIP identificado.

RDD del candidato exacto y respaldo Git solo tras reconocimiento. La revisión
estática y los tests locales con proveedor simulado no acreditan hardware
objetivo, proveedor externo ni producción.

RED observado: dos tests fallaron por HEAD anterior y evento 008 ausente.
GREEN observado: diez tests focalizados con el ZIP identificado y 55 tests CI
locales pasaron; uno de CI quedó omitido explícitamente por falta de ese ZIP.
La segunda generación de la matriz fue idéntica byte a byte: SHA-256
`c0545d3da8ca5fea18149b36748cc8967afd771bd712368c619814be34da085f`.
