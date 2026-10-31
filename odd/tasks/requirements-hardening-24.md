# Endurecimiento de requerimientos-socraticos

Extender skill existente; no crear QA ni activar CI/producción. Objetivo hardware no accesible.

## Specs
- S1: «Ok haz la skill»; precisión «La skill a endurecer es requerimientos socraticos».
- S2: «Si es posible conrigura los agentes para esta tarea con mayores capacidades».
- S3: «el sistema debe ser agnóstico al hardware pero debe correr eficientemente en mi hardware entonces debe tener un proceso para conocer en donde está alojado».
- S4: «Debe hacer un sondeo y calcular la capacidad de hardware para tener un valor de cobertura».
- S5: «Quiero uses en ese proceso método científico bungeano y falsacion de popper».
- S6: «Usar axiomas como filtro ... para definir las invariables de manera correcta».
- S7: «eran variables booleanas»; «Si 32 es un límite no una regla».
- S8: «Solo análisis; ejecución con autorización específica»; «no quiero CI todavia».

## Tasks
- T1 [S1,S5-S8] Actualizar contrato/metodología y manual de skill existente.
- T2 [S3,S4] Sondeo local limitado de lectura; procedencia y UNKNOWN.
- T3 [S4,S7] Analizador booleano de máximo32 variables totales, entradas/salidas separadas; consultas de factibilidad, cobertura y conflictos.
- T4 [S1,S8] Integración gentle-ai requirements, pruebas y regresión existentes.
- T5 [S2,S5,S6] Revisión formal independiente de riesgos matemáticos; RDD exacto.
- T6 [S1] Registro/export completo, versión y estado honesto.

## Log
L1: «La skill a endurecer es requerimientos socraticos» reemplaza alcance inicial
erróneo QA. No se creó código QA. Venv solver aislado puede reutilizarse para
requirements; no modifica entorno del PC ni instala Lean.
L2: Mayores capacidades aplicadas por agente en esta tarea, sin cambiar configuración
económica persistente. No código del producto usuario, CI ni estrés físico.
L3: Nombre de venv inicial qa-inquisidor es historial técnico; mover a ubicación
neutral antes de integrar. Modelos analizados no prueban verdad del significado
humano ni hardware. Sondeo no autoriza calibración ni ejecución del PRD.

L4: T1-T4 completadas: helpers, schema, contrato y launcher. 113tests OK (101regresión+7lógica+5entorno), ejemplos públicos y schemas verificados. Revisión Astra:11tests+7modelos; seguimiento5tests+6fixtures cuotas. Sin cargas/Lean/PC. Candidato congelado validation2.4 PRE_REVIEW. T5/T6 RDD/export pendientes.

L5: RDD cuatro lentes detectó selección de intérprete explícito ignorada; RED observado y3tests nuevos; corregido sin fallback explícito.116tests OK. Corrección nativa capturada/validada, approved/acknowledged review-afc5fe83dd67b2e3, target sha256:40d3bd2a3a5c4be2be8a0c62f0acbd70d8c2864cbf93f26411206953f891a5b5. T1-T6 completadas en alcance local. Export JSON/ZIP creados y archivos comparados al árbol revisado. Sin Lean ni aceptación i3/WSL ni CI.
