# WU-CI-OBSERVATION-009 — observación de grupo reproducible en CI

## Origen y alcance

El workflow Quality del commit `2c597d40babcf255eb5c975dc77d9ad7496ccf8b` se ejecutó en GitHub (run `41396305785`) y falló en `test_proc_read_error_latches_infra_lock`: esperaba `UNCONFIRMED`, observó `CONFIRMED`. El test inyectaba un fallo en `Path.read_text`, pero esa llamada dependía de que el grupo siguiera visible durante la carrera con el proceso auxiliar. La unidad corrige el oráculo de prueba, no cambia la política del supervisor ni los límites del runner.

## Criterios

- Inyectar directamente un fallo controlado en la observación del grupo después del lanzamiento, independientemente del tiempo de vida del auxiliar; comprobar `cleanup=UNCONFIRMED`, `status=INFRA_LOCK` y que una segunda ejecución no se lance.
- Conservar una comprobación separada de la ruta procfs: si la lectura de un miembro observado falla, la observación se considera incierta. No afirmar que se reprodujo un estado D del kernel.
- Ejecutar la suite completa local, luego RDD del candidato exacto y publicar solo con recibo aprobado/reconocido. Confirmar el siguiente run de GitHub antes de declarar CI verde.
- No usar carga artificial, cambios de permisos ni pruebas en el i3/WSL del propietario.

## Registro

- 2026-11-02: ODD abierto antes de editar el test. RED remoto: https://github.com/amaurijoseromerozavala-coder/requerimientos-socraticos-skill/actions/runs/41396305785 .
- El RED remoto está conservado como `remote-red.json` y `remote-red-excerpt.txt`: `CONFIRMED` observado frente a `UNCONFIRMED` esperado por un oráculo dependiente del tiempo de vida del auxiliar.
- GREEN local: `bash ci/run_quality.sh` produjo exit 0; 7 pruebas CI, 65 del supervisor, 62 de QA y 256 de Requerimientos. El núcleo no cambió.
- RDD y segunda ejecución remota pendientes.
