# WU-CI-RUNTIME-010 — candidato previo a RDD

El segundo run remoto (`41397248336`) confirmó que los 65 tests del supervisor pasaron. La suite de Requerimientos se cerró con `RESOURCE_HEADROOM_UNKNOWN` en múltiples casos; el log carecía del estado del cgroup visible. Esta unidad añade un mapeo comprobado para la raíz de montaje cgroup v2 en un espacio de nombres, registra solo estados acotados del runner y fija checkout/setup-python a releases cuyo `action.yml` declara `node24`.

El RDD detectó que un cgroup hijo bajo el marcador de montaje `/..` también debe resolverse respecto de la raíz visible. La prueba negativa falló antes de corregir esa ruta y luego pasó. La ejecución local completa terminó con exit 0: 7 tests de CI, 65 de supervisor, 62 de QA y 260 de Requerimientos. El run remoto y cierre RDD de este candidato siguen pendientes. La fuente de `RESOURCE_HEADROOM_UNKNOWN` en GitHub aún no se ha demostrado; el sistema conserva el rechazo si no puede observar los límites.
