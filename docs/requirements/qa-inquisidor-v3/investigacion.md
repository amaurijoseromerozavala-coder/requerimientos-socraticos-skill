# Investigación de este ciclo

Fecha: 2026-10-29. Requerimientos2.4.6 y su protocolo fueron leídos antes de
formalizar. Registro local Gentle `.atl/skill-registry.md`: requerimientos al
inicio, requerimientos y QA después del refresh real. No hay índice `.codegraph`;
se omitió CodeGraph conforme a AGENTS.md, sin indexar automáticamente.

Descubrimiento ALL_TOOLS: no MCP directo Engram/CodeGraph/Context7 disponible.
Engram se consultó mediante su transporte MCP local real, resolviendo primero
el proyecto `replica-gentle-ai`; búsqueda devolvió historial QA y endurecimiento.
La autoridad actual procede de archivos/decisiones contrastados, no de previews
de memoria. No fue necesario consultar una API de librería nueva: se reutilizan
Python/jsonschema y los lectores acotados existentes. Context7 no se invocó.

Web: búsqueda `site.nasa.gov systems engineering handbook requirements
verification validation traceability matrix`, luego lectura de fuentes primarias:

- [NASA, matriz de verificación](https://www.nasa.gov/reference/appendix-d-requirements-verification-matrix/): identificadores y vínculo a fuente para cada requisito.
- [NASA, gestión de requisitos](https://www.nasa.gov/reference/6-2-requirements-management/): trazabilidad bidireccional y control de cambios de baseline.

Se aplican como guía para decisiones de diseño, no como certificación NASA o
DO-178C. Recibos reales de búsqueda/apertura: `receipts/web-search.json` y
`receipts/web-open.json`. Una llamada inicial con parámetro incorrecto devolvió
isError y no se contó como investigación exitosa; la consulta válida se conservó.

Checkland: transformación de revisión parcial/opinión a evaluación trazable;
beneficiario y dueño humano, actores skill/coordinador/revisor, límites de
autoridad/recursos/entorno. Kendall: fuentes→entradas→decisiones→informes y casos.
Bunge/Popper: hipótesis y falsadores previos, controles negativos, contraste real
y corrección de tres fallos detectados por revisión independiente. Ninguna de
estas metodologías sustituye un resultado ejecutado o confirma intención por sí sola.
