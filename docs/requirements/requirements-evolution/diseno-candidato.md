# Evolución de Requerimientos Socráticos: candidato de diseño

Estado: DISCOVERY / AWAITING_USER. Fecha: 2026-10-30, America/Manaus.
Solo planificación. Ninguna propuesta se considera integrada por aparecer aquí.

## 1. Propósito y fuentes

[D] El humano pide analizar skills.txt, contrastarlo con lo existente y decidir
punto por punto, con opciones, consecuencias y recomendaciones, cómo mejorar la
propia skill. Autoriza preparar documentos; no instalar motores ni implementar.

[F] El archivo adjunto contiene propuestas conversacionales; sus comparaciones,
recomendaciones y mandatos citados no son decisiones actuales del humano.
Fuente íntegra y hashes: source-chat.txt y evidence-map.json.

[F] Baseline local observado: requerimientos-socraticos2.4.6, QA0.1.3-alpha y
PRD de supervisor local todavía DRAFT. El supervisor no está implementado.
[F] Existe además un paquete cloud socratic-requirements3.2.1. Su texto declara
otro stack; no se ha establecido equivalencia, migración ni instalación local.
[C] Mantener restricciones de plataformas, alcance local y hardware compartido.
CI/producción siguen diferidos. La retención32MiB/manual pertenece al supervisor
QA; no se traslada automáticamente a todas las memorias de requisitos.

## 2. Diagnóstico del bosquejo

| Punto | Evaluación | Tratamiento propuesto |
|---|---|---|
| Conservar la skill como núcleo | [I] Reduce traducciones y migraciones | Baseline local fijado, extensiones pequeñas |
| Humano y PRD como autoridad | [I] Adecuado, con alcance por operación | Separar intención, integridad, procedencia y permiso efectivo |
| Controlador determinista | [I] Útil como evaluador de contratos | No llamarlo autoridad externa si comparte cuenta/archivos con el agente |
| Revisor externo | [I] Puede encontrar omisiones | Informe propuesto; independencia de agente no implica independencia de credenciales |
| Z3 y FRET | [F/E] Local booleano; FRET documenta lenguaje restringido y representaciones formales | Verificadores complementarios, traducción revisada; no equivalencia automática |
| Ouroboros/Symposium | [U] Identidad exacta, versiones y capacidades no corroboradas en esta ronda | No instalar ni adoptar sus comandos basándose en el adjunto |
| Spec Kit/Superpowers/Trail of Bits | [I/U] Ideas de procesos reutilizables; compatibilidad completa no comprobada | Evaluar una capacidad y licencia/versión por vez, después de delimitar alcance |
| Benchmarks comparativos | [I] Necesarios para afirmar mejora | Corpus independiente y oráculos fijados antes de comparar |
| Cambiar modelo sin cambiar política | [I] Viable como contrato | Modelo propone; reglas no dependen de su respuesta persuasiva |
| Workflow hasta producción | [I] Arquitectura posterior distinta | Diseñar interfaz de entrega, sin activar CI ni despliegues |

No se ha demostrado que una skill produzca menos errores que otra. Conteo de
tests, estrellas o un resultado SAT no miden fidelidad a la intención humana.

## 3. Correcciones conceptuales que necesita el diseño

1. [I] Un digest prueba correspondencia de bytes, no quién autorizó su contenido.
   Un recibo requiere contrato de emisor, identidad del candidato, versión de
   política, operación permitida, vigencia y verificador confiable. Lo que no se
   pueda comprobar debe quedar explícitamente no verificado.
2. [I] Un control local puede imponer reglas a consumidores cooperantes. No
   garantiza que cualquier programa de la cuenta lo invoque. No elevar el
   resultado local a permiso de producción.
3. [I] `pruebas=[]` no permite cerrar por vacuidad. El catálogo de obligaciones
   aplicables se fija por requisito; NOT_APPLICABLE exige razón trazable. Un
   timeout expresa falta de resultado, no refutación de la propiedad.
4. [I] El ejemplo temporal del adjunto restringe únicamente la transición desde
   SCOPED. No cubre por sí solo todas las entradas a EXECUTING, revocación ni
   continuidad de ejecución. Hay que definir si el permiso se comprueba al
   inicio, continuamente o en puntos concretos antes de formular la propiedad.
