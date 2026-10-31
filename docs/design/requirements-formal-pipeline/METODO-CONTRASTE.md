# Método de contraste para el análisis formal de requisitos

Estado: ampliación documental propuesta; no implementación ni ensayos nuevos.
Decisión humana literal: «Quiero uses en ese proceso método científico bungeano
y falsacion de popper». Se incorpora como método requerido. Los mecanismos
concretos siguientes son operacionalización propuesta, no certificación filosófica.
Base: skills/requerimientos-socraticos/references/method.md, sección Bunge y Popper.

## Contexto confirmado y límites

El humano aclaró que 32 corresponde a variables booleanas y confirmó DO-178C.
No fijó aquí qué unidad contiene esas variables: por decisión, módulo o modelo
completo sigue por precisar antes de implementar el límite. No se convierte una
propuesta anterior del asistente en decisión humana. Tampoco está fundamentada
la afirmación histórica «triplica la cobertura»: falta métrica y cálculo.
DO-178C no se reduce a una tabla, solver, prueba Lean ni revisión RDD.
Lean, ROBDD y exploración simbólica son alternativas discutidas, no instaladas.

## Separar la naturaleza de cada afirmación

| Clase | Ejemplo | Contraste adecuado |
|---|---|---|
| Decisión normativa | No iniciar sin autorización | Fuente humana y coherencia; comprobar después cumplimiento |
| Definición | Qué significa autorización vigente | Precisión, ejemplos y confirmación de significado |
| Deducción formal | Una transición preserva un invariante | Demostración o búsqueda de contraejemplo bajo modelo explícito |
| Hipótesis empírica | Este motor cabe en el equipo objetivo | Medición autorizada de recursos sobre ese equipo |
| Observación | Un caso produjo un resultado concreto | Artefactos, condiciones y procedimiento reproducibles |

No falsar la preferencia humana como si fuera una ley física. Sí puede refutarse
que una implementación satisface una obligación acordada. Las inconsistencias
entre decisiones se presentan al dueño, sin resolverlas por preferencia del LLM.

## Ciclo operacional

1. Problema: qué resultado falta, qué sistema se estudia y qué consecuencias importan.
2. Referentes: componentes, entorno, relaciones, mecanismo y frontera de abstracción.
   No confundir totalidad del sistema con suma de comprobaciones aisladas.
3. Hipótesis rivales: predicciones alternativas cuando exista incertidumbre material.
4. Formalización: texto→significado confirmado→EARS→IR tipado; supuestos separados.
5. Deducción: consecuencias y consultas ligadas a revisión, dominio y propiedad.
6. Falsador previo: qué observación o contraejemplo contradice la afirmación,
   oráculo, condiciones, controles y alcance antes de observar el resultado.
7. Contraste: análisis matemático o ensayo empírico según la clase de afirmación.
8. Adjudicación: refutada en alcance / no falsada bajo T / inconclusa / no ensayada.
9. Revisión: conservar historial, preguntar por gaps semánticos, versionar modelo
   y reabrir conclusiones dependientes. No cambiar oráculo para encubrir el fallo.

No presentar este ciclo como definición exhaustiva de la filosofía de Bunge o
Popper: es un contrato de trabajo inspirado en ambos, con resultados verificables.

## Preguntas y controles sobre el modelo

Antes de analizar propiedades comprobar dominio no vacío y activación de guardas.
Buscar entradas factibles sin respuesta, contradicciones de conjunto, vacuidad y
supuestos que excluyan contraejemplos. Toda exclusión requiere fuente y razón.
La división de un modelo requiere comprobar interfaces y dependencias cruzadas.
UNKNOWN del solver o conocimiento insuficiente conserva el pendiente.
Un testigo simbólico es una asignación del modelo, no una observación del hardware.

Para afirmaciones de cobertura, declarar: universo, restricciones, tamaño, método,
límites temporales/espaciales, regiones examinadas y pendientes. Si se completa
exploración exacta, limitar el resultado a ese universo. Una muestra o MC/DC no se
etiquetan cobertura exhaustiva. Lean acredita el enunciado probado bajo sus
supuestos/axiomas; no confirma significado humano ni correspondencia del software.

Controles negativos deliberados evalúan al instrumento: retirar una guarda debe
ser detectado si ese es el objeto del control. Se etiquetan como mutaciones del
modelo; no son defectos reales ni RED observado del sistema original.
Separar test negativo que pasa de RED de TDD que falla por incumplimiento real.

## Matriz de contraste propuesta

| ID | Afirmación | Falsador u observación contraria | Resultado actual |
|---|---|---|---|
| H1 | El análisis conserva todos los casos factibles declarados | Tabla finita independiente encuentra caso omitido sin exclusión confirmada | NOT_RUN |
| H2 | Las condiciones desconocidas no habilitan una operación | Traza con requisito de condición conocida incumplido y operación iniciada | NOT_RUN |
| H3 | Un resultado favorable no oculta otra obligación pendiente | Informe agregado PASS con obligación material NOT_RUN/STALE | NOT_RUN |
| H4 | El instrumento detecta contradicciones de conjunto | Tres obligaciones incompatibles juntas, compatibles por parejas, no detectadas | NOT_RUN |
| H5 | La configuración seleccionada resulta viable en i3/WSL | Ensayo representativo excede presupuesto y criterio de parada previamente acordados | NOT_RUN; presupuesto y acceso pendientes |
| H6 | El modelo representa el significado confirmado | Escenario confirmado por humano contradice la interpretación formal | PENDING_SEMANTIC_REVIEW |

H1–H4 son propiedades propuestas de un analizador todavía no construido; no
confundirlas con resultados de los scripts existentes ni con pruebas ya realizadas.
H5 es empírica; no se resuelve demostrando una fórmula. H6 combina evaluación
semántica humana y contraste de ejemplos; Lean no puede decidir intención.

## Registro y salida

Cada entrada conserva claim_id, clase, texto fuente, autoridad, supuestos,
modelo/revisión, hipótesis rivales aplicables, predicción, falsador, oráculo,
método, presupuesto acordado, evidencia, resultado, límites y preguntas abiertas.
El hallazgo se traduce a escenario natural con valores, estado y reglas afectadas;
se pregunta una dimensión material a la vez. No inventar diálogos ni respuestas.

Un fallo exige localizar si corresponde al requisito, traducción, modelo,
instrumento, implementación o entorno antes de atribuir causa. Una prueba adversa
al conjunto de hipótesis y supuestos no identifica automáticamente cuál falló.
No acumular solo confirmaciones; priorizar pruebas que distingan alternativas y
los casos donde una afirmación arriesga ser refutada, respetando normas y recursos.

El informe distingue método, diseño, análisis formal y observación empírica.
Nunca convierte «no se encontró contraejemplo» en verdad universal. No reducir
alcance para volver favorable un resultado; cualquier exclusión nueva requiere
justificación y autoridad. Mantener fuentes originales y resultados desfavorables.
RDD documental comprueba el alcance admitido; no sustituye experimento ni prueba
formal, ni acepta riesgos o políticas por el humano. CI continúa diferido.
