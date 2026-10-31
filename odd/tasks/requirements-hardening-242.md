# Requerimientos socráticos 2.4.2

Objetivo: mejoras aceptadas tras contraste QA; solo herramientas de la skill.
Entrega local sin CI, producción, cambios de permisos ni commits de producto.
Runner: venv local, unittest; cada ensayo en subproceso con timeout exterior.

## Specs

S1. «Entonces solo mejora lo que pasé tu analisis»: unificar supervisión de
procesos del analizador y vía Git; plazo, entrada/salida acotadas, limpieza
de procesos propios y control Linux de hijo directo ante pérdida del padre.
No se promete tiempo real ni aislamiento universal de descendientes/cuenta/kernel.

S2. Validar los mismos bytes ligados a OIDs Git SHA-256, incluidas entrevista,
diseño y recibos; proveedor en memoria sin documentos candidatos temporales.
Mantener APIs y diagnósticos existentes; preservar límites y rechazo de rutas.

S3. Conservar 0600, CI diferido, BLOCKED_GLOBAL_ENFORCEMENT y autoridad humana.
Registrar RED/GREEN real, regresión, revisión independiente y RDD nativo.
No simular ensayos del i3/WSL ni mediciones de hardware.

## Tasks

- T1 [S1] inline: inspección tras interrupción y corregir fixture pendiente — DONE.
- T2 [S1] delegado: supervisor compartido y regresión analizador — DONE; RED/GREEN en audit.
- T3 [S2] delegado: fuentes documentales y dependencias en memoria — DONE; 43+18 tests.
- T4 [S1,S2] inline: integrar objetos Git y worker acotado — DONE; 3 integración y 5 framing.
- T5 [S3] inline: regresión, revisión independiente, RDD y exportación — DONE; 168tests,35 reproducción independiente,10diff, recibo nativo exacto.

## Log

L1. Usuario: «Entonces solo mejora lo que pasé tu analisis».
2026-10-28: «Continua», «Intenta ahora», «Comprueba ahora», «Comprueba».
Cloud vuelve conectado y consola responde. Procesos visibles: servicios del
entorno, Codex y ps; no aparece el unittest anterior. Esto no demuestra su
historia de terminación. test_process_supervision.py existía, sin implementación.
Su mock Popen se corrigió antes de ejecutar: falla explícitamente si intenta
crear proceso, evitando que un PID simulado llegue a señales reales. RED previo
interrumpido no se usa como resultado válido. No se atribuye causa a la caída.

2026-10-28: regresión completa168tests OK, 6.536s, límite exterior45s.
La prueba histórica de extracción se adaptó a colección de bytes: ahora verifica
que ni interrupción ni reutilización creen un pool de candidato. No se cambió
el falsador para esconder un fallo: la ausencia de archivos es el cambio solicitado.
La prueba específica de muerte del padre Git se añadió después de integrar;
no se presenta como RED previo. Linux observó terminación y recogida del
consumidor propio; no es medición i3/WSL. Revisión independiente en curso.

2026-10-28: CLI Gentle AI real validó un commit documental sintético por stdin.
RDD inicial con logs íntegros excedió presupuesto; no creó autoridad. Nuevo
candidato completo de código/schemas/contratos/tests, con logs externos intactos,
creó review-c7092036da2c5504, riesgo alto,4lentes, approved y acknowledged.
Identidad: sha256:4e5755c816af2357d5f9e2f60235e0f3b2f27f108bfcb1d3adab8c2d11f4dc1b.
87archivos seleccionados idénticos al árbol revisado. Version2.4.2; límites,
0600, CI diferido y BLOCKED_GLOBAL_ENFORCEMENT conservados. Informe posterior
RESULTADO.md y exportaciones se entregan fuera del candidato aprobado.

2026-10-28: contraste QA posterior sin modificar skill: archivo30MiB no admisible
(límite8MiB); fixture167bytes rechazado FILE_SIZE_LIMIT antes de cuerpo. Memoria
virtual/RSS y presupuesto agregado siguen pendientes; no se adoptan mandatos QA.
Se preservan evidencia35ensayos independientes, alcance estático RDD y CI diferido.
Reporte adicional: docs/skill-audit/requirements-hardening-242/CONTRASTE-QA-POSTERIOR.md.
