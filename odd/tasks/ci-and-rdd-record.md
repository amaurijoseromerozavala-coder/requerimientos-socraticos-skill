# WU-CI-RDD-008 — trazabilidad pública y CI acotado

## Mandato y alcance

El propietario pidió corregir el expediente RDD de WU-SUP-PRE-REAP-007 y activar CI. Esta unidad publica un addendum cronológico del resultado real de Gentle AI, sin editar la instantánea revisada en el commit `3656381`, y añade una verificación automática de calidad para el código actual. CI estaba diferido por decisión anterior; esta solicitud lo reanuda para este repositorio. No autoriza producción, pruebas de saturación ni cambios de protección/permisos de rama.

## Oráculos de aceptación

- El addendum identifica commit, árbol candidato, identidad RDD, linaje, resultado y reconocimiento exactos; declara que son un registro publicado después del candidato y que no es una firma independiente. El expediente previo conserva su `RDD: pendiente` como estado al preparar aquel candidato, y el README dirige al addendum.
- Un verificador acotado comprueba que el commit y el árbol Git mencionados existen y coinciden, que el marcador de consumo nativo corresponde al mismo objetivo/linaje, y que el addendum no atribuye al revisor pruebas que no ejecutó. Mutar un identificador debe producir RED.
- GitHub Actions ejecuta, sin secretos y con permisos mínimos, las suites de Requerimientos Socráticos, QA Inquisidor y Supervisor Local en Linux/Python 3.12, además del verificador del addendum. Tiempo y concurrencia son acotados; nada calibra el i3/WSL.
- El log normal del runner no excede 16 KiB; las salidas detalladas se conservan solo temporalmente durante la ejecución. Ante fallo, se muestran fragmentos acotados y el exit real.
- Validar localmente el flujo real, conservar RED/GREEN y comprobar la ejecución de GitHub Actions del commit publicado. Si falla, no afirmar CI verde.

## Secuencia

1. RED documental y de CI con falsadores antes de crear el addendum y el workflow.
2. GREEN local con dependencias fijadas y controles negativos, más regresiones relevantes.
3. RDD de Gentle AI del candidato exacto y reconocimiento; solo entonces commit y push.
4. Observar la ejecución de GitHub Actions y registrar su resultado en comunicación, sin alterar el candidato revisado.

## Registro

- 2026-11-02: ODD abierto antes de editar código, documentación o workflow.
- RED: las pruebas de contrato fallaron porque faltaban el verificador y el workflow (`contract-red.stderr`).
- RED documental: la prueba detectó README y AGENTS aún declarando CI diferido (`status-red.stderr`).
- RED de salida: el primer GREEN funcional pasó 388 pruebas, pero emitió 518537 bytes por stdout, superando la cota de 16 KiB; se corrige antes de RDD.
- RED de parada: al cambiar solo en una copia temporal el retorno del runner de código real a cero, `test_runner_failure` falló (`runner-negative-red.stderr`). El runner real conserva exit 7 en ese caso.
- RED de publicación: una línea histórica de README aún decía que no había workflow (`publication-red.stderr`); la documentación se alineó.
- GREEN local final: 7 pruebas de contrato, 64 del supervisor, 62 de QA y 256 de Requerimientos; exit 0, stdout 193 bytes y stderr vacío (`local-green.stdout`). El RDD y la ejecución remota aún no se han realizado.
