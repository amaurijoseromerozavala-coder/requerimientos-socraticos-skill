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

<!-- project:strict-workunits -->
## Unidades de trabajo: ODD, TDD y RDD obligatorios

Instrucción permanente del propietario: aplicar ODD/TDD/RDD estricto a todo el
proyecto, incluso al cambio más pequeño, y respaldar cada unidad terminada en
GitHub únicamente después de su RDD. No se requiere repetir la autorización de
publicación para cada unidad que cumpla estos gates; los consentimientos que
exija el runtime de revisión se solicitan para el candidato correspondiente.

- **WU-ODD:** antes de editar, registrar objetivo, alcance, criterios de aceptación
  y tareas en `odd/tasks/`. Mantener trazabilidad hacia la solicitud humana.
- **WU-TDD:** establecer un oráculo pertinente, ejecutar y conservar RED antes de
  corregir, observar GREEN y comprobar regresiones afectadas. Para documentos,
  usar verificaciones de contrato y controles negativos. No inventar RED, no
  sustituir evidencia semántica por conteos de tests. Si no puede ejecutarse una
  comprobación necesaria, declarar bloqueo y no cerrar la unidad.
- **WU-RDD:** revisar el candidato exacto mediante Gentle AI; conservar hallazgos,
  alcance y recibo aprobado/reconocido. RDD ausente, pendiente, rechazado o sin
  consentimiento bloquea el cierre y la publicación. Cambios posteriores en el
  candidato invalidan su aplicabilidad y requieren nueva revisión.
- **WU-BACKUP:** después del cierre RDD, verificar identidad de los archivos,
  crear commit de la unidad y sus evidencias asociadas y hacer push normal al
  repositorio autorizado. Verificar el SHA remoto y entregar enlace. Si falla el
  push, declarar respaldo pendiente. No force-push, CI, despliegue ni cambios de
  permisos por inferencia; preservar historial y excluir secretos/estado privado.
- **WU-CANDIDATE-IDENTITY:** distinguir contenido revisado de recibos y logs que
  produce la revisión/publicación. Esos registros posteriores deben apuntar al
  candidato o commit exacto, no modificar sus archivos ni presentarse como
  contenido ya revisado. Un cambio sustantivo, incluso documental, es otra unidad;
  el recibo no se usa para otorgarse aprobación a sí mismo.
- **WU-NO-SILENT-EXCEPTIONS:** ninguna excepción por tamaño, conveniencia o coste.
  No desactivar gates ni sustituir aprobación por silencio. Si un requisito del
  flujo no se puede cumplir, registrar el bloqueo y comunicarlo al propietario.

La aprobación RDD y el respaldo no acreditan calibración física, implementación
pendiente ni autorización de producción. Estas obligaciones de proceso no cambian
las políticas de revocación, presupuestos o alcance funcional ya confirmadas.
<!-- /project:strict-workunits -->
