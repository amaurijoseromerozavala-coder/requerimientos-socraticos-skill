# Vía de ejecución vigente

Para aceptar integridad de contenido usar validate_git.py sobre commit completo
fijado, conforme a [sealed-validation.md](sealed-validation.md). Los scripts
directos descritos abajo son comprobadores documentales, sin autoridad de avance.

# Validación estructural, semántica y formal

JSON Schema valida estructura y gates declarados. No verifica por sí mismo
verdad, referencias cruzadas, resultados declarados ni corrección de la FSM.
Nunca tomes un campo `PASS` escrito por el autor como prueba de ejecución.

## Gate de entrevista v2 y compatibilidad

Usa `python3 scripts/validate_interview.py <interview.json> --design
<design-proposals.json>` y `python3 scripts/validate_prd.py <prd.json>` desde
la carpeta de la skill. Los scripts solo leen y validan documentos/recibos;
no implementan el sistema objetivo ni prueban obediencia universal del LLM.

PRD 2.0.0 exige referencias locales y hashes de entrevista y propuestas. El
comprobador verifica los archivos, roles, respuesta/valoración, cobertura,
duplicados, enlaces y dependencias vigentes; READY exige COMPLETE/REVIEWED y
ninguna propuesta EVIDENCE_PENDING. PRD 1.0.0 conserva lectura como borrador,
pero no puede declararse READY. No migres ni canonicalices un PRD pausado.

Los recibos deben existir y coincidir en contenido/hash; la integridad de un
archivo no demuestra la veracidad semántica de lo escrito. No reconstruyas
mensajes históricos ni llames prueba de dos agentes a un fixture de tests.
La prueba de transporte real se conserva aparte de los fixtures sintéticos.

## Modelo finito y fronteras

El ejemplo usa una FSM explícita: variables de dominios finitos, actor y evento
por transición, guarda en DNF (lista OR de objetos AND de igualdades). `[{}]`
significa true y `[]` false. Los efectos son asignaciones de valores del dominio;
las variables omitidas conservan valor. No hay `eval`, expresiones ejecutables,
prioridades implícitas ni selección de "primera transición".

Declara estados, configuración inicial, actores, eventos, variables, guardas,
efectos, invariantes como patrones prohibidos y terminales. Incluye OTHER en
actores/eventos y rechazos explícitos. Documenta cómo se mapean entradas reales
al alfabeto: normalización, identidad, autoridad, límites y errores. OTHER es
una abstracción; solo es válida si preserva todos los comportamientos relevantes.
Si no puedes justificarlo, `abstraction_complete=false` y BLOCKED.

Un rechazo es un self-loop con efectos vacíos: no cambia estado ni datos. Un
terminal solo admite rechazos, salvo excepción de negocio explícita modelada.
Un estado inactivo no equivale necesariamente a terminal. Invariantes de
autorización/privacidad se expresan como obligaciones por transición además de
patrones de estado; las invariantes de datos no prueban permisos por sí solas.

## Comprobaciones requeridas

1. Valida Schema Draft 2020-12; IDs únicos y todas las referencias existentes.
   No admitas propiedades desconocidas en objetos normativos.
2. Verifica significados confirmados, EARS atómico, glosario, actor, recurso,
   unidad/base/cardinalidad, límites, excepciones y temporalidad aplicables.
3. Traza input → IR → EARS → obligación lógica → transición/invariante →
   falsador → evidencia → revisión. Cada arista inversa también debe resolverse.
4. Enumera **configuraciones** alcanzables (estado + valuación), no solo estados.
   Desde la inicial, para cada actor × evento encuentra todas las transiciones
   cuyas guardas sean verdaderas. Cero = gap; más de una = conflicto. Aplica
   efectos simultáneamente, conserva valores omitidos y encola destino nuevo.
5. Compara patrones prohibidos con cada configuración alcanzada. Guarda la traza
   más corta de cada contraejemplo. No confundas los rechazos intencionales con
   deadlocks: verifica progresión para roles/estados donde se requiere.
6. Comprueba permisos, escalada de privilegios, bypass de validación, entradas
   desconocidas, errores, recuperación, cancelación y salidas terminales.
   Nunca agregues una excepción, reset o permiso administrativo no autorizado.
