# WU-RS3-GAP-QUESTION-READONLY-VIEW-026

## Objetivo y precedencias

Continuar WU-025 con un consumidor ejecutable mínimo de `scenario_clauses`:
una vista HTML estática para lectura humana. No hay UI previa en el repositorio.
El texto del glosario debe renderizarse como contenido literal, nunca como
markup, script, enlace ni instrucción de control. La pregunta permanece fijada
por el módulo y ninguna respuesta se captura o confirma.

## Alcance

Crear un renderizador/CLI local de solo lectura con entrada JSON acotada,
validación cerrada del paquete y salida HTML únicamente por stdout. No iniciar
servidor, navegador, sesión, cuenta, autenticación ni gate D03/D05. No afirmar
que el HTML pruebe la seguridad de cualquier navegador, LLM o futura UI.

## Oráculos RED congelados

1. Un `proposed_phrase` con `<script>`, atributos HTML y entidades permanece
   visible como texto literal; no crea nodos activos ni modifica la pregunta.
2. `text` alterado, autoridad distinta de `NOT_GRANTED`, fuentes inconsistentes
   o asignación alterada se rechazan antes de emitir HTML.
3. La salida no contiene formularios, scripts, enlaces ni recursos externos.
4. Entrada mayor que la cota o JSON inválido da error sin HTML parcial.

RED pertinente → GREEN/regresión → RDD exacto → respaldo Git.

## Evidencia RED/GREEN

RED focal: la suite no pudo importar `render_gap_questions` porque el consumidor
no existía (exit 1). GREEN focal: 4 tests, exit 0, incluidos HTML adversarial,
rechazo de claims inconsistentes, límite de entrada y CLI positivo.
Regresión integral `ci/run_quality.sh`: exit 0; CI 55, supervisor 130,
QA 62 y requisitos 377 tests, OK. Hardware objetivo: NOT_RUN.

## Corrección RDD R3-001

La revisión detectó que una mutación de `sources.A.source_text` sin actualizar
`source_sha256` era aceptada por la vista. El nuevo control negativo reprodujo
el defecto (exit 1: faltó `ValueError`). Tras comprobar presencia, formato y
digest del texto, los 4 tests focales pasaron. La regresión integral volvió
a pasar (55 CI, 130 supervisor, 62 QA y 377 requisitos). La validación RDD
del candidato corregido sigue pendiente.
