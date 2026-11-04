# WU-RS3-SOURCE-REQUEST-CONSTRUCTION-011

## Objetivo y precedencias

Depende de WU-RS3-SOURCE-SNAPSHOT-BINDING-010. Impedir que el adaptador envíe
al proveedor bytes de solicitud que diverjan de la `SourceSnapshot` que después
usa para validar la respuesta. La unidad solo conecta la instantánea del
llamador con el transporte local; no autentica su origen humano.

## Alcance y contrato

El adaptador construye internamente una solicitud JSON UTF-8 determinista con
versión, `source_ref` y `source_text`. `invoke()` no acepta payload externo. Los
bytes conservan el texto exacto, se acotan antes de lanzar el proceso y nunca
se registran ni aparecen en el resultado. Una fuente que exceda el límite de
transporte se rechaza antes del lanzamiento. Los errores de proveedor y el
bloqueo por limpieza incierta conservan sus contratos anteriores.

Fuera de alcance: capturar texto desde un terminal humano, fuentes persistentes,
red, credenciales, D03/D05 y permiso de producción. Cualquier llamador puede
construir una instantánea; esta unidad no verifica quién la construyó.

## Oráculos RED congelados

1. El proceso proveedor recibe un JSON con versión y fuente idéntica a la
   instantánea; el resultado solo admite una propuesta que coincida con ella.
2. Pasar bytes alternativos a `invoke()` falla; no existe segundo canal de
   fuente suministrado por el llamador.
3. Una instantánea cuyo JSON escapado supera 8 KiB se rechaza antes del launch.
4. El resultado no contiene el texto fuente ni otorga autoridad humana.
5. Regresión: timeout, señal, salida no válida y limpieza incierta conservan
   su clasificación previa.

RED → cambio mínimo → GREEN y regresión → RDD exacto → respaldo Git y CI.
Los fixtures usan exclusivamente texto sintético.

## Evidencia local RED/GREEN

- RED observado: `python3 -B -m unittest discover -s skills/requerimientos-socraticos/tests -p test_rs3_source_request_construction.py -v` terminó exit 1: dos errores por `invoke()` sin `request_bytes` y un fallo porque se admitía un payload alternativo.
- GREEN focalizado: 3 tests nuevos, 7 del adaptador y 4 de vinculación de instantánea terminaron OK.
- Regresión: `PATH=/tmp/ci-runtime-venv/bin:$PATH /tmp/ci-runtime-venv/bin/python -B -m unittest discover -s skills/requerimientos-socraticos/tests -q` terminó exit 0, 338 tests OK.
- CI local: `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh` terminó exit 0: 55 CI, 120 supervisor, 62 QA y 338 requisitos.
