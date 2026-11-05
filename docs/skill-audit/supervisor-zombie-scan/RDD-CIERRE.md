# WU-SUPERVISOR-ZOMBIE-SCAN-032 — cierre RDD

Candidato staged de tres archivos: `sha256:aa23c40678711068a0b348a90c2cf77f5b9c30f4d64a9a55c79f8297bbe285e6`.
Gentle AI completó la lente de fiabilidad en el lineage
`review-b379f4a4b6093241`, aprobó y aceptó su reconocimiento exacto. Este
recibo se creó después de la revisión y no es parte del candidato.

RED: un prefijo de 4.100 zombis sintéticos ajenos devolvía grupo vivo
(1 fallo entre 3 tests, exit 1). GREEN focal más ejecución real del test de
dos corridas: 4 tests, exit 0. Regresión `ci/run_quality.sh`: exit 0;
CI 55, supervisor 133, QA 62 y requisitos 391 tests. El hardware objetivo
i3/WSL no se ensayó (NOT_RUN). La revisión fue estática y no verificó los
resultados de test de forma independiente.

El escaneo sigue siendo finito: más de 32.768 entradas o errores de lectura
mantienen la respuesta conservadora. No se altera la clasificación de
señales ni se atribuye OOM a SIGKILL.
