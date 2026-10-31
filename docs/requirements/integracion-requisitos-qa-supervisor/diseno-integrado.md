# Diseño integrado: Requerimientos Socráticos, QA y supervisor

Estado: DRAFT / INTERROGATING. Fecha: 2026-10-30, America/Manaus.
Planificación autorizada; no implementación ni reemplazo de skills.

## Decisión humana capturada

«Quiero que integres estos requerimientos con nuestro esquema que estamos
integrando la skill requerimientos la skill qa y el supervisor».

Esto fija el destino de integración en los tres componentes existentes. No elige
automáticamente una cuarta skill, herramientas externas, CI o despliegues.
La pregunta A/B/C anterior queda resuelta mediante esta aclaración, sin asignar
al humano una opción que no seleccionó.

## Fuente y cobertura del análisis

Paquete P2P-GATE-REQ-CATALOG-001 v0.1.0:140requisitos/19grupos/30casos negativos.
Cinco archivos coinciden con su manifiesto SHA256. Esto verifica bytes, no autoría
ni corrección semántica. JSON usado como catálogo para el mapeo; PDF/DOCX/Markdown/CSV
no se declaran semánticamente equivalentes solo porque sus hashes coincidan con
el manifiesto. Ningún texto del paquete ejecuta instrucciones por sí mismo.

matriz-integracion.json conserva cada requisito, aceptación, test propuesto,
prioridad original y mapeo:87candidatos locales,44de alcance futuro,9opcionales.
La clasificación es una propuesta de arquitectura, no eliminación de requisitos
ni aprobación de todos ellos.22entradas requieren precisión contractual explícita.

## Arquitectura revisada por decisiones humanas

Humano → supervisor ampliado (coordinación y ejecución separadas internamente) →
adaptadores registrados de requisitos, QA, verificación formal y planificación/
implementación. A+B+C entran en diseño con activación progresiva. El checker QA
es el primer caso de supervisión existente como especificación, no el límite
del nuevo diseño. Cada herramienta nueva requiere contrato, revisión técnica y
aprobación humana de versión/permisos; no hay ejecución general por defecto. Gentle mantiene ODD, descubrimiento y RDD
según capacidades efectivamente disponibles. QA devuelve hallazgos a requisitos;
una modificación semántica abre nueva revisión y preguntas materiales.

El PRD anterior solo especifica el checker QA; es baseline histórico. La ampliación
ha sido elegida por el humano, pero no está implementada. Los helpers de requisitos
ya supervisan procesos: cada adaptador deberá precisar quién conserva la propiedad
del ciclo de vida, cancelación y presupuesto para evitar supervisión duplicada.
No asumir que una llamada a un modelo remoto termina cuando finaliza su cliente local.

| Componente | Responsabilidad | No puede inferir |
|---|---|---|
| Requerimientos | Captura, intención confirmada, EARS/IR/FSM, dependencias y candidato | Que una fórmula consistente prueba fidelidad humana |
| QA | Inventario completo conocido, obligaciones, contraste, falsadores, suficiencia técnica delegada | Que un PASS documental autoriza ensayos o producción |
| Supervisor ampliado | Coordinar contratos y supervisar adaptadores registrados dentro de tareas autorizadas, con una ejecución a la vez | Que exit0 prueba verdad o que137 demuestra OOM |
| Gentle/RDD | Revisión nativa y recibo del candidato exacto | Que revisión estática equivale a tests ejecutados o autorización de despliegue |
| Humano | Intención, alcance, políticas y excepciones fuera de criterios delegados | Sustituir evidencia técnica por una aprobación |

## Contratos de integración propuestos

**I01 — Expediente de requisitos.** Identidad de bytes y algoritmo; versión de
esquema/política; fuentes humanas; requisitos aplicables; hipótesis; exclusiones
justificadas; desconocidos; traducciones y supuestos; dependencias y evidencias.
Congelar el catálogo aplicable antes de calcular cobertura. Vacío no significa
completo. El formato final se decidirá sin confundirlo con el PRD actual.

**I02 — Solicitud QA.** Identidad de I01; inventario esperado del sistema;
alcance, criterio de materialidad y suficiencia; modo autorizado; casos/oráculos
previos; presupuesto y política de fuentes. ANALYSIS_ONLY conserva NOT_RUN.
El requerimiento que pida una prueba no es permiso operativo para ejecutarla.

