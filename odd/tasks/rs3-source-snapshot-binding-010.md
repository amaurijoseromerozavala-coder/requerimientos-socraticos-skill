# WU-RS3-SOURCE-SNAPSHOT-BINDING-010

## Objetivo y precedencia

Vincular la propuesta devuelta por el proveedor local al texto y referencia
fijados por el llamador **antes** de lanzar el proceso. Depende de
WU-RS3-WEAK-MODEL-ADMISSION-006 y WU-RS3-LOCAL-PROVIDER-ADAPTER-008. Responde
a la brecha de trazabilidad RS3-REQ-036/047 sin aceptar esos requisitos.

## Alcance

Crear una instantánea inmutable y acotada del texto/ref suministrados por un
llamador confiable; el adaptador la exige en su constructor. La compuerta JSON
compara ambos campos exactos después de validar el CandidateIR y antes de
emitir PROPOSED_FOR_REVIEW. Una diferencia produce REJECT_INPUT, no AST.
Mantener la admisión directa sin snapshot como análisis **no vinculado**, sin
autoridad ni ejecución. No añadir credenciales, cuentas, fuentes reales ni
servicios cloud.

## Oráculos RED congelados

1. Un proveedor devuelve una propuesta coherente pero cambia `P solo si Q` por
   `P si Q` y ajusta kind/direction: no puede pasar la frontera.
2. Cambiar únicamente `source_ref` tampoco pasa.
3. El adaptador no se construye sin snapshot válido; la instantánea no puede
   mutarse después de crearla.
4. Ninguna salida debe incluir el texto fuente bruto ni convertirse en
   HUMAN_CONFIRMED o execution_authorized=true.
5. Una salida congruente mantiene PROPOSED_FOR_REVIEW y el comportamiento
   previo de plazos/errores/limpieza.

RED antes de corregir; GREEN focalizado y suites afectadas; RDD del candidato
exacto, seguido de respaldo Git. Los tests usarán solo textos sintéticos.

## Evidencia RED/GREEN local

- RED: `python3 -B -m unittest discover -s skills/requerimientos-socraticos/tests -p test_rs3_source_snapshot_binding.py -v` terminó exit 1: `ModuleNotFoundError: No module named 'source_snapshot'`.
- GREEN focalizado: la misma orden terminó exit 0, 4 tests OK. El test legado del adaptador necesitó recibir la nueva instantánea obligatoria; su suite terminó con 7 tests OK tras esa adaptación explícita.
- Regresión amplia: `PATH=/tmp/ci-runtime-venv/bin:$PATH /tmp/ci-runtime-venv/bin/python -B -m unittest discover -s skills/requerimientos-socraticos/tests -q` terminó exit 0, 335 tests OK. El primer intento con `python3` del sistema carecía de `z3-solver` y no es evidencia de regresión del candidato.

## Frontera de confianza

La instantánea autentica **nada** por sí sola: cualquier llamador con acceso a
la API puede construirla. Solo demuestra correspondencia entre salida del
modelo y bytes del llamador. La captura del verdadero texto humano, D03/D05 y
producción permanecen fuera de alcance y bloqueados.
