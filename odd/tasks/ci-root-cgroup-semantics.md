# WU-CI-ROOT-011 — semántica de la raíz cgroup v2

El run remoto `41477049313` del commit `7807a30` informó dos ancestros de memoria sin límite visible y un tercer nivel `UNKNOWN`; los 65 tests del supervisor y los 62 de QA pasaron, pero Requerimientos se cerró con `RESOURCE_HEADROOM_UNKNOWN`. La documentación del kernel indica que la raíz real cgroup v2 está exenta del control de recursos y no debe tener archivos de interfaz de control. Esta unidad distingue esa raíz de un ancestro desconocido.

## Criterios

- Clasificar la raíz visible sin `memory.max` como ilimitada **solo** cuando mountinfo indique raíz `/`, `cgroup.controllers` informe `memory` y se confirme la ausencia de los archivos exclusivos de cgroups no raíz (`cgroup.type`, `cgroup.events`).
- Si falta una de esas pruebas o falla su lectura, conservar `UNKNOWN` y bloquear admisión.
- RED controlado para raíz real y control negativo para raíz no demostrada. GREEN local completo, RDD exacto y publicación; después verificar el runner remoto. Ningún ensayo de carga.

Referencia: documentación Linux cgroup v2, sección Conventions: «The root cgroup should be exempt from resource control and thus shouldn’t have resource control interface files.» https://docs.kernel.org/admin-guide/cgroup-v2.html

## Evidencia

- RED local: la raíz demostrada retornó `UNKNOWN` frente a `UNLIMITED_VISIBLE_SCOPE`; el control negativo de raíz no demostrada permaneció `UNKNOWN`.
- GREEN local: `bash ci/run_quality.sh` exit 0, 7 CI, 65 supervisor, 62 QA, 262 Requerimientos.
- El run remoto y el RDD de este candidato siguen pendientes; no se atribuye a esta corrección una calibración del hardware del usuario.