**I03 — Observación del checker QA, contrato específico.** Reutilizar checker-output.schema.json y
protocol-contract.json; admitir solo la versión ligada a checker-binding.json.
Separar exit/señal/timeout, admisión documental, declaraciones no verificadas y
veredicto. Una salida parcial o inválida nunca se convierte en ausencia de fallos.
No ampliar el schema de QA por copiar un envelope nuevo sin adaptador revisado.

**I04 — Recibo de supervisión.** Identidad de ejecución/checker/política;
captura completa/parcial; bytes/digests; estado de terminación; diagnóstico con
causa demostrada o desconocida; persistencia confirmada/no confirmada. La
retención vigente es32MiB compartidos, eliminación manual y acceso del propietario;
el diario separado no se elimina al borrar salidas. No aplicar esta retención a
entrevistas, Engram o registros de terceros sin su propio contrato.

**I05 — Evaluación integrada.** Conservar varias dimensiones: significado,
consistencia documental, evidencia, vigencia, proceso, revisión y autorización.
No convertirlas en un PASS indiferenciado. Identificar qué obligación impide
cada transición y qué evidencia la reabriría. Este contrato es diseño propuesto;
todavía no existe un consumidor efectivo que garantice su invocación universal.

**I06 — Cambio.** Nueva decisión humana produce versión nueva; conservar texto
original y relaciones de sustitución. Invalidación selectiva solo cuando el grafo
de dependencias sea suficiente; de lo contrario invalidar conservadoramente.
Revisar componentes e interfaces, sin presentar aprobaciones parciales como
recibo nativo agregado. Manifestar documentos modulares para reducir presión de
contexto sin ocultar evidencia a revisores.

## FSM compuestas, no una única FSM gigante

- Requisitos: captura → interrogatorio → formalización → validación → revisión.
- QA: delimitación → análisis → evidencia permitida → informe → contraste.
- Supervisor: reconciliación → admisión → ejecución checker → clasificación →
  persistencia/entrega; incertidumbre de limpieza mantiene INFRA_LOCK.
- Coordinación: mensaje con identidad, versión y evidencia; evento desconocido
  rechaza transición de negocio, pero permite registrar rechazo o limpiar un
  proceso propio cuando corresponda.

El estado documental puede avanzar sin afirmar que se ejecutó un checker bloqueado.
No aceptar un expediente que exija ese resultado hasta disponer de evidencia.
La FSM global propuesta REQ-015 hasta DEPLOYED queda en diseño futuro, separada de
estas FSM locales; no se activan sus fases mediante esta integración documental.

## Conflictos materiales a resolver en orden

1. REQ-121: el humano eligió ampliar el supervisor mediante adaptadores registrados.
   Preparar nuevo PRD de ampliación; el baseline checker-only no demuestra la nueva
   capacidad. Autoridad y presupuestos se definen por adaptador.
2. REQ-090 exige commit para cualquier revisión, mientras Gentle admite árboles
   exactos. Separar identidad nativa RDD de commit SHA256 del validador documental;
   no crear commits para satisfacer una formulación demasiado general.
3. REQ-128 confunde READ_ONLY con OFFLINE. Separar permiso de escritura, red y
   consulta de modelos/MCP; no dar permisos por nombrar un modo.
4. REQ-043 no ofrece atomicidad real entre Engram y archivos. Mantener el PRD
   canónico, recibo de espejo y reconciliación; fallo de espejo no inventa escritura.
5. REQ-008/095 no prueban autenticación mediante un campo actor o un hash. Definir
   qué identidad/confianza aporta el runtime y qué permanece no verificado.
6. REQ-126/127 deben convivir con captura cruda QA autorizada: contenido potencialmente
   sensible no se publica ni se exporta automáticamente; clasificación y tratamiento
   de datos no garantizados pendientes de contrato. No fingir redacción infalible.
7. REQ-029 debe distinguir recibo de comando ejecutado y revisión estática: no
   inventar comandos/test results para una revisión que solo leyó fuentes.
8. REQ-134 debe interpretar código y payload según versión: exit0 del checker
   no es éxito del sistema. Mantener INVALID_INPUT, INFRA y UNKNOWN diferenciados.