5. [I] El mismo expediente lógico puede tener resultado reproducible; repetir
   una ejecución limitada puede alternar resultado concluyente/UNKNOWN por
   recursos. Esas dos formas de repetibilidad deben evaluarse por separado.
6. [I] Una skill que propone su propia mejora no puede aprobarla sustituyendo
   silenciosamente las reglas que la evaluaban. Separar baseline, candidato,
   corpus, revisión y activación; mantener retorno al baseline identificado.
7. [F] El PRD canónico previo excedió un presupuesto nativo de revisión. [I]
   Proponer módulos revisables con manifiesto raíz y revisión de sus interfaces.
   Particionar no significa que aprobar partes demuestre el conjunto.

## 4. Arquitectura de referencia, todavía propuesta

CESM: composición=entrevista, IR, verificación, evidencia, evaluación y adaptadores;
entorno=humano, Codex/OpenCode, Gentle, OS, proveedores y hardware visible;
estructura=contratos versionados y dependencias explícitas;
mecanismo=proponer, confirmar, compilar, contrastar, revisar y aceptar.

| Módulo | Entrada y salida | Frontera e integración |
|---|---|---|
| Captura de intención | Texto literal → interpretaciones candidatas | Conservar literal; una respuesta corta no añade unidades, plazos o permisos |
| Registro de decisiones | Confirmación → significado delimitado | Citar turno/actor; corrección posterior sustituye sin borrar historia |
| IR semántica | Significado → conceptos, dimensiones y dependencias | Reutilizar IR local; no compilar desconocidos materiales como axiomas |
| Compiladores | IR → EARS, booleanos, FSM | Cada traducción conserva mapeo y supuestos; extensiones temporales opcionales |
| Verificadores | Modelo identificado → observaciones acotadas | Reutilizar Z3/supervisión; separar estructura, lógica y comportamiento real |
| Expediente | Obligación → evidencia, cobertura, vigencia | Versiones, hashes, ámbito y límites; historial Engram no sustituye artefactos |
| Evaluador de avance | Expediente + política → decisión documental | Función total, orden explícito, desconocidos preservados; no privilegios propios |
| Adaptadores | Contrato de capacidad → herramienta disponible | Proveedor intercambiable, capacidades observadas; sin ejecutar motores ausentes |
| Entrega | PRD identificado → contrato para arquitectura/QA | No activar implementación; receptor verifica alcance y versión |

Relación propuesta: Gentle aporta sus procesos existentes; la skill conserva la
elicitación; QA observa calidad; el supervisor local, cuando exista y esté
autorizado, supervisa únicamente el checker QA. No duplicar esos componentes en
un nuevo framework monolítico.

## 5. Estados y evidencia: propuesta inicial

Separar dimensiones en vez de un único PASS:

- semántica: OPEN / CONFIRMED / CONFLICT;
- admisión: VALID / INVALID / NOT_ASSESSED;
- comprobación: SUPPORTED_WITHIN_SCOPE / COUNTEREXAMPLE / UNKNOWN / NOT_RUN;
- vigencia: CURRENT / STALE / UNVERIFIED;
- autorización: NOT_REQUESTED / GRANTED_FOR_OPERATION / DENIED / EXPIRED;
- ejecución: NOT_RUN / COMPLETED / INFRA_FAILURE.

FSM propuesta: CAPTURED → CLARIFYING → SEMANTIC_CANDIDATE → MODELING →
VERIFYING → REVIEWING → DOCUMENT_ACCEPTED. Pausa y bloqueo preservan pendientes.
Cambio de significado vuelve a CLARIFYING; cambio de bytes invalida evidencia
dependiente. DOCUMENT_ACCEPTED no tiene transición automática a implementación.
Estados, guardas y prioridades aún necesitan decisiones; no es una FSM validada.

## 6. Paquetes de mejora y opciones por decidir

