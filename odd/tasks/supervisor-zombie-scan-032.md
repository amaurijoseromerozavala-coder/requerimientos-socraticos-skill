# WU-SUPERVISOR-ZOMBIE-SCAN-032

## Objetivo y alcance

Una regresión de WU-031 encontró `STOPPED/GROUP_CLEANUP` en el test existente
`test_two_real_runs_reuse_only_after_durable_receipts`: el entorno presenta
más de 4.100 procesos zombi ajenos, y `_group_still_exists` devuelve `True`
al exceder 4.096 entradas antes de terminar el escaneo. Corregir solo ese
falso positivo, manteniendo fail-closed cuando haya miembros vivos o la
observación sea realmente incompleta.

## Oráculos RED congelados

1. Con más de 4.096 zombis ajenos y ningún miembro vivo del grupo objetivo,
   el grupo se informa vacío.
2. Un miembro vivo después de ese prefijo se detecta.
3. Si se rebasa el presupuesto físico de inspección, la respuesta sigue
   siendo incierta; no inventar grupo vacío.
4. El test de dos corridas reales del journal vuelve a EXITED y la suite de
   calidad completa pasa.

No generar procesos zombi para ensayar; usar registros `/proc` sintéticos
para el falsador y la suite existente para el control material acotado.
No alterar contratos de autoridad ni estados de QA. RED → GREEN → RDD
exacto → GitHub.

## Evidencia

RED focal: 3 tests, 1 fallo pertinente (exit 1): 4.100 zombis ajenos se
clasificaban como grupo vivo. GREEN focal más prueba real de dos corridas:
4 tests, exit 0. Regresión `ci/run_quality.sh`: exit 0; CI 55, supervisor
133, QA 62 y requisitos 391 tests. El equipo i3/WSL objetivo no estuvo
disponible para calibración (NOT_RUN). La causa observada en este entorno
fue un total de 4.125 procesos, de ellos 4.117 zombis al sondear, superior
al techo previo de 4.096 entradas.