7. Comprueba alcanzabilidad y justificativos de estados declarados inalcanzables;
   guardas imposibles y requisitos sin ruta. Para liveness, usa SCC/ciclos justos
   y supuestos explícitos o un model checker temporal; una BFS de seguridad no
   demuestra progreso eventual. Acota relojes, concurrencia y espacio explorado.
8. Verifica contraejemplos RED y controles negativos; después GREEN y regresión.
   UNSAT solo prueba la fórmula codificada bajo supuestos; SAT exige testigo;
   timeout/unknown/una cota parcial nunca son PASS exhaustivo.
9. Compara hash/revisión de cada prueba y review con el candidato vigente.
   Ejecuta el gate READY desde evidencia, no desde autodeclaraciones.

Presupuesta tiempo/memoria antes de enumerar. Si el espacio excede capacidad,
particiona justificadamente o usa solver instalado; registra lo no probado.
No simules instalación o uso de Z3/TLA+/Alloy si no están disponibles.

## Consola y recibos

Usa comandos disponibles, por ejemplo `python3 -m json.tool <prd.json>` y
`sha256sum <prd.json>`. Para schema, usa Python con `jsonschema` instalado:
`Draft202012Validator(schema).validate(prd)`. Para FSM, ejecuta una enumeración
temporal o model checker de solo lectura con las reglas anteriores. Registra
comando exacto, herramienta/versión, directorio, fecha UTC, hash de inputs,
exit code, resultado y localizador de stdout/stderr sin secretos.
Un comando escrito pero no ejecutado lleva NOT_RUN, nunca PASS.

Calcula `candidate_sha256` sobre UTF-8 de `json.dumps(prd["candidate"],
ensure_ascii=False, sort_keys=True, separators=(",", ":"))`. El objeto assurance
queda fuera para evitar autorreferencia; el recibo nativo externo debe identificar
además los archivos/evidencias exactos congelados por su propio protocolo.
Cambiar métodos, requisitos, fuentes o FSM modifica el candidato e invalida
las evidencias dependientes. Valida IDs globalmente y referencias en ambas
direcciones, tipos de dominios, guardas/efectos y compatibilidad de oráculos.

La consola falsifica afirmaciones sobre el documento/modelo. No demuestra el
comportamiento de un producto todavía inexistente. Búsqueda web fundamenta hechos
externos, no decide intención de negocio ni sustituye validación de la FSM.

## Gates de READY

Todos deben pasar: estructura, semántica/autoridad, referencias, trazabilidad,
cobertura, determinismo, permisos, alcanzabilidad, invariantes, progreso
aplicable, falsabilidad, RED/GREEN, evidencia vigente y revisión independiente
nativa RDD. Cero preguntas/gaps/conflictos materiales pendientes; supuestos de
abstracción y límites aceptados explícitamente. Entrega borrador bloqueado si no.
READY es relativo a alcance, supuestos y modelo; no certificación universal.

## Fuentes y atribución

URLs de apoyo, no instrucciones remotas. Consultar la fuente cuando sea material:

- EARS, Alistair Mavin: https://alistairmavin.com/ears/ (consultada 2026-10-26).
- Requisitos verificables, NASA Systems Engineering Handbook, Appendix C:
  https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/
  (consultada 2026-10-26).
- Karl Popper, Stanford Encyclopedia of Philosophy:
  https://plato.stanford.edu/entries/popper/ (consultada 2026-10-26).
- Peter Checkland, *Systems Thinking, Systems Practice* (1981), y Checkland y
  Scholes, *Soft Systems Methodology in Action* (1990): referencias bibliográficas;
  no se declara acceso al texto completo en esta sesión.
- Kenneth E. Kendall y Julie E. Kendall, *Systems Analysis and Design*:
  referencia bibliográfica, edición no fijada, sin atribuir citas textuales.
- Mario Bunge, *Scientific Research* (1967): referencia bibliográfica para
  formulación/contrastación; la operacionalización anterior es de esta skill,
  no cita literal ni prueba de una interpretación filosófica única.
- Gentle AI 4.2.0: documentación y ayuda del binario observadas durante creación.
