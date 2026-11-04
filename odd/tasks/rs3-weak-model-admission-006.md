# WU-RS3-WEAK-MODEL-ADMISSION-006

## Objetivo y precedencia

Crear una compuerta local y acotada para propuestas JSON generadas por modelos
lingüísticos débiles. Precede CandidateIR provisional y el oráculo semántico de
WU-RS3-SEMANTIC-ORACLES-005. Vincula las propuestas RS3-REQ-036, 038, 039,
040, 043 y la campaña adversarial del PRD; no adopta el paquete entero.

## Alcance

Aceptar solo bytes UTF-8 JSON bajo 16 KiB y profundidad 8, sin claves
duplicadas ni constantes no JSON. Validar el objeto con CandidateIR y emitir
uno de cuatro estados cerrados: REJECT_INPUT, NEEDS_CLARIFICATION,
PROPOSED_FOR_REVIEW o INFRA_FAILURE. La salida nunca confirma decisiones ni
autoriza acciones.
El corpus de pruebas usa exclusivamente datos sintéticos y no llama a
proveedores. No se incorpora DSPy, entrenamiento, credenciales o servicio.

## Oráculos RED congelados

- JSON inválido, truncado, demasiado grande/profundo, UTF-8 inválido,
  duplicados, NaN, campos de permiso, confirmación humana o AST libre deben
  producir REJECT_INPUT sin eco del payload.
- Inversión de operador, cambio de modalidad, fuente con instrucciones, texto
  no admitido y negación deben permanecer NEEDS_CLARIFICATION sin AST.
- Solo la propuesta sintética coherente puede llegar a PROPOSED_FOR_REVIEW;
  incluso ella debe conservar autoridad no concedida y ejecución no autorizada.
- Una excepción del parser o un fallo de recursos no debe transformarse en
  PROPOSED_FOR_REVIEW.

RED observado: `ModuleNotFoundError: weak_model_gate` al ejecutar los tests
fijados antes de implementar. GREEN focalizado: 3 tests, incluido corpus de
14 casos sintéticos. GREEN final: 324 tests de Requerimientos Socráticos y
52 tests CI locales pasaron; uno de CI quedó omitido explícitamente por falta
del ZIP externo. RDD se registra después de congelar el candidato.
Los casos ensayados no prueban seguridad universal. RDD nativo del candidato
exacto; respaldo Git después del reconocimiento.

## Recursos y límites

Solo stdlib y el preflight ya existente; no estrés, red ni procesos hijos. El
corpus no registra secretos reales. D03/D05 y producción permanecen bloqueados.