Los demás ajustes están individualizados en la matriz. Prioridades P0/P1/P2 del
paquete no se convierten automáticamente en política local ni en autorización.

## Orden de trabajo propuesto

1. Ratificar decisiones de integración, sin reabrir las ya explícitas.
2. Completar I01–I06 y mapear cada requisito local a propietario y falsador.
3. Comprobar correspondencia semántica y FSM entre componentes.
4. Definir casos negativos de integración y corpus comparativo antes de ejecutar.
5. Revisar candidato exacto modular y sus interfaces mediante RDD disponible.
6. Presentar candidato documental; implementación y activación requieren alcance
   posterior. Mantener baseline identificable para comparación y reversión.

No es un plan ejecutado ni un READY. El supervisor sigue DRAFT; su revisión
canónica anterior tiene un bloqueo por contexto y la revisión suplementaria
independiente quedó parcial por límite del proveedor. Este diseño no los cancela.

## Política de ejecución confirmada

Una ejecución supervisada a la vez. Un adaptador habilitado puede ejecutarse dentro
de una tarea ya autorizada sin repetir permisos; ampliación de alcance, recursos o
acciones vuelve al humano. Habilitar un adaptador no autoriza todas sus tareas.

Ante fallo, registrar observación, detener tarea y no reintentar automáticamente.
Nueva ejecución solo si se confirma terminación y limpieza requerida; si no,
bloquear admisión. Un fallo documental no bloquea por sí solo toda la instancia
cuando el proceso ya terminó y no quedan recursos pendientes. No equiparar limpieza
de procesos con rollback de archivos o reversión remota: esas políticas siguen abiertas.

Registro de decisiones y respuestas literales: decisiones-confirmadas.json y
registro-preguntas.md. La retención32MiB/manual sigue siendo la política de salidas QA;
no se extiende automáticamente a todos los nuevos adaptadores.

## Escrituras e incorporación confirmadas

INT-D08: trabajo con escritura en espacio aislado. INT-D09: conservar cambios
parciales y evidencias de tareas fallidas, sin promoverlos al proyecto. La captura
QA32MiB/manual es independiente del almacenamiento del workspace, aún sin presupuesto.

INT-D10: incorporar automáticamente resultados dentro de una tarea ya autorizada
cuando cumplan todos sus criterios verificables. No exige una aprobación humana
adicional del diff en cada ocasión, ni autoriza commit, push, instalación o despliegue.
La presente selección es política de diseño, no permiso de implementación actual.

INT-D11: si cambia el proyecto base, detener incorporación, conservar candidato
estacionado y reevaluar sobre la nueva base. No fusionar ni reintentar automáticamente.
Una nueva evaluación no preserva por defecto la evidencia afectada ni la aprobación
ligada a otra identidad. La continuidad de la autorización depende de su alcance.

### Consecuencias técnicas propuestas, todavía por verificar

Separar identidad de base, candidato aislado y destino observado. Comparar y aplicar
requiere coordinación que impida cambios relevantes entre ambos pasos; comparar un
hash antes de escribir no prueba atomicidad. Definir qué abarca cada identidad:
contenido, índice, archivos no rastreados, permisos y dependencias según el contrato.
No imponer un commit como único tipo de identidad si el runtime admite snapshot exacto.

La adopción debe conservar un expediente que explique criterios y evidencia que
permitieron cada incorporación. Si el estado de aplicación es incierto, no emitir
éxito ni admitir tareas que dependan del destino incierto. No prometer atomicidad
multiarchivo mediante renombrado individual. Son obligaciones de diseño pendientes,
no un mecanismo implementado o demostrado.

## Recuperación y almacenamiento confirmados

INT-D12: restauración automática condicionada a base recuperable verificable y
preservación de cambios ajenos. Si no puede comprobarse, bloquear y escalar; conservar
evidencia. Esto no autoriza reintentos ni demuestra una técnica de rollback.

INT-D13: presupuestos por tarea y límite total del supervisor para espacios aislados
y copias de recuperación. No se borran automáticamente trabajos conservados.
INT-D14: presupuestos ajustables, sin elegir1GiB/2GiB. Antes de solicitar ampliación,
un preflight debe comprobar disponibilidad para el espacio requerido. Si no existe
capacidad comprobada, no presentar la ampliación como viable ni admitirla por mera
aprobación humana. Aún no se ha fijado fórmula, margen ni monto inicial.

