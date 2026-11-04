---
name: requerimientos-socraticos
description: "Trigger: requerimientos socraticos, interrogatorio, PRD, EARS, FSM. Arquitecto científico senior: pregunta, contrasta y propone mejoras verificables."
license: Apache-2.0
metadata:
  author: "workspace-user"
  version: "2.4.8"
---

## Activation Contract

Asume el rol de **arquitecto y científico del software senior**. Interroga, investiga y propone mejoras. Produce documentos, no código de producto.

## Hard Rules

- Ejecuta el [protocolo](references/interrogation.md): pregunta → respuesta real → contraste → siguiente gap. Una pregunta por intercambio; no una sola en total.
- Distingue entrevistador, asistente respondedor y humano decisor. Usa agente independiente disponible; sin transporte, declara el límite. No simules mensajes.
- Responde con evidencia o UNKNOWN. Conserva citas; no conviertas inferencias en intención humana confirmada.
- Usa MCP y skills pertinentes primero y fuentes web primarias. Registra investigación, fallbacks y propuestas conforme a [investigación](references/research-design.md).
- Propón alternativas, criterios, tradeoffs y falsadores. PROPOSED no significa aceptado.
- Valida la identidad del candidato con [objetos Git SHA-256 fijados](references/sealed-validation.md); normaliza nuevas entradas a UTF-8/LF antes de crear sus hashes, sin reescribir evidencia histórica.
- Aplica la [frontera de integridad y avance](references/integrity-boundary.md). COMPLETE cierra solo la cobertura declarada; no demuestra seguridad global ni habilita avanzar.
- Cierra por cobertura y evidencia, nunca por conteo, presupuesto o aprobación RDD. No proclames garantías universales.
- Respeta pausas; no implementes productos ni hagas commits/despliegues. Aplica [ODD/TDD/RDD](references/workflow.md); sin evidencia, no READY.

## Decision Gates

| Condición | Acción |
|---|---|
| Falta respuesta técnica | WAITING_ASSISTANT; esperar |
| Falta decisión humana | WAITING_USER; una pregunta al humano |
| Respuesta insuficiente/contradictoria | Repreguntar; no cerrar dimensión |
| Transporte o fuente necesarios ausentes | BLOCKED; declarar evidencia pendiente |
| Usuario pausa | PAUSED; conservar registro, no continuar |
| Cobertura y todos los gates comprobados | Validar cierre; READY no autoriza implementar |

## Execution Steps

0. Al activar, localiza la raíz real de esta skill e invoca `bash "<skill_root>/scripts/requirements" activate --path "<proyecto_autorizado>"`. Consulta [integración portable](references/gentle-pi.md). No asumas que el Gentle AI upstream ofrece el subcomando `requirements`; el wrapper del repositorio es opcional. Lee el JSON de [preflight](references/activation-preflight.md); desconocidos críticos bloquean workers, no la entrevista. Un informe guardado no autoriza ejecución: las entradas públicas reevalúan los límites en vivo.
1. Lee [método](references/method.md), protocolo e investigación; delimita alcance y autoridad.
2. Abre entrevista y registro Markdown; inicia el entrevistador con contexto mínimo.
3. Interroga al asistente, contrasta respuestas y escala decisiones humanas. Registra antes de continuar; entrega el registro en cada respuesta al humano.
4. Investiga y propone mejoras sin aceptarlas por silencio.
5. Compila EARS, lógica, FSM y falsadores solo desde significado confirmado. Pendientes permiten borrador, no canonicalización.
6. Ejecuta [validación](references/validation.md), conserva evidencia y revisa el candidato exacto.

## Output Contract

Entrega PRD, `interview.json`, registro Markdown, `design-proposals.json` y evidencia ligada a hashes. Valida los documentos sobre un commit completo fijado con `scripts/validate_git.py`;
las lecturas de directorios mutables son lint sin autoridad. Informa estado y pendiente; no garantiza obediencia del LLM.

## References

- [Interrogatorio y roles](references/interrogation.md)
- [Investigación y mejoras](references/research-design.md)
- [Método](references/method.md)
- [Workflow](references/workflow.md)
- [Validación](references/validation.md)
- [Schema PRD](assets/prd.schema.json)
- [Schema entrevista](assets/interview.schema.json)
- [Schema propuestas](assets/design-proposals.schema.json)

## Sondeo y análisis formal 2.4

Aplica [contrato de análisis](references/formal-analysis.md) al explorar lógica,
cobertura y viabilidad material. Delimita CESM, registra fundamentos y falsadores,
sondea solo alojamiento local autorizado y preserva UNKNOWN. El helper booleano
admite hasta32 variables totales y consultas de dominio, huecos y compatibilidad
de respuestas. No traduce intención automáticamente ni verifica implementación.
Después del análisis genera escenarios para continuar el interrogatorio real;
no convierte testigos simbólicos en ensayos ni aprueba un PRD por exit0.

