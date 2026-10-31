# Registro real skill → asistente: continuación QA



Entrevistador: /root/qa_requirements_resume. Respondedor: /root.

Estado: ciclo técnico acotado contestado; PRD global incompleto.



## Q-QA-006

Q-QA-006 — destinatario: ASSISTANT_RESPONDER; dimensión: autoridad de alcance/materialidad/suficiencia semántica. ¿Qué fuente humana vigente identifica quién puede aceptar esos tres juicios para derivar RECORD_CURRENT_SUCCESS, y qué contrato documental propones para distinguir un juicio técnico del asistente de una decisión autorizada cuando esa delegación no consta? Expón el estado de cada juicio —confirmado, propuesta o UNKNOWN— y un caso concreto que deba conservar RECORD_GAP_OR_STALE aunque IDs, hashes y evidencias estructurales sean válidos. No implementes ni atribuyas una decisión al humano por silencio.


A-QA-006: No consta una fuente humana que delegue al asistente la aceptación final de alcance, materialidad y suficiencia semántica. Confirmado: el humano pide analizar todo el sistema, evidencia comprobada, repetibilidad con entradas/versiones/entorno fijados y declarar lo no demostrado; default Solo análisis; ejecución con autorización específica. UNKNOWN: quién puede aceptar esos tres juicios en cada evaluación y mediante qué delegación. Juicio técnico del asistente: permitido proponer inventario, materialidad y correspondencia, con fuentes y razones, pero esa propuesta no acredita por sí misma aceptación humana. Contrato propuesto: acceptance registra actor real, role, decision_source_ref humano o delegación explícita vigente, assessment/snapshot/scope_digest/versiones, los tres juicios por separado, evidencia/razón, estado PROPOSED/ACCEPTED/REJECTED y límites. Ningún ACCEPTED se deriva del nombre HUMAN_OWNER en JSON; el runtime debe contrastar la fuente con la instrucción real. Cambiar inventario/alcance/evidencia relevante invalida la aceptación dependiente. Sin delegación o decisión verificable, RECORD_GAP_OR_STALE conserva pendiente aunque la estructura sea válida. Caso: todos los casos de dos módulos pasan y sus hashes coinciden, pero el inventario omite un tercer consumidor conocido, o solo el asistente afirma que el ensayo físico es no material. No hay cobertura aceptada de todo el sistema; no derivar SUCCESS. Recomiendo al humano elegir entre aceptación final humana explícita para esos juicios o delegación técnica acotada por evaluación; no lo decido por silencio. Esto es diseño pendiente, no implementación ni prueba.


El entrevistador contrastó la respuesta como diseño propuesto; se cierra solo esta dimensión del ciclo técnico. Q006 escaló la política, resuelta posteriormente por fuente humana preservada. No cierra PRD ni evidencia de sistema.



## Q-QA-007

Q-QA-007 — dimensión: tipado y cardinalidad del contrato de evidencia. ¿Qué predicado total y comprobable propones para derivar exactamente una salida entre REJECT_INPUT, RECORD_CURRENT_FAILURE, RECORD_GAP_OR_STALE y RECORD_CURRENT_SUCCESS desde un inventario no vacío y sus registros, cuando pueden coexistir un contraejemplo vigente y otra obligación NOT_RUN? Define precedencia, claves/cardinalidades/uniones por ID y tratamiento de UNKNOWN; distingue la totalidad de esta función documental de la cobertura del sistema real y deja la aceptación humana parametrizada, no supuesta.


