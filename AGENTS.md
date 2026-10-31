<!-- project:mandatory-platform-and-hardware-policy -->
## Regla dura: normas y protección de infraestructura

Por instrucción expresa del usuario, no ejecutar acciones que violen las normas
aplicables de OpenAI, las licencias o condiciones de uso del software de terceros,
ni las normas de plataformas de terceros. No poner en riesgo hardware o
infraestructura de terceros, incluidos hosts cloud, runners y servicios compartidos.

Esta regla se aplica a comandos, herramientas, MCP, skills, agentes, automatizaciones
y pruebas. Una finalidad de QA, falsación o estrés no exime del cumplimiento de
normas ni autoriza poner en riesgo infraestructura de terceros. Esta regla no
prohíbe pruebas de estrés en infraestructura propia o expresamente autorizada,
cuando sean conformes y cuenten con límites, observación y condiciones de parada.
La ausencia de acceso al equipo objetivo se registra como NOT_RUN, nunca PASS.
Antes de una operación con impacto relevante, comprobar su alcance, condiciones
aplicables y límites de recursos. Si el cumplimiento o el impacto seguro no están
establecidos, no ejecutarla: registrar el bloqueo y buscar una alternativa conforme.
No intentar eludir restricciones técnicas, cuotas ni controles de las plataformas.
La autorización del usuario no convierte una infracción en una acción permitida.

CI permanece diferido y producción bloqueada. El humano reanudó la construcción
local de QA Inquisidor el 2026-10-29; análisis por defecto y ensayos de aplicación
solo con autorización específica suficiente. Esta autorización no habilita CI,
producción ni pruebas físicas del equipo inaccesible.
<!-- /project:mandatory-platform-and-hardware-policy -->

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->

<!-- requerimientos-socraticos:registry -->
## Available custom skill

- `requerimientos-socraticos`: natural-language requirements → EARS, explicit logic, FSM, falsification, hardened JSON PRD; documents only. Read `/workspace/replica-gentle-ai/skills/requerimientos-socraticos/SKILL.md` when requested.
- `qa-inquisidor` (0.1.3-alpha): revisión de calidad del sistema completo, análisis por defecto y comprobador local de consistencia documental. Read `/workspace/replica-gentle-ai/skills/qa-inquisidor/SKILL.md` when requested. No certifica verdad semántica, producción ni comportamiento físico.

<!-- project:response-and-cloud-compliance -->
## Comunicación y operaciones cloud

Aplicar [pautas documentadas](docs/compliance/openai-codex-cloud.md).
Centrar respuestas en diagnóstico, evidencia y corrección autorizada; separar
hechos, hipótesis y propuestas. No atribuir causas internas a avisos de plataforma.
No intentar evitar controles mediante cambios de palabras ni otros mecanismos.
El lenguaje neutral solicitado no sustituye la evaluación del contenido y acción.
Ensayos autorizados solo dentro de alcance y límites seguros establecidos, con
parada y limpieza; no saturar infraestructura compartida. Autorización de ensayos
no implica CI, instalación de QA ni producción. No exponer credenciales.
<!-- /project:response-and-cloud-compliance -->