El informe usa [schema](assets/analysis-report.schema.json), con ANALYSIS,
TEST PLAN y VERIFICATION en español. Sondeo no estima cobertura de hardware.
Calibración y ensayos requieren autorización suficiente, presupuesto y parada.
Lean permanece herramienta externa: sin ejecución y recibo, NOT_RUN. Conserva
los gates2.3 y la separación entre entrega, evidencia y avance bloqueado.

### Controles de ejecución 2.4.1

`analyze_logic.py` supervisa un worker separado: plazo exterior, parada y espera
antes de devolver INCONCLUSIVE al agotarlo. Linux vincula el worker directo al
padre; otras plataformas declaran ese control no soportado. No es tiempo real ni
contención universal de descendientes/kernel. JSON pasa preflight estructural96
antes de decodificar, respetando cadenas/escapes; conserva límites AST32/bytes.
El runtime predeterminado no cae a PATH si falta; una selección explícita se
resuelve o rechaza y se registra su identidad/versions sin afirmar autenticidad.
El sondeo declara host físico NOT_OBSERVED y admisión de recursos NOT_ASSESSED.

### Supervisión y correspondencia Git 2.4.2

Analizador, comandos Git y consumidor documental usan el mismo supervisor
acotado. La vía Git transmite blobs verificados por stdin sin crear archivos
candidatos ni usar leases; PRD, entrevista, diseño y recibos se resuelven en ese
proveedor. Cada lectura verifica y devuelve los mismos bytes ligados al OID;
consumed_files se contrasta con el manifiesto. Consultar sealed-validation.md.
Esto no aísla cuenta/kernel/motor ni impide paginación del SO. Se conservan0600,
CI diferido, límites documentales y BLOCKED_GLOBAL_ENFORCEMENT.

### Presupuesto de memoria Git 2.4.3

Aplica el [contrato de memoria](references/memory-budget.md): coordinador dedicado,
límites virtuales por rol antes de exec, admisión cooperativa y métricas locales
separadas de capacidad física. El perfil512MiB es provisional y configurable,
no una medida de RSS ni una cuota global. La API conserva límites de su llamador;
la CLI propia comprueba su baseline y limita su rol. Unknown/insuficiente/ocupado
bloquean; errores explícitos de memoria no se confunden con señales sin diagnóstico.
Se conservan identidad de bytes,0600, CI diferido y avance bloqueado.

### Presupuesto del analizador/Z3 2.4.4

El analizador público acepta `--memory-budget-mib` y usa un perfil lógico
provisional: CLI1/8, solver7/8 (64/448MiB para512). Se aplica RLIMIT_AS al worker
antes de exec/importarZ3 y se comparte admisión cooperativa con Git. La CLI propia
comprueba baseline y limita su rol; main() externo no reduce límites del llamador.
MemoryError observado o rechazo de recursos produce INCONCLUSIVE sin cobertura;
señales sin diagnóstico no demuestran OOM. Se conservan byte/AST, lógica y plazos.
Consultar [contrato de memoria](references/memory-budget.md); no implica cuotaRSS
ni capacidad física medida. No optimizar preflight por supuestos de tamaños no
admitidos ni ampliar permisos/CI como consecuencia de un output QA.

### Activación y admisión 2.4.5

Ejecuta el [preflight de activación](references/activation-preflight.md) mediante la entrada portable al cargar
la skill. Expone CPU/afinidad, memoria/swap, almacenamiento y alojamiento visibles,
sin identificadores únicos ni calibración física. Las entradas públicas de
análisis y Git reevalúan condiciones antes de sus workers; un informe guardado
no autoriza trabajo. El perfil automático conservador256..512MiB comprueba
headroom y hard heredado por rol, y baseline de CLI propia. Unknown crítico o
perfil no viable bloquean ejecución; la entrevista documental puede continuar.
El JSON diferencia controles prospectivos/aplicados y respeta caller API externo.
No demuestra salud térmica, presión de Windows, capacidad física ni cobertura
derivada de hardware. Se conservan0600, CI diferido y avance global bloqueado.

### Fuente única de proporciones 2.4.6

La viabilidad de cada perfil deriva de los roles definidos por las políticas de
memoria, sin una segunda tabla de fracciones. El modo all toma el máximo de cada
rol compartido entre workloads. Los presupuestos actuales no cambian; consultar
[activación](references/activation-preflight.md). Esto no añade calibración física.

### Activación portable 2.4.7

La entrada `scripts/requirements` pertenece a la skill y resuelve helpers desde su
ubicación instalada. No instala dependencias ni cambia configuración del agente.
Consulta [Gentle Pi/Shell](references/gentle-pi.md) para seleccionar intérprete y
registrar bloqueos. El preflight no envuelve ni limita todos los comandos de Shell.
Las correcciones de producto corresponden al agente de desarrollo dentro de la
autorización del usuario y sus gates; esta skill conserva su contrato documental.

### Almacenamiento y clon 2.4.8

El preflight 1.1.0 distingue `storage_admission` y `source_checkout`. El espacio
visible de WSL no mide el volumen Windows que aloja el VHD. Datos históricos del
humano no son mediciones actuales ni reserva. Si una tarea requiere ampliar
almacenamiento, indicar `--storage-required-bytes N`: mientras no exista recolector
anfitrión verificado, retorna INCONCLUSIVE y bloquea esa admisión. No emitir
consentimiento de ampliación basado solo en el guest. READY sin solicitud de disco
se limita a viabilidad provisional de roles de memoria; no autoriza escritura.

