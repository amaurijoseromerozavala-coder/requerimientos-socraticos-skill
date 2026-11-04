# WU-RS3-ANALYSIS-TO-VIEW-027

## Objetivo y precedencias

Continuar WU-026 conectando la salida JSON real de `analyze_logic.py` con la
vista HTML de solo lectura, sin extracción manual de `gap_questions`. Un modo
explícito `--report` debe aceptar archivo regular o stdin (`-`) acotado.

## Alcance y límites

El adaptador exige consistencia entre `provenance.model_sha256`, el paquete
`gap_questions` y los testigos propuestos en `gap_region.samples` o
`gap_interpretation`. No reejecuta Z3, no autentica el reporte y no permite
capturar decisiones. Mantener el modo de paquete existente. No ensayar
navegador ni hardware objetivo inaccesible.

## Oráculos RED congelados

1. Un reporte producido por el analizador con glosario válido se convierte en
   HTML escapado mediante CLI `--report`, sin extracción manual.
2. Reporte con digest o asignación de pregunta alterados no produce HTML.
3. Reporte sin testigo revalidado o sin preguntas propuestas se rechaza.
4. Entrada por stdin, JSON inválido o exceso de bytes falla sin HTML parcial.

RED pertinente → GREEN/regresión → RDD exacto → Git.

## Evidencia RED/GREEN

RED focal: el analizador produjo un reporte real, pero el consumidor rechazó
`--report` tanto con archivo como con stdin (2 fallos; los casos negativos
no se contaron como prueba del contrato nuevo). GREEN focal: 3 tests, exit 0;
incluye reporte real, archivo/stdin y mutaciones de digest, asignación y
marca de revalidación.
Regresión integral `ci/run_quality.sh`: exit 0; CI 55, supervisor 130,
QA 62 y requisitos 380 tests, OK. Hardware objetivo: NOT_RUN.
