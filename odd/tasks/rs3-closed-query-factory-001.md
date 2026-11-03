# RS3-WU-CLOSED-QUERY-FACTORY-001

## Alcance

Corresponde a T019–T020 del paquete RS3-HANDOFF-001, dentro del analizador
booleano existente. Extrae la construcción de las cuatro consultas conocidas
a una factoría cerrada. No añade un ejecutor Z3, un estado de autoridad ni
una semántica nueva de `production_ready`.

## Oráculos y RED

- RS3-AT-001/002: `NO_OUTPUT` construye únicamente
  `D ∧ ¬∃(todos los outputs):C`; el mutante `D∧C∧¬∃outputs:C` no se admite.
- RS3-AT-004: la factoría toma la lista completa de outputs del modelo;
  no acepta una lista de cuantificación enviada por el cliente.
- RS3-AT-005/008: `GAP`, `NO_OUTPUT` y `RULE_CONSISTENCY` conservan estados
  distintos; la última es existencial, no prueba universal.
- Una operación arbitraria o una cadena en lugar del enum exacto se rechaza.
- La CLI conserva estructura, códigos de salida y presupuestos. Los tests
  nuevos deben fallar antes de crear la factoría; los de regresión pasan tras
  integrarla.

## Tareas

1. Crear tests de factoría y capturar RED pertinente.
2. Implementar factoría pura de fórmulas y conectarla al analizador existente.
3. Ejecutar GREEN y regresiones, revisar RDD exacto y respaldar tras gates.

La intención humana y la validez del producto siguen fuera del alcance.
