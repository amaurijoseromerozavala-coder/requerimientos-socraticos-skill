# WU-RS3-GAP-QUESTION-DATA-BOUNDARY-025

## Objetivo y precedencias

Continuar WU-024. Separar el texto de pregunta y opciones, definidos por el
sistema, de las frases de un glosario propuesto que pueden contener
instrucciones adversariales. El formato JSON debe transportar cada frase como
dato con variable, valor booleano y fuente asociada. La UI futura debe
presentar estos datos como texto literal y no como instrucción ejecutable.

## Alcance y límites

Modificar solo el constructor de preguntas, sus pruebas y la referencia de
uso. No afirmar protección universal contra prompt injection: un consumidor
posterior que concatene datos no confiables en un prompt puede reabrir la
brecha. No cambiar solver, procedencia Git, D03/D05 ni autoridad humana.

## Oráculos RED congelados

1. Una frase adversarial del glosario no aparece en `question.text` ni cambia
   la pregunta y opciones fijas; permanece íntegra como dato estructurado.
2. Las frases estructuradas corresponden exactamente a los valores booleanos
   revalidados y conservan variable/fuente para corrección humana.
3. Estado y autoridad siguen `PROPOSED_UNVERIFIED`/`NOT_GRANTED`; un glosario
   ausente o inválido no produce pregunta.

RED pertinente → implementación mínima → GREEN/regresión → RDD exacto → Git.

## Evidencia RED/GREEN

RED focal: una frase adversarial cambió `question.text`, 1 fallo de 2 tests;
el control de glosario ausente pasó. GREEN focal: 2 tests, OK. Dos pruebas
anteriores que exigían frases incrustadas en `text` fallaron al cambiar el
contrato; se actualizaron para exigir las mismas frases y valores en el campo
estructurado, sin eliminar sus comprobaciones. Regresión acotada: 16 tests,
OK. Regresión integral `ci/run_quality.sh`: exit 0; CI 55, supervisor 130,
QA 62 y requisitos 373 tests, OK. Hardware objetivo: NOT_RUN.