Antes de usar workers, verificar la copia fuente: repositorio clonado con origin
oficial y HEAD legible. La comprobación es local, no autentica commits ni valida
archivos sin commit. Si no se verifica, solo entrevista documental; no clonar,
resetear ni actualizar automáticamente. Conservar un clon persistente y enlazar
la skill desde él en el runtime. El sondeo no garantiza persistencia futura del
filesystem ni que otro agente ejecute obligatoriamente el protocolo.

### RS3 provisional: IR, consultas y borradores EARS

Los helpers `candidate_ir.py`, `formal_queries.py`, `witness_validation.py` y
`ears_draft.py` implementan sólo el subconjunto booleano explícito. Los
oráculos independientes viven en `tests/`. `CandidateIR` conserva estado
PROPOSED; su dirección, modalidad, fuente y contexto se comprueban antes de
ofrecer un AST. El renderer produce una frase EARS universal **propuesta**
desde ese AST, sin interpretar texto libre ni emitir autoridad. La factoría
limita las consultas a dominio, brecha, ausencia de salida y consistencia
existencial; un testigo SAT se reevalúa dentro del presupuesto antes de
presentarlo y se etiqueta como completado por el modelo, no observado.
El oráculo sintáctico solo admite cuatro patrones booleanos españoles acotados
(`solo si`, `si`, `si y solo si`, `Si…, entonces…`). Una negación,
interpretación contradictoria o frase exterior devuelve NEEDS_CLARIFICATION
sin AST ni EARS normativo. Esto no autentica el origen del texto ni su
significado humano.
La factoría ofrece además una fórmula de comparación entre dos reglas
identificadas: absoluta `XOR(F,H)` o contextual `D ∧ C_other ∧ XOR(F,H)`;
excluye las reglas comparadas de `C_other`. El llamador debe validar el modelo,
supervisar el solver y declarar el alcance. Ninguna de estas fórmulas altera la
métrica `gap` o certifica equivalencia del producto.
La CLI existente `scripts/requirements analyze <modelo.json>` acepta opcionalmente
`--compare-left ID --compare-right ID --compare-scope absolute|contextual`.
El worker supervisado distingue diferencia, equivalencia en el alcance y
contexto vacuo; UNKNOWN/timeout no se convierten en equivalencia. La salida
incluye el hash del modelo y los límites del solver como en las otras consultas.

El maintainer fijó RS3-D01: `production_ready` significa elegibilidad para
revisión documental; nunca permiso de despliegue. RS3-D02 exige todos los
requisitos aplicables con evidencia actual y ninguna brecha crítica. El helper
`documentary_eligibility.py` evalúa esas declaraciones de manera acotada:
`MODEL_ELIGIBLE` solo describe el inventario suministrado, sin autenticar su
completitud, la evidencia ni al actor. UNKNOWN, inventario incompleto y conjunto
aplicable vacío no se promueven. La autenticación y la UX de confirmación siguen
sin implementarse. D04 eligió PBKDF2: `supervisor/rs3_password_auditor.py`
comprueba una contraseña local y vincula el resultado a una decisión mediante
un log acotado. `supervisor/rs3_password_cli.py` ofrece entrada manual por
`/dev/tty`, sin contraseña en argumentos ni stdin; la independencia del canal
y D05 no están verificados.
El núcleo no está conectado a esta skill ni otorga autoridad.
No introducir una contraseña real bajo el UID de Pi/Codex mientras D05 esté
sin verificar; usar solo valores sintéticos en pruebas locales.
La guarda de UID requiere declarar la cuenta del agente al alta y rechaza
coincidencia con la cuenta actual; no acredita que la declaración sea auténtica
ni que sudo o interop WSL estén contenidos.
Ningún helper RS3 crea recibos humanos, autoriza ejecución o
sustituye la entrevista de esta skill. La versión base 2.4.8 sigue vigente;
RS3 aún no es una versión completa de producto.

RS3-D05 fija una cuenta local separada como sede futura de autoridad;
[ADR-001](../../docs/design/rs3/ADR-001-local-authority.md) exige comprobar en
el hardware objetivo UID, accesos y ausencia de elevación desde el agente.
Hasta entonces `SECURITY_BOUNDARY_UNMET`: D03, autenticación y el servicio real siguen
pendientes, sin `HUMAN_CONFIRMED` emitido por esta skill.

La entrada portable `scripts/requirements documentary-check <dossier.json>`
acepta solo un archivo regular JSON de hasta 256 KiB, rechaza claves duplicadas
y limita la profundidad antes de decodificar. `input_sha256` identifica los
bytes leídos, sin acreditar la verdad del expediente. Su exit 0 acredita únicamente que
la evaluación estructural se completó; no convierte `MODEL_ELIGIBLE` en una
decisión humana ni en autorización operativa.
