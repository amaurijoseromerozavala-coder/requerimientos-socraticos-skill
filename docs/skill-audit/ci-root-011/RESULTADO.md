# WU-CI-ROOT-011 — candidato previo a RDD

El run `41477049313` observó dos ancestros cgroup `UNLIMITED_VISIBLE_SCOPE` y uno `UNKNOWN`; la política bloqueó correctamente la admisión. La documentación del kernel distingue la raíz real: está exenta de archivos de control de recursos. El cambio solo clasifica esa raíz como ilimitada cuando el montaje es `/`, `cgroup.controllers` contiene `memory` y se comprueba que faltan `memory.max`, `cgroup.type` y `cgroup.events`. La ausencia ambigua sigue siendo `UNKNOWN`.

Control RED y control negativo registrados en ODD. La suite local pasó: 7 CI, 65 supervisor, 62 QA y 262 Requerimientos. RDD y ejecución remota pendientes.
