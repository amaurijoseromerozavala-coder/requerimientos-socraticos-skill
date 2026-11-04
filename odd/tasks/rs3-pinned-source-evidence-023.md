# WU-RS3-PINNED-SOURCE-EVIDENCE-023

## Objetivo y precedencias

Continuar WU-022: verificar que cada cita de un glosario propuesto corresponde
exactamente a un intervalo de bytes de un archivo regular en un commit Git
completo fijado. No leer el worktree del candidato. El contenido sigue siendo
propuesta semántica y no confirma autoría ni intención humana.

## Alcance

Glosario `rs3-gap-glossary/v2`: cada entrada añade offsets de bytes del
fragmento. `--source-repo` y `--source-commit` deben ir juntos; el commit es
OID completo de acuerdo con el formato Git real. Leer objetos sin extracción,
sin lazy fetch, sin replace objects y con límite de 64 KiB por blob. Rechazar
symlinks, paths inseguros, OIDs/referencias simbólicas, tamaño excesivo y texto
que no coincida byte a byte. Indicar algoritmo Git y SHA-256 del blob.
El formato v1 sigue produciendo preguntas propuestas sin procedencia Git;
v2 sin snapshot no produce pregunta. La fuente Git fijada no es una firma.

## Oráculos RED congelados

1. Commit fijado conserva la cita original aunque se edite el worktree luego;
   la salida reporta bytes verificados, commit y digest del blob, sin ratificar
   semántica o autoría.
2. Cita autoconsistente pero distinta de los bytes Git se rechaza.
3. `HEAD` como referencia, flags incompletos o v2 sin snapshot no se promueven.
4. Un symlink en el árbol no se lee como fuente regular.

RED pertinente → implementación mínima → GREEN/regresión → RDD exacto → Git.

## Evidencia RED

Dos controles positivos fallaron con exit 2 por flags desconocidos, antes de
añadir la implementación. Los rechazos coincidentes con los casos negativos
de ese estado no se contaron como prueba del comportamiento nuevo.

## Evidencia GREEN y regresión

`/tmp/ci-runtime-venv/bin/python -B -m unittest discover -s skills/requerimientos-socraticos/tests -p test_rs3_pinned_source_evidence.py -v`: 3 tests, OK.
`PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh`: exit 0; CI 55,
supervisor 130, QA 62 y requisitos 367 tests, OK. No se ejecutó calibración
en el hardware i3/WSL del usuario.

## Corrección RDD R3-001

Gentle AI detectó que Python trunca un slice cuyo `end` supera la longitud real
del blob. Un control negativo con un blob sin LF y `end > len(blob)` reprodujo
el defecto: el proceso devolvió 0 cuando debía rechazarlo. Después de exigir
`end <= len(raw)`, el mismo test pasó (3 tests focales, OK). La regresión
completa volvió a pasar (55 CI, 130 supervisor, 62 QA, 367 requisitos).
La validación RDD del candidato corregido sigue pendiente.
