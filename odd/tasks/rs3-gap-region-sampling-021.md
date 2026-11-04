# WU-RS3-GAP-REGION-SAMPLING-021

## Objetivo y dependencias

Extender WU-020: explorar más de una combinación de `D ∧ ¬G` sin enumerar
indiscriminadamente `2^32` entradas. El humano pidió continuar hacia el barrido
de brechas. El testigo individual sigue siendo una muestra; la interpretación
semántica y ratificación de un requisito continúan fuera del solver.

## Contrato y presupuesto

`--gap-samples N` optativo, entero 0..16, por defecto 0. Muestreo de modelos
Booleanos en orden lexicográfico con falso antes de verdadero, usando consultas
SAT por prefijo y cláusulas de bloqueo de asignaciones ya vistas. Comparte el
plazo total y el supervisor existente; `UNKNOWN` o vencimiento da
`INCONCLUSIVE`, nunca cobertura exacta. Solo `UNSAT` tras bloquear todas las
muestras observadas permite `EXACT_WITHIN_SUPPLIED_MODEL`. El límite de 16 es
un presupuesto operativo del muestreo, no un número de variables objetivo.
No sustituye la tabla exacta opcional existente para hasta 12 entradas.

## Oráculos RED congelados

1. Para un modelo de dos entradas con tres brechas, N=2 devuelve las dos
   primeras asignaciones en orden determinista, sin duplicados y estado
   `PARTIAL_LIMIT`; N=4 devuelve tres y `EXACT_WITHIN_SUPPLIED_MODEL`.
2. N=0 no ejecuta muestreo; N<0 o N>16 se rechaza antes del worker.
3. Cada muestra se revalida contra `D ∧ ¬G`, conserva modelo/origen y no
   adquiere semántica ni autoridad; salida incierta queda `INCONCLUSIVE`.
4. Una brecha de guardas no altera la semántica separada de `NO_OUTPUT`.

RED pertinente → implementación → GREEN/regresión → RDD exacto → Git.

## Evidencia RED

Cuatro controles nuevos terminaron exit 1 antes de la implementación: tres
rechazos de `--gap-samples` por argumento ausente y un módulo `gap_region`
ausente. La ejecución usó el venv de CI con Z3 disponible.

## Evidencia GREEN y regresión

Cuatro controles focalizados, exit 0. La regresión
`PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh` terminó exit 0:
55 CI, 130 supervisor, 62 QA y 361 requisitos. El caso N=4 agota el pequeño
modelo sintético de tres entradas brecha; N=2 informa remanente. No se hizo
calibración del i3/WSL ni se estableció significado de dominio.
