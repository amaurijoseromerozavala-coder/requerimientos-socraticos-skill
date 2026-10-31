# PRD: QA Inquisidor para Gentle AI

Estado: **DRAFT**. Fuente canónica: `prd.json`. Este documento es una vista
humana; el registro de requisitos, sus fuentes y falsadores está en el JSON.
No se ha creado ni activado la skill QA Inquisidor ni auditado una aplicación.

## Intención confirmada

QA Inquisidor ejercerá verificación adversarial y rigurosa sobre el sistema
objetivo completo. Buscará bugs, casos límite, incoherencias, conflictos de
contratos y variaciones no deterministas. Emitirá contenido en español con las
secciones, en este orden, `ANALYSIS`, `TEST PLAN` y `VERIFICATION`.

La regla «zero doxa» exige separar conocimiento observado, hipótesis, decisiones
y recomendaciones. No prohíbe formular una hipótesis: prohíbe presentarla como
hecho sin evidencia. «No refutado bajo T» no equivale a verdad universal.

Decisión humana Q1: exigir repetibilidad con entradas, versiones y entorno
fijados, declarando lo no demostrado. No se promete determinismo del LLM,
ausencia universal de bugs ni equivalencia entre un mock y un sistema real.

«Perfeccionismo» se operacionaliza como rigor, controles negativos y pendientes
visibles, con presupuestos finitos. No significa hostilidad hacia personas,
búsqueda infinita ni ocultamiento de límites para producir un PASS.

## Fronteras y cobertura integral

Cada invocación necesita un sistema objetivo, snapshot, requisitos/contratos,
fronteras y autorización. Inventariar componentes, servicios, persistencia,
interfaces, configuración, dependencias y despliegue cuando sean aplicables.
Revisar sus relaciones y consumidores, no solo las líneas modificadas.

Toda parte debe tener estado y razón: EXAMINED, NOT_EXAMINED, BLOCKED o
NOT_APPLICABLE. Una dependencia inaccesible permanece visible. No presentar una
muestra, subconjunto o componente aislado como examen integral.

Las búsquedas por símbolos y los cachés reducen lectura repetida, pero requieren
hashes y entorno vigentes. Al cambiar el sistema, reconstruir su inventario y
reconsiderar contratos entre componentes, invalidando la evidencia dependiente.
No es obligatorio ejecutar de nuevo cada prueba inafectada: su reutilización
debe justificarse mediante dependencias y contexto; no únicamente por antigüedad.

## Arquitectura candidata de la futura skill

Es una propuesta de organización, no una implementación ni una decisión sobre
la arquitectura de una aplicación todavía desconocida:

1. **Captura y autoridad:** identificar objetivo, requisitos, permisos y presupuesto.
2. **Inventario del sistema:** componentes, contratos y mapa de impacto completo.
3. **Registro de afirmaciones:** fuente, clasificación epistémica y falsador.
4. **Plan adversarial:** bordes, fallos, recuperación, integración y regresiones.
5. **Obtención de evidencia:** MCP/skills pertinentes primero; consola o fuentes
   primarias con motivo documentado cuando aporten mejor evidencia.
6. **Control de fases:** FSM, invalidación y rechazo de cierre sin cobertura.
7. **Informe:** contrato JSON cerrado y representación española de tres secciones.

La opción inicial a evaluar es un coordinador con pasos secuenciales y contexto
dirigido; agentes adicionales solo para una razón concreta. Comparar su consumo
con alternativas antes de atribuir ahorro. No seleccionar un modelo local que
necesite una GPU o memoria no demostradas como disponibles.

Para contratos documentales, JSON Schema Draft 2020-12 y el validador ya presente
son una opción comprobable de validación estructural. No sustituyen comprobación
semántica, referencias cruzadas, permisos o pruebas de ejecución. Un solver
formal adicional solo se propondrá para una obligación que lo necesite, con
coste y límites explícitos; no instalarlo por defecto.

