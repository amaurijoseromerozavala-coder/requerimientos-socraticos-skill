# WU-RS3-D05-SPLIT-ACCOUNT-PLAN-041

## Autoridad, objetivo y alcance

El maintainer autorizó avanzar con la topología recomendada de dos cuentas
dedicadas en Linux/WSL. La evidencia aportada por Gentle Pi para el commit
`eddff42` informó exposición del socket Docker, WSLInterop y un montaje
Windows escribible desde la cuenta actual. Esa transcripción es
`USER_REPORTED`; no demuestra control de una cuenta guardián inexistente.

Esta unidad prepara el procedimiento material y endurece el sondeo pasivo
del agente para detectar **cualquier** montaje Windows escribible visible en
`mountinfo`, no solo `/mnt/c`. Corrige la dependencia de dos pruebas respecto
a las capacidades efectivas del runner. No crea cuentas, modifica permisos,
ejecuta sudo/Docker/Windows, provisiona secretos ni habilita D03/D05.

## Oráculos RED congelados

1. Si `/mnt/c` no es el montaje observado pero otro volumen Windows identificado
   mediante `drvfs` o `9p` con `aname=drvfs` es escribible, el sondeo informa
   `EXPOSED`, incluso cuando WSLInterop está deshabilitado.
2. Un montaje Linux ordinario bajo `/mnt` o una línea de mountinfo que solo
   contiene el texto `drvfs` en un campo no determinante no se clasifica como
   Windows. Si el inventario de montajes no se puede leer por completo, no se
   afirma ausencia de exposición.
3. Las pruebas de señales ausentes fijan UID/capacidades sintéticas; el resultado
   no varía con los privilegios del runner. Una capacidad efectiva no nula se
   informa por separado como exposición.
4. El plan de dos cuentas conserva un operador externo, código confiable no
   escribible por el agente, almacén privado del guardián, controles negativos
   de elevación y host Windows, y puertas de parada antes de cualquier código
   real o recibo. Ni cuentas separadas ni `sudo -n -l` exit 1 prueban D05.

## Verificación y límites

ODD → pruebas RED → implementación y guía mínima → GREEN/regresión → revisor
independiente → RDD exacto → respaldo Git. Las pruebas materiales en el equipo
objetivo quedan `NOT_RUN` hasta recibir nueva evidencia. El sondeo sigue
`authority_verification=NOT_ESTABLISHED`, `execution_authorized=false`.

## Resultados observados

- RED inicial: la suite focal produjo `ImportError` porque faltaba
  `_other_windows_mount_write`.
- GREEN focal: `Ran 16 tests`, `OK`. Incluye un montaje Windows alterno,
  falsos positivos `ext4/9p` y un inventario mayor de 1 MiB que vuelve a
  `NOT_ASSESSED`.
- Regresión local `ci/run_quality.sh` exit 0: CI 55, supervisor 173, QA 62,
  requisitos 429, todos `OK`, con Python 3.12 y `z3-solver==4.15.4.0`. El
  runner usa su límite virtual interno de 1 GiB.
- El revisor independiente confirmó los oráculos focales y pidió acotar la
  descripción del sondeo a la raíz de los montajes reconocidos, además de
  distinguir una vía sudo utilizable de la mera presencia del binario. Ambas
  precisiones quedaron en la guía antes del RDD nativo.
- Ensayos de cuentas, `sudo`, Windows host y canal humano en el i3/WSL:
  `NOT_RUN`. El estado D05 permanece `NOT_ESTABLISHED`.
