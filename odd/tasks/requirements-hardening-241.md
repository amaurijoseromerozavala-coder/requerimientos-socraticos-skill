# Correcciones aceptadas para requerimientos-socraticos 2.4.1

Solo correcciones locales autorizadas; no CI, cargas intensivas ni aceptación física.

## Specs
- S1: «Realiza las correcciones que pasan tu análisis».
- S2: «supervisión externa del análisis, control de anidamiento antes de decodificar JSON y registro explícito del intérprete y sus dependencias» (alcance comunicado para ejecución).
- S3: «el sistema debe ser agnóstico al hardware pero debe correr eficientemente en mi hardware».
- S4: «Solo análisis; ejecución con autorización específica»; «no quiero CI todavia».

## Tasks
- T1 [S1,S2] Preflight JSON iterativo consciente de cadenas/escapes; tests RED/GREEN.
- T2 [S1,S2] Separar worker de supervisor, plazo exterior y cierre/espera de procesos propios; Linux vínculo de vida al padre con alcance declarado.
- T3 [S1-S3] Intérprete explícito/fijado y procedencia de runtime; perfil con host UNKNOWN y no admisión automática.
- T4 [S1-S4] Pruebas públicas acotadas, regresión, revisión independiente y RDD exacto.
- T5 [S1] Actualizar skill/documentación y exportación completa, sin alterar recibos2.4.

## Log
L1: «Realiza las correcciones que pasan tu análisis» autoriza implementación local.
L2: El caso JSON profundo se manejó estructuradamente en2.4; preflight es defensa
adicional, no corrección de un segfault observado. Timeout interno era soft,
no se prometió plazo de tiempo real. No se acepta predicción QA como resultado.
L3: Supervisión exige SO responsivo; Linux PDEATHSIG para worker directo, no garantía
universal de descendientes, kernel o contención ante procesos de misma cuenta.

L4: Preflight6tests, supervisor9tests,131tests totales OK. Grupo con líder terminado: RED .82077s para .1s y corrección observada; revisor independiente confirma .10049s y cierre; holder fuera grupo1.10231s cleanupINCOMPLETE en fixture recogido porharness. Guard agregado no-POSIX bloquea worker y tiene test local. Sin promesas Windows/macOS ni hardware. T1-T3 completas, T4/T5 RDD/export pendientes.

L5: RDD cuatro lentes detectó compatibilidad INVALID_INPUT; RED observado, clase diferenciada corregida,132tests OK. Corrección validada y approved/acknowledged review-65b72cd5614b2220, target sha256:a587a67b793c15b95c7cf28b20150eef275cf6a8dc7105932adf26e314cf716a. T1-T5 completadas en alcance local, sin aceptación i3/WSL ni Lean/CI. ExportJSON/ZIP creados y fuentes comparadas al árbol revisado.