La política32MiB/manual de salidas QA permanece separada; estos presupuestos de
workspace no la sustituyen. La respuesta no autoriza ampliar simultáneamente otros
recursos, red, CPU, permisos de archivos o ejecución.

### Diseño técnico propuesto para la ampliación

1. Antes de una escritura o reserva que excedería el presupuesto, detener la
   admisión de nuevas escrituras afectadas. Si se detecta un exceso ya ocurrido,
   registrarlo como incumplimiento del control; no legitimarlo retroactivamente.
2. Calcular incremento necesario y destino exacto. Observar espacio utilizable
   por la cuenta, cuotas aplicables y reservas existentes, evitando contar el mismo
   volumen compartido varias veces. Incluir recuperación y temporales en la demanda.
3. Si la evidencia es insuficiente o no hay espacio, RESOURCE_BLOCKED. Conservar
   presupuesto anterior y evidencia; no solicitar una ampliación presentada como viable.
4. Si es viable, proponer al humano monto anterior/nuevo, incremento, tarea,
   volumen afectado, consumo agregado, observación y límites del preflight.
5. Tras autorización suficiente, revalidar disponibilidad y obtener reserva/cuota
   efectiva cuando el mecanismo disponible lo permita; actualizar contabilidad
   antes de reanudar. Si cambió la disponibilidad, permanecer bloqueado.
6. Observar fallos de asignación/escritura aunque el preflight haya pasado. Ninguna
   lectura de espacio libre garantiza capacidad futura ni capacidad física del host
   desde WSL. Declarar alcance guest/volumen, unknowns y límites del mecanismo.

El flujo es una propuesta de implementación verificable, no código ni una garantía
actual. La verificación de disponibilidad previa al consentimiento está confirmada;
la elección de mecanismo de reserva, márgenes y cuotas sigue pendiente.

Falsadores propuestos: ampliación solicitada como viable con capacidad desconocida;
aprobación que ignora un cambio de espacio antes de reanudar; doble conteo de volumen;
aumento implícito de otro presupuesto; fallo de escritura clasificado como éxito.
Todos los ensayos del mecanismo permanecen NOT_RUN.

## Estimación y exploración confirmadas

INT-D15: si aumentar una tarea exige elevar también el límite total, una sola
solicitud enumera ambos presupuestos actuales, incrementos y valores nuevos. La
aprobación debe cubrir explícitamente ambos; no hay aumento global implícito.

INT-D16: el supervisor calcula una propuesta de presupuesto inicial, comprueba
viabilidad y la incluye en la autorización de tarea. Desglosar trabajo, temporales,
evidencias y recuperación; método y márgenes por adaptador siguen pendientes.

INT-D17: ante una parte material no estimable, proponer exploración con presupuesto
propio y autorización suficiente. La tarea principal sigue bloqueada mientras la
estimación sea insuficiente. No se crea un presupuesto ilimitado para descubrir
cuánto presupuesto hace falta: el de exploración debe ser acotado antes de iniciarse.

INT-D18: solo inspección y muestras pequeñas mediante adaptadores habilitados, sin
modificar proyecto principal ni ejecutar su código. Lectura de un comando en un
manifiesto no permite ejecutarlo; importar módulos, instalar dependencias o lanzar
hooks del proyecto tampoco es inspección pasiva. Los muestreos deben declarar sus
límites y no convertir una muestra favorable en una garantía de tamaño total.

INT-D19: al agotar el presupuesto, detener la exploración; conservar observaciones
y resultados parciales sin promoverlos a suficientes. Preparar una solicitud de
ampliación únicamente después de preflight que establezca disponibilidad requerida.
Si disponibilidad insuficiente/desconocida, RESOURCE_BLOCKED sin ampliación.
No reanudar ni elevar límites hasta autorización suficiente. Revalidar disponibilidad
al reanudar según contrato propuesto; autorización y admisión de recursos son distintas.

