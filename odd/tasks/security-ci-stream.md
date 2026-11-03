# WU-SEC-CI-STREAM-001 — captura de suites antes de persistencia

## Ruta y frontera

`ci/run_quality.sh` invoca cuatro suites por `run_suite`. El shell hoy abre
`$ci_scratch_dir/$label.stdout` y `.stderr` antes de ejecutar la suite; un
fallo muestra fragmentos de esos archivos al runner de CI. Esta unidad cambia
solo esa ruta: pipes anónimos → buffers de memoria acotados → saneamiento de
ambos canales → archivos temporales 0600 → resumen o diagnóstico acotado.
Los códigos de salida de suites se conservan. Los fallos de supervisión,
saneamiento, capacidad o escritura deben cerrar la admisión sin salida cruda.

Los pasos `check_rdd_record.py`, sondeo de entorno, hijos que escriban sus
propios archivos y capturas hechas por servicios externos no forman parte de
esta frontera. No se proclama detección universal de secretos sin marcadores
reconocidos. Los originales históricos y las reglas de CI no se alteran.

## Oráculo RED/GREEN

Usar solo valores ficticios. Probar stdout, stderr, dos formas de `--token`,
valor dividido entre lecturas, copias entre canales, dato ordinario, exit no
cero, excepción del saneador, error de escritura y plazo/interrupción. Ningún
archivo bajo control ni salida del wrapper debe contener un valor reconocido
antes de sanear. Un valor ambiguo se rechaza sin archivo. En salida ordinaria
se conservan bytes y código de salida; una suite fallida jamás produce GREEN.
Las copias numéricas de un valor reconocido y los marcadores JSON precedidos
por texto de log se rechazan sin persistencia cuando no pueden sanearse con
certeza.

El lector retiene como máximo 1 MiB por canal. Si el límite se excede o no
confirma la recolección del hijo, no persiste una captura parcial. Se conserva
el plazo de 90 segundos y el límite virtual heredado del runner. Los tests no
usan carga artificial ni tokens reales.

## Tareas

1. Registrar RED en pruebas del capturador y del runner.
2. Implementar wrapper acotado en memoria; escribir solo bytes saneados.
3. Integrarlo en `run_suite`, manteniendo resumen y semántica fail-closed.
4. Ejecutar GREEN/regresiones, inspección de confidencialidad y RDD exacto.
