# WU-RS3-SUPERVISED-ANALYSIS-VIEW-028

## Objetivo y precedencias

Continuar WU-027: ofrecer una entrada local única que invoque el analizador
con comando fijo, plazo exterior y captura acotada; solo si el hijo sale 0,
entrega un informe completo, y su limpieza queda confirmada, convertirlo en
HTML de solo lectura. No aceptar reportes suministrados por el agente en esta
entrada. Reutilizar `process_supervision.run_supervised`.

## Alcance y límites

Un modelo y glosario locales son entradas no confiables; el analizador
conserva sus propias admisiones y límites. El invocador exterior controla al
hijo directo y observa su estado, sin contener descendientes arbitrarios ni
garantizar plazos bajo un SO no responsivo. No generar archivos persistentes,
no capturar decisiones, no tocar D03/D05 ni producción. Sin ensayo i3/WSL.

## Oráculos RED congelados

1. Análisis real válido produce HTML escapado a través de la entrada única.
2. Hijo que duerme más que el plazo exterior es terminado y recolectado; no
   se emite HTML, sin inferir causa OOM.
3. Exit no cero, salida truncada o limpieza incierta bloquean HTML aunque
   exista JSON aparente de éxito.
4. Entrada o reporte inválidos producen fallo explícito, sin HTML parcial.

RED pertinente → GREEN/regresión → RDD exacto → respaldo Git.

## Evidencia RED/GREEN

RED focal: la suite no pudo importar `analyze_to_view` porque la entrada
supervisada no existía (exit 1). GREEN focal: 4 tests, exit 0. El control de
hijo detenido utilizó un proceso real que duerme, observó el plazo, la
recolección por `waitpid` y la ausencia de HTML; limpieza incierta y salida
truncada se inyectaron como fallos de contrato, sin pretender reproducir un
estado D del kernel. Regresión integral `ci/run_quality.sh`: exit 0;
CI 55, supervisor 130, QA 62 y requisitos 384 tests. El hardware i3/WSL
objetivo no estuvo disponible para calibración física (NOT_RUN).
