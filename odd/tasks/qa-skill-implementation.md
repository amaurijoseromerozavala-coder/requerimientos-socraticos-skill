# Implementación local de QA Inquisidor

Crear skill y herramientas locales; no producción ni CI. Hardware objetivo no accesible.

## Specs
- S1: «Ok haz la skill».
- S2: «el sistema debe ser agnóstico al hardware pero debe correr eficientemente en mi hardware entonces debe tener un proceso para conocer en donde está alojado».
- S3: «Debe hacer un sondeo y calcular la capacidad de hardware para tener un valor de cobertura».
- S4: «Quiero uses en ese proceso método científico bungeano y falsacion de popper».
- S5: «Si 32 es un límite no una regla»; «eran variables booleanas».
- S6: «Solo análisis; ejecución con autorización específica»; «no quiero CI todavia».
- S7: «ANALYSIS / Code review. TEST PLAN / Test strategy. VERIFICATION / Results.»; «responde en español».
- S8: «siempre analizar todo el sistema objetivo ... no solo últimos cambios»; «mcp firts y skills firts».

## Tasks
- T1 [S1,S4,S6-S8] Contrato de skill, esquema de datos y manual.
- T2 [S2,S3] Sondeo local de lectura con capas/UNKNOWN, sin prometer capacidad física.
- T3 [S3,S5] Núcleo booleano acotado y consultas de dominio/cobertura/conflictos, con fallback explícito.
- T4 [S3,S4,S7] Informes JSON+Markdown, ejemplo y puente Lean separado.
- T5 [S1-S8] Pruebas negativas y regresión de interfaz pública.
- T6 [S1] Registro local, exportación y RDD de candidato exacto.

## Log
L1: «Ok haz la skill» autoriza ahora implementar y registrar la skill local.
L2: No autoriza CI, producción, sondeo remoto del PC ni cargas intensivas.
L3: Se preservan requerimientos2.3.0 y borradores históricos. Lean queda capacidad
externa: no se inventa una prueba Lean ejecutada ni equivalencia con DO-178C.
L4: SUPERSEDED: humano precisó «La skill a endurecer es requerimientos socraticos».
No se escribió código QA. Continuación en odd/tasks/requirements-hardening-24.md.

L5.2026-10-29: REANUDADO por solicitud humana de construir QA con Gentle AI,
seguida de «No quiero happy paths quiero la skill funcione en la realidad».
Skill requerimientos2.4.6 cargada, intercambio real Q006–008 y decisión literal
«Delegas esos juicios técnicos a la skill dentro de criterios explícitos; las
excepciones vuelven a ti.» Se creó skill local0.1.0-alpha de análisis y checker
documental, sin ejecutor de aplicación. Registro Gentle real muestra2skills.
Tres findings independientes reproducidos RED antes de corregir; suite final
43OK en coordinador y revisor más4probes independientes. Sin ensayos físicos,
sin CI/producción ni claim de calidad integral. Requerimientos no se modificó.
RDD del nuevo candidato requiere consentimiento nativo por riesgo medio.
Detalles y continuación canónica del trabajo: odd/tasks/qa-inquisidor-prd.md.
