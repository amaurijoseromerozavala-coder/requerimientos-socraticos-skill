# WU-RS3-GAP-SCENARIO-INTERROGATION-020

## Objetivo y precedencias

Solicitud humana: cuando Z3 encuentre una combinación factible sin requisito
aplicable, presentar su significado para interrogatorio. Depende de consultas
Z3 ya implementadas, reevaluación del testigo, UI WU-018 y ratificación de
requisitos/tests WU-019. El significado de negocio puede ser propuesto por el
agente, no deducido por Z3 ni promovido a requisito por ese agente.

## Alcance permitido

Emitir en `analyze_logic.py` un paquete estructurado, acotado y ligado al SHA
del modelo para `SAT(D ∧ ¬G)`. Evaluar el testigo además con un evaluador
Booleano independiente; si falla, emitir `INCONCLUSIVE`, no un escenario.
Separar `GAP` de `NO_OUTPUT`; las entradas sin guarda no equivalen a ausencia
de salida. Añadir instrucciones de entrevista: mapear variables a glosario y
fuente; sin significado, pedir aclaración. Una respuesta personalizada vuelve
a reformulación; una decisión de requisito nuevo sigue WU-019. Sin proveedor
LLM nuevo, credenciales reales ni autorización runtime.

## Oráculos RED congelados

1. GAP SAT verificado sobre modelo pequeño produce entrada factible, guardas
   inactivas, digest de modelo y pregunta neutral; `semantic_status` sigue
   `UNINTERPRETED` y `authority` es `PROPOSAL_ONLY`.
2. GAP UNSAT o UNKNOWN no fabrica escenario; testigo ausente, alterado o no
   revalidado produce `INCONCLUSIVE`.
3. La existencia de GAP no se presenta como `NO_OUTPUT`, fallo observado del
   producto o requisito faltante ya confirmado.
4. La skill ofrece fuera de alcance, excepción válida, requisito faltante,
   comportamiento prohibido y error de modelo como hipótesis para decisión
   humana; no ratifica por silencio.

RED pertinente → implementación mínima → GREEN/regresión → RDD exacto → Git.

## Evidencia RED

La primera invocación con `python3` de base terminó exit 1 porque no tenía Z3;
es un problema del entorno y no cuenta como RED. Con el venv de CI instalado,
los casos SAT/UNSAT fallaron por ausencia de `gap_interpretation` y el control
negativo por módulo `gap_scenario` ausente; 3 errores, exit 1.

## Evidencia GREEN y regresión

Tres controles focalizados, exit 0. `PATH=/tmp/ci-runtime-venv/bin:$PATH bash
ci/run_quality.sh` terminó exit 0: 55 CI, 130 supervisor, 62 QA y 357
requisitos. No se usó un LLM ni se interpretó un dominio real; el paquete
permanece `PROPOSAL_ONLY` y el equipo objetivo sigue NOT_RUN.
La regresión se repitió sobre el árbol final tras marcar que el escenario es
un solo testigo y no todas las combinaciones: mismos conteos y exit 0.