La ampliación cambia solo los recursos enumerados en la solicitud. No amplía
métodos, permisos de escritura, red ni permiso para ejecutar código del proyecto.
Una ampliación aprobada permite continuación bajo alcance autorizado; no introduce
reintentos automáticos de tareas fallidas. La evidencia previa no se borra ni se
reclasifica retroactivamente. Se mantiene una ejecución supervisada a la vez.

## Traza de comportamiento propuesta para formalización

ESTIMATE → (suficiente) TASK_ADMISSION; o (insuficiente) EXPLORATION_PROPOSED →
AWAITING_AUTHORIZATION → ADMISSION → EXPLORING.

EXPLORING → (presupuesto agotado) STOPPING → (terminación/limpieza confirmadas)
CAPACITY_PREFLIGHT → (capacidad suficiente) AWAITING_EXPANSION_AUTHORIZATION;
o (capacidad insuficiente/desconocida) RESOURCE_BLOCKED.

Autorización recibida → REVALIDATE_ADMISSION → (viable) EXPLORING;
si no es viable, RESOURCE_BLOCKED. Limpieza incierta → bloqueo de nuevas ejecuciones.
Una observación suficiente vuelve a ESTIMATE; no habilita por sí sola la tarea principal.

Es un boceto de estados, no una FSM exhaustiva ni prueba de implementación. Falta
fijar las guardas observables, límites por adaptador, contabilidad, cancelación y
revocación. No se afirma READY ni se ejecutó exploración del proyecto.

## Pendientes materiales de diseño

Contratos concretos de adaptadores; métodos/márgenes de estimación; reserva y cuota;
identidad y recuperación; actualización/revocación; incorporación controlada.
Las decisiones ya confirmadas no deben preguntarse de nuevo. Los valores o mecanismos
no especificados permanecen abiertos y no se deducen de las respuestas A/B.

## Revocación diferida confirmada

INT-D20/21: una revocación ordinaria impide iniciar otras tareas, pero permite
terminar la tarea que ya estaba en curso, incluso con varias invocaciones de
adaptadores dentro de su autorización existente. Identificar de forma inequívoca
esa tarea; no renombrar una tarea nueva como continuación para ampliar la excepción.

Se conservan ejecución secuencial, alcance, límites y prohibición de reintentos
automáticos. Agotar presupuesto, fallar o no confirmar limpieza no queda excusado
por esta política. No otorgar automáticamente permisos adicionales ni una extensión
de la tarea. Semántica de caducidad, cancelación inmediata y cambios de versión del
adaptador se definirá por separado; no confundirla con revocación ordinaria diferida.

INT-D22 resuelve Q-INT-022: la tarea termina en aislamiento; después de revocación
no se incorporan resultados al proyecto sin nueva autorización. Esta excepción
prevalece sobre INT-D10 (incorporación automática habitual). Superar las verificaciones
no elimina la necesidad de esa autorización. Antes de cualquier incorporación
autorizada se mantiene la comprobación de base y vigencia de evidencias de INT-D11.


### Precedencia de incorporación documentada

- Sin revocación y dentro de la tarea autorizada: incorporación automática solo si
  todos los criterios verificables están satisfechos y la base no cambió.
- Con revocación diferida registrada antes de iniciar incorporación: terminar el
  trabajo aislado; exigir nueva autorización de incorporación.
- Con base modificada: detener incorporación y reevaluar; una autorización no
  convierte evidencia obsoleta en vigente.
- Con fallo o estado incierto: no presentar éxito; aplicar el contrato de parada,
  bloqueo y recuperación ya definido.

INT-D23: si la revocación se recibe durante una incorporación iniciada, detener
nuevas escrituras de incorporación y aplicar la recuperación condicionada de INT-D12.
Distinguir escrituras para continuar la incorporación de escrituras estrictamente
necesarias para restaurar una base recuperable sin sobrescribir cambios ajenos.
Si la restauración no es verificablemente segura, mantener el proyecto bloqueado y
solicitar intervención; conservar resultados aislados y evidencias.

No se garantiza cancelar instantáneamente una operación ya emitida al sistema
operativo. El diseño debe definir el punto de recepción/aceptación de la revocación,
la observación de operaciones en curso y la coordinación con la recuperación antes
de afirmar terminación o restauración. Estas obligaciones técnicas siguen pendientes
de especificación y prueba; la política humana ya está resuelta.