| ID | Decisión | Opciones y consecuencias | Recomendación provisional |
|---|---|---|---|
| D01 | Frontera del candidato | A núcleo de requisitos con interfaz futura: menor alcance; B núcleo y orquestador separado: más contratos; C único flujo hasta producción: mayor acoplamiento | A |
| D02 | Línea base | Local2.4.6; paquetecloud3.2.1; convergencia explícita: cambia tamaño de migración y evidencias | Local2.4.6 contrastada; no asumir parentesco |
| D03 | Autoridad efectiva | Evaluador local documental; consumidor externo protegido: este último exige infraestructura y confianza nuevas | Local con límites declarados mientras CI siga diferido |
| D04 | Fidelidad semántica | Confirmación solo de decisiones materiales; confirmación de toda normalización: más preguntas y coste | Solo cambios materiales y opciones ambiguas |
| D05 | Formalización | Booleanos/FSM acotada; adaptador temporal opcional; sustituir motor: creciente complejidad | Reusar y añadir capacidad cuando un requisito la necesite |
| D06 | Revisión y coste | Secuencial por riesgo; múltiples revisores siempre: más coste sin garantía de independencia | Secuencial por criterio explícito |
| D07 | Evidencia modular | Manifiesto de módulos + revisión de interfaces; monolito: simple exportación pero más presión de contexto | Módulos más exportación completa derivada |
| D08 | Comparación de candidatos | Corpus fijado antes de evaluar y conjunto reservado; adaptar pruebas al candidato: sesgo | Corpus separado, oráculos explícitos y controles negativos |
| D09 | Motores externos | Ideas sin dependencias; adaptadores desactivados; integración completa | Ideas y contratos primero; investigar motores cuando aplique |
| D10 | Activación de automejora | Candidato revisable sin reemplazo; prueba paralela sin autoridad; sustitución directa | Candidato separado, comparación y aprobación antes del reemplazo |

Las recomendaciones son [I], no decisiones aceptadas. Resolver una por turno;
investigar contratos externos solo cuando sean materiales a esa decisión.

## 7. Estrategia de evaluación propuesta

Casos mínimos: decisión inventada; respuesta de unidad que no resuelve plazo;
normalización que altera significado; contradicción material; dominio inconsistente;
obligaciones vacías; evidencia obsoleta; traducción que pierde una condición;
timeout; proveedor ausente; revisión parcial; candidato que cambia sus criterios
de aceptación; exportación incompleta; fallo presente fuera del prefijo examinado.

Para cada caso fijar requisito, resultado esperado, evidencia y falsador antes de
ejecutarlo. Medir decisiones sin soporte, desconocidos materiales omitidos,
contradicciones detectadas, avances indebidos, preguntas redundantes, coste y
resultados inconclusos. Umbrales y corpus no están aprobados. No afirmar cobertura
universal ni capacidad física a partir de las métricas del entorno cloud.

## 8. Viabilidad y pendientes

[I] Un flujo secuencial y documentos acotados es una dirección razonable para el
i3/8GB declarado; no es una prueba de rendimiento. [F] El sondeo observado es del
entorno cloud, no del PC del usuario. [U] Calibración y límites por adaptador.

[E] FRET documenta lenguaje restringido, representaciones formales y exportación:
https://github.com/NASA-SW-VnV/fret . No se verificaron aún sus requisitos exactos
de instalación ni su rendimiento en WSL/i3.
[E] Spec Kit documenta procesos componibles y planificación:
https://github.com/github/spec-kit . No está integrado en este candidato.
Las afirmaciones de versiones de Node/OpenCode, Ouroboros y otros proyectos del
adjunto siguen EVIDENCE_PENDING; no se usan para elegir dependencias aquí.

ASSURANCE-DEBT-01: revisión especializada fresca pendiente por límite de uso
previamente observado; cero invocaciones nuevas en este ciclo. No se simula revisión.
ASSURANCE-DEBT-02: todavía no existe modelo completo ni benchmark ejecutado de la mejora.
EPISTEMIC-DEBT-01: compatibilidad/licencia/versiones de motores externos por investigar.
Estos pendientes impiden READY; no impiden deliberación documental con el humano.

## 9. Primera decisión

Q-EVO-001 — TARGET_DIMENSION: frontera del candidato.
¿Diseñamos primero A) la mejora del núcleo de requisitos con interfaz futura,
B) el núcleo y una skill orquestadora separada, o C) una única skill para todo el
flujo? Se admiten otra alternativa o decisión aplazada.
Respuesta humana: pendiente. No se han aprobado D01–D10.
