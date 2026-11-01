# WU-SUP-GROUP-001 — cierre acotado del grupo de procesos

## Specs

Solicitud: continuar la integración del supervisor a partir del informe de QA. El núcleo ya crea una sesión nueva para el hijo, pero sus señales de terminación se dirigen solo al hijo directo. Esta unidad verifica y corrige el caso en que un miembro del mismo grupo continúa después del plazo.

Mientras el hijo directo siga vivo y su PGID sea verificable, el supervisor solicita SIGTERM y, si vence la gracia, SIGKILL al grupo creado para ese hijo. Conserva `returncode` como observación del hijo directo; no interpreta la causa de señales externas. La confirmación de `wait()` acredita solo la recolección del hijo directo. No declara contención universal de descendientes: un proceso puede salir del grupo o sobrevivir después de que el padre haya sido recolectado. No implementa recuperación autónoma, journal ni incorporación QA. No usa carga intensiva ni el hardware objetivo.

## Acceptance

- Un hijo vivo y un descendiente que comparten el grupo y omiten SIGTERM terminan tras el plazo acotado; el supervisor no presenta éxito del checker.
- La prueba limpia sus procesos incluso si la implementación inicial falla.
- Señales a un grupo inexistente o distinto no se interpretan como prueba de limpieza completa.
- Las regresiones del núcleo y adaptador siguen pasando.

## Tasks

1. RED: introducir una prueba de un descendiente en el mismo grupo y conservar el fallo observado.
2. GREEN: corregir la solicitud de terminación al grupo con identidad acotada y fallos cerrados.
3. Ejecutar regresión, revisar alcance real y someter el candidato exacto al RDD de Gentle AI.
4. Solo tras RDD aprobado y reconocido, publicar en GitHub y verificar SHA.

## Log

- 2026-11-01: alcance delimitado. La recuperación y la unión del journal quedan para unidades posteriores.
- 2026-11-01: RED: el descendiente continuó tras el plazo (test aislado, `exit=1`). GREEN: `exit=0`; regresión: 47 pruebas, `exit=0`.
