# WU-PORTABLE-001 — Requerimientos Socráticos 2.4.7

Estado: IMPLEMENTED_TESTS_PASS_RDD_PENDING. Equipo i3 del usuario: NOT_OBSERVED.

Nueva entrada autocontenida scripts/requirements: funciona por ruta sin requerir
subcomando upstream. Wrapper opcional resuelve rutas relativas al ejecutable y
permite upstream explícito, sin alterar perfiles de autenticación. Todas las
operaciones usan la selección común de Python; ausencia de runtime/helper falla
con diagnóstico. Ayuda sin intérprete e instalación de dependencias nunca automática.

SKILL.md y guía Gentle Pi/Shell explican activación real, alcance de requisitos,
correcciones por agente de desarrollo autorizado y límites de Shell/preflight.
No se afirma que instalar una skill instale el supervisor o imponga cuotas a Shell.

RED: 13 fallos/subcasos de la suite inicial (entrada ausente/rutas cloud/delegación).
GREEN: 8 tests de portabilidad (incluidas regresiones adicionales de venv y comando
desconocido), 9 tests de entorno existentes, bash -n correcto. Preflight real
cloud devuelve READY_FOR_LIVE_ADMISSION, sin autorización de trabajo ni prueba i3.
Copia con espacios, enlace simbólico, todas las rutas dispatch probadas, runtime
explícito inválido/vacío y upstream que apunta al wrapper rechazados.

La unidad retained-pipe sigue pendiente de su propio consentimiento RDD; no forma
parte de este candidato. No se publica este cambio antes de su cierre RDD.
