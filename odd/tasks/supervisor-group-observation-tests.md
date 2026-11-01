# WU-SUP-GROUP-003 — controles negativos de observación del grupo

## Solicitud y alcance

El propietario pide corregir la observación R3-001 del RDD de WU-SUP-GROUP-002 y volver a aplicar RDD. El hallazgo señala dos ramas sin prueba específica: error de lectura al observar `/proc` y grupo con solo zombis. Esta unidad añade pruebas acotadas a esas ramas; no cambia la implementación de producción salvo que un ensayo revele un defecto.

## Oráculos

1. Si la lectura de `/proc` falla tras recolectar al hijo, `cleanup=UNCONFIRMED`, `status=INFRA_LOCK` y una segunda ejecución de la instancia queda bloqueada. Un descendiente vivo controlado mantiene el grupo durante el ensayo; la prueba lo detiene en `finally`.
2. Si la observación de `/proc` muestra solo un miembro zombi del grupo, una ejecución real del hijo sin otros miembros activos conserva `EXITED`, `cleanup=CONFIRMED` y `returncode=0`. El dato zombi se simula de forma explícita; no se proclama reproducción de un zombi del kernel.
3. Una mutación temporal de cada rama debe hacer fallar su prueba respectiva (RED de control negativo). El código fuente original debe restaurarse antes de GREEN y la regresión.

## Tareas

1. Añadir las dos pruebas y ejecutar los mutantes controlados para RED, conservando salida y restaurando código fuente.
2. Ejecutar GREEN sobre código real y la suite completa del supervisor.
3. Congelar candidato, RDD nativo Gentle AI, reconocer, publicar y verificar SHA remoto.

## Registro

- 2026-11-01: unidad abierta antes de editar las pruebas.
- 2026-11-01: las dos pruebas pasaron sobre el código vigente. Mutación temporal de ambas ramas: RED, 2 fallos esperados; archivo de producción restaurado sin diferencias. GREEN focal: 2 OK. Regresión del supervisor: 51 OK. Sin calibración en el i3/WSL.