A-QA-007: Propuesta técnica con precedencia REJECT_INPUT > RECORD_CURRENT_FAILURE > RECORD_GAP_OR_STALE > RECORD_CURRENT_SUCCESS. Primero shape/tipos, claves únicas assessment/obligation/case/evidence/judgment, referencias resueltas sin overwrite y cardinalidades: inventario 1..N, 1 estado derivado por obligación; cada obligación material aplicable tiene al menos un caso/oráculo previo y cada caso requerido tiene exactamente un registro actual (historial aparte), 0..N evidencias identificadas. Duplicados/ref ambigua o huérfana -> REJECT_INPUT, sin transición. NOT_RUN/UNKNOWN válidos son datos pendientes, no errores de sintaxis. Por obligación: CURRENT_FAILURE si hay contraejemplo observado vigente, tipo/snapshot/entorno/versiones coincidentes y oráculo previo contrastado; CURRENT_SUCCESS solo si todos sus casos requeridos favorables, sin contradicción/pendiente y suficiencia justificada; resto GAP. Evidencia FAIL vigente y PASS simultáneo para mismo caso es contradicción de datos => REJECT_INPUT con ambos preservados, no elegir uno. Agregado sobre obligaciones materiales aplicables no vacías: cualquier fallo válido -> FAILURE conservando lista gaps/cobertura incompleta; sin fallos y cualquier gap/juicio pendiente -> GAP; sin fallos/gaps y todas éxito y autoridad válida -> SUCCESS; conjunto material vacío o cobertura no justificada -> GAP. Invariantes FAILURE no implica todo verificado; SUCCESS no implica permiso. Humano acaba de decidir literalmente: 'Delegas esos juicios técnicos a la skill dentro de criterios explícitos; las excepciones vuelven a ti.' La elección de delegación es confirmada, no convierte criterios futuros en hechos. Propongo criterios explícitos conservadores: inventario de todo sistema y contratos trazado a fuentes, ninguna exclusión conocida sin razón/autoridad; materialidad desconocida se conserva requerida; toda obligación requerida con oráculo previo, evidencia vigente del tipo exigido y sin pendiente/contradicción; incertidumbre o conflicto de alcance/autoridad -> ESCALATE_USER/GAP. Delegación no es autoautorización de ensayos. Esta función finita es total sobre resúmenes tipados admitidos, no prueba completitud del sistema real ni fiabilidad universal de fuentes. Tipos y tabla aún se preparan, no ensayos ejecutados.


El entrevistador contrastó la respuesta como diseño propuesto; se cierra solo esta dimensión del ciclo técnico. Q006 escaló la política, resuelta posteriormente por fuente humana preservada. No cierra PRD ni evidencia de sistema.



## Q-QA-008

Q-QA-008 — dimensión: vigencia de criterios delegados e invalidación. ¿Qué condiciones verificables debe satisfacer un juicio delegado para vincularse al assessment, alcance/inventario, obligaciones/oráculos, candidato y versión previa de criterios, y qué cambio o excepción lo obliga a GAP/ESCALATE_USER en vez de reusar SUCCESS? Incluye el caso de una fuente pendiente que el asistente intenta convertir en NOT_APPLICABLE y cómo registrarás la valoración sin afirmar que inventario trazado demuestra completitud real.


A-QA-008: Propongo criterios identificados/versionados/fijados antes del juicio; judgment_id único con actor_runtime real, delegation_source_ref humano vigente, assessment_id y content digests de snapshot, scope+inventario, obligations+oracles, evidence_set y criteria. Cada juicio conserva decision SUPPORTED/PENDING/EXCEPTION, razón, fuentes y límites. Guardas mecánicas: referencias únicas, todos los digests recalculados coinciden con los mismos bytes consumidos; criterios existentes previamente por la traza documental (orden de registro, no confiar solo en timestamp autorreportado), todos los predicados definidos comprobados, sin UNKNOWN/excepción relevante. Su verdad externa no se prueba por el hash. ACCEPTED automático se limita al contrato confirmado y criterios conservadores explícitos; una nueva política de negocio o redefinición del alcance necesita fuente humana, no se deriva por delegación técnica. Cambio de candidato/scope/inventario/obligación/oráculo/evidencia/criterio/delegación produce INVALIDATE y nuevos juicios/evaluación; nunca editar un criterio para justificar retroactivamente SUCCESS. Cualquier fuente requerida pendiente conserva UNKNOWN, materialidad conservadora y GAP/consulta; no puede transformarse en NOT_APPLICABLE para completar cobertura. NOT_APPLICABLE solo con razón trazable que no excluya alcance humano conocido, y decisión humana si hay conflicto/excepción. Ejemplo fuente del contrato del consumidor falta: registrar fuente pendiente, obligación requerida, juicio PENDING y consulta; no etiquetarla no aplicable. El juicio describe cobertura del inventario conocido, incluye método de descubrimiento/búsquedas/fronteras y pendientes, y no prueba que no existan componentes desconocidos. No existe sistema objetivo seleccionado ni evidencia de aceptación de sus requisitos; por eso este PRD puede definir guardas sin dar PASS de sistema. La tabla/checks probarán la abstracción finita, no autoridad universal ni privacidad del runtime. Criterios y candidato documental nuevos requieren su propia revisión RDD.


El entrevistador contrastó la respuesta como diseño propuesto; se cierra solo esta dimensión del ciclo técnico. Q006 escaló la política, resuelta posteriormente por fuente humana preservada. No cierra PRD ni evidencia de sistema.



## Decisión humana emitida por el coordinador

En QA Inquisidor, ¿quién debe confirmar que el alcance, la importancia de los pendientes y la evidencia bastan para emitir PASS?


Delegas esos juicios técnicos a la skill dentro de criterios explícitos; las excepciones vuelven a ti.


No se simula una pregunta del agente al humano. Esta decisión no autoriza ejecución.
