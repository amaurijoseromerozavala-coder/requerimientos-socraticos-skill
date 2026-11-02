# WU-CI-RUNTIME-010 — evidencia del runner y avisos de acciones

## Objetivo

El run `41397248336` confirmó la corrección del supervisor, pero la suite de Requerimientos recibió `RESOURCE_HEADROOM_UNKNOWN` en el runner Ubuntu 24.04. El mismo run emitió un aviso de deprecación de Node 20 para las acciones fijadas. Resolver la observación de cgroup sin relajar el cierre por incertidumbre y actualizar las acciones a versiones fijadas cuyo manifiesto declara Node 24.

## Oráculos y límites

- RED: conservar el fallo remoto del run `41397248336`; la suite local no sustituye el runner.
- Un cgroup v2 con raíz de montaje distinta de `/` debe mapearse a su directorio visible; rutas fuera de la raíz montada o montaje ausente mantienen `UNKNOWN`.
- El flujo debe exponer diagnóstico acotado si la admisión permanece incierta; nunca inventar memoria disponible.
- Acciones por SHA de release verificadas como `node24`; no usar etiquetas móviles.
- GREEN local y RDD del candidato exacto antes de push. Solo el siguiente run remoto puede establecer CI verde.

No hay prueba de carga ni calibración del i3/WSL.

## Evidencia

- RED remoto: run `41397248336`, suite Requerimientos con 35 fallos y 9 errores, varios con `RESOURCE_HEADROOM_UNKNOWN`; supervisor 65 y QA 62 pasaron. El runner no expuso su cgroup en ese log, por lo que el mapeo de raíz es una hipótesis falsable, no una causa confirmada.
- RED local antes de editar producción: el control de raíz montada produjo tres estados en vez de uno; el contrato del workflow rechazó las acciones Node 20 anteriores. La primera prueba del runner diagnóstico rechazó el mock anterior, que se actualizó para representar el nuevo paso de observación.
- GREEN local: `bash ci/run_quality.sh` con Python 3.12, `jsonschema`, `z3-solver` y PyYAML fijados, exit 0: 7 CI, 65 supervisor, 62 QA y 259 Requerimientos.
- RDD señaló el caso de un cgroup hijo bajo el marcador de montaje `/..`. RED nuevo: `UNKNOWN` observado frente a `OBSERVED_VISIBLE_SCOPE` esperado. Tras corregirlo, la suite local completa pasó: 7 CI, 65 supervisor, 62 QA y 260 Requerimientos.
- El siguiente run remoto sigue pendiente. Si `RESOURCE_HEADROOM_UNKNOWN` persiste, el diagnóstico acotado permitirá distinguir cgroup ausente de raíz no mapeada, sin convertir un UNKNOWN en PASS.
