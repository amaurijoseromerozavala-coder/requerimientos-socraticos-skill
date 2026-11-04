# WU-RS3-GAP-GLOSSARY-GROUNDING-022

## Objetivo y precedencias

Continuar WU-021: vincular cada variable de un escenario de brecha con una
frase verdadera/falsa y fuente literal de glosario, para preparar una pregunta
socrática. El glosario es propuesto; no autentica fuente ni significado y no
ratifica nuevos requisitos. Depende del modelo formal y testigos revalidados.

## Contrato y alcance

`--glossary <json>` optativo y acotado a 64 KiB. Incluye `model_sha256` de los
bytes analizados y, para cada entrada, `when_true`, `when_false`, `source_ref`,
`source_text` y SHA-256 de ese texto. Rechazar estructura/bytes inválidos;
glosario obsoleto o variable ausente produce `STALE_GLOSSARY`/
`NEEDS_GLOSSARY` sin pregunta semántica. El digest de texto demuestra solo
consistencia interna, no procedencia externa. Las muestras se cotejan con el
modelo ya validado, y la pregunta mantiene `PROPOSED_UNVERIFIED`.

No introducir un proveedor LLM, autenticación humana, navegador ni operaciones
del equipo objetivo. El agente podrá explicar la propuesta, pero la selección
y eventual requisito nuevo siguen WU-018/019.

## Oráculos RED congelados

1. Glosario completo con modelo coincidente produce frases por cada valoración,
   citas literales y digests, sin afirmar ratificación o verdad del dominio.
2. Falta una variable o cambia el SHA del modelo: no hay pregunta formulada.
3. Cambia un byte de `source_text` sin actualizar SHA: entrada inválida.
4. Sin glosario: `NEEDS_GLOSSARY`; ninguna brecha sintáctica recibe semántica
   automática.

RED pertinente → implementación → GREEN/regresión → RDD exacto → Git.

## Evidencia RED

Antes de implementar la opción, tres controles fallaron porque el launcher
rechazó `--glossary`; el caso sin glosario no contenía `gap_questions`.
Exit 1 con el venv de CI y Z3 disponible.

## Evidencia GREEN y regresión

Tres controles focalizados, exit 0. La regresión
`PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh` terminó exit 0:
55 CI, 130 supervisor, 62 QA y 364 requisitos. Los datos de glosario son
sintéticos y autoconsistentes; no se autenticó una fuente humana ni se ensayó
el i3/WSL. El árbol final se probó tras impedir reutilizar muestras descartadas.

## Hallazgo RDD R3-001 y corrección acotada

La lente de fiabilidad halló que una variable ausente devolvía
`NEEDS_GLOSSARY` antes de validar la integridad de las entradas presentes.
Falsador añadido con B ausente y texto A alterado: RED exit 1 (recibió 0
en lugar de 2). La corrección valida todas las entradas presentes antes de
clasificar faltantes; conserva el rechazo de nombres extra. Requiere nuevo
GREEN, regresión y validación RDD del candidato corregido.
