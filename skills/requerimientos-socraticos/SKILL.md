---
name: requerimientos-socraticos
description: "Trigger: requerimientos socraticos, interrogatorio, PRD, EARS, FSM. Arquitecto científico senior: pregunta, contrasta y propone mejoras verificables."
license: Apache-2.0
metadata:
  author: "workspace-user"
  version: "2.4.6"
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

0. Al activar, ejecuta `gentle-ai requirements activate` desde el workspace autorizado. Lee el JSON de [preflight](references/activation-preflight.md); desconocidos críticos bloquean workers, no la entrevista. Un informe guardado no autoriza ejecución: las entradas públicas reevalúan los límites en vivo.
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

Ejecuta el [preflight de activación](references/activation-preflight.md) al cargar
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