## Perfil de recursos

El objetivo declarado es un i3-3240, 8 GB de RAM física, SSD de 238 GB y GT 710
de 2 GB, con Ubuntu WSL limitado a «6gb», «2gb» de zram y «8gb» de swap.
El perfil está en `environment-target.json`; no es una medición de este Cloud.

Antes de ejecutar pruebas, observar límites efectivos, versiones y recursos
libres. Zram consume parte de la RAM asignada; swap no aporta RAM física ni
demuestra rendimiento aceptable. No hay umbrales de latencia, tiempo máximo,
token budget o carga de trabajo decididos: cada ejecución deberá recibirlos o
registrar que faltan antes de afirmar cumplimiento de rendimiento.

## Contrato de evidencia y salida

Cada hallazgo necesita ubicación, afirmación concreta, clasificación, condición
de refutación y evidencia. Conservar comando/MCP real, versión, fecha, snapshot,
entorno, resultado, salida y hash. Marcar lo no ejecutado como NOT_RUN. No usar
un exit code aislado como prueba de que se satisfizo el oráculo esperado.

`qa-report.schema.json` define el contrato propuesto. Los encabezados permanecen
en inglés por petición expresa; todo texto sustantivo es español. Los veredictos
son PASS_WITHIN_SCOPE, FAIL, INCONCLUSIVE y BLOCKED. El primero solo se admite
con cobertura completa del alcance declarado, resultados aplicables pasados y
evidencia vigente. Su validación estructural no demuestra por sí sola los claims. Un comprobador
semántico debe vincular cada resultado PASS a evidencia PASS del tipo de
ejecución planificado. REAL_EXECUTION exige un recibo real; evidencia estática
puede complementar, pero no sustituirlo. Rechazar IDs duplicados antes de
construir índices y exigir correspondencia de un caso con un resultado; una
colisión no puede sobrescribir registros ni ocultar una obligación.

El esquema exige al menos un caso negativo, de borde, fallo o recuperación;
revisar además que se cubran las clases aplicables, no solo ese mínimo sintáctico.
La repetibilidad requiere al menos dos observaciones comparables como mínimo
lógico; el número necesario, tolerancias y significancia dependen del contrato.
Dos repeticiones no certifican determinismo universal.

## Modelo de control y límites formales

La FSM tiene CAPTURED, ANALYSIS, TEST_PLAN, VERIFICATION, REPORTABLE, BLOCKED
y DONE. Dos variables registran cobertura y evidencia completas. Hay cinco
eventos abstractos: PROGRESS, INVALIDATE, UNAVAILABLE, RESUME y OTHER.
OTHER y actores no autorizados tienen rechazo explícito sin mutación.

DONE exige ambas variables verdaderas; INVALIDATE vuelve a ANALYSIS y las
limpia. PROGRESS representa el resultado comprobado de una fase, no un permiso
para que el LLM autodeclare éxito. El PRD mantiene abierto G1: concretar los
oráculos reales de fase y su integración con herramientas en el diseño de la
futura skill. Por ello `abstraction_complete=false` y no se declara READY.

La enumeración del modelo puede demostrar cobertura, exclusividad, autorización
y conservación de los invariantes de esta abstracción. No demuestra el
comportamiento de un software inexistente, la integridad de una autenticación
externa, concurrencia real ni todas las ambigüedades del lenguaje natural.

## Verificación de este PRD

Los criterios y controles negativos están en `acceptance-cases.json` y preceden
al borrador. Se preservan comprobador documental, comandos, salidas y testigos
en `evidence/`; su resultado se informa en `validation.json`. RDD revisa el
candidato documental exacto, no atribuye funcionamiento a la futura skill.

Autorizar el PRD no autoriza implementar, instalar, reparar o desplegar. Las
pruebas potencialmente destructivas o sobre producción necesitan autorización
propia; sin ella, se conserva el plan y se declara el bloqueo.
