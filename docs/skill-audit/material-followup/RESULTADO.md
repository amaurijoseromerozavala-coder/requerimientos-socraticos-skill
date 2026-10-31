# Contraste material y estructural — 2026-10-26

Estado: BLOCKED_GLOBAL_ENFORCEMENT. QA y producción siguen pausados.
Instrucción humana posterior y vigente: «no quiero CI todavia». No preparar,
publicar ni configurar CI hasta nueva petición. Solo se listó acceso GitHub en
lectura; no se modificó ningún repositorio remoto. Workspace sin remoto Git.

## Experimentos realmente ejecutados

Código instalado de la skill 2.1.1 conservado sin modificaciones. Pruebas nuevas
en copias temporales, no sobre QA. Evidencias en results.json y verify_claims.py.

1. CI=true y GITHUB_ACTIONS=true, PATH con consumidor falso exit0 y variable
   REQUIREMENTS_CONSUMER: advance devolvió exit1, BLOCKED/DOWNSTREAM_NOT_CONFIGURED.
   El falso consumidor no fue invocado. Bypass no observado para ese vector.
2. Orden instrumentado sobre tres directorios existentes: sus watches fueron
   instalados antes de la primera lectura regular de contenido (28 llamadas de
   lectura observadas). El código llama monitor.arm(root) antes de tree(...).
   Por tanto, la secuencia alegada «hash primero, activación después» no describe
   esta versión. No se equipara un test de tres directorios a garantía universal.
3. Programa C compilado con cc -std=c11 -Wall -Wextra -Werror -O2: fork real,
   64 escrituras pseudoaleatorias y restauración del byte original en un archivo
   de un subdirectorio; ejecución sincronizada al inicio de la primera lectura
   regular, con watches ya armados. El monitor rechazó el resultado con evento
   MODIFY/CLOSE_WRITE. No se afirma sincronización física de milisegundo exacto
   ni una prueba exhaustiva de todas las intercalaciones.
4. Veinte validadores cloud concurrentes terminaron exit0 con igual raíz. No se
   indujo presión de RAM/swap. Es diagnóstico de concurrencia local sin carga,
   **no aceptación del Test 1 ni prueba de estabilidad en el i3/WSL2**.

## Estado de las afirmaciones

- Test 1 físico: NOT_RUN_TARGET_UNAVAILABLE. No existe conexión operativa al PC
  del usuario en esta sesión; el entorno observado por MCP es cloud. No se
  ejecuta stress-ng en cloud para presentarlo como evidencia de ese hardware.
- Estado material: NO VERIFICADO, no fallo físico observado. Un requisito de
  aceptación puede quedar rechazado por evidencia insuficiente; eso no demuestra
  que flock falle ni que haya corrupción. Timeout, OOM y latencia >5000ms son
  fenómenos distintos: un timeout controlado puede ser fail-safe; latencia por
  sí sola no demuestra bytes corruptos. Se requeriría comparar datos y observar
  el resultado real de cada operación en el equipo objetivo.
- La preparación de watches y lo posterior al último check siguen fuera de la
  ventana declarada. Un archivo diferente un milisegundo después no contradice
  un snapshot del instante anterior. El futuro consumidor deberá usar los bytes
  verificados, sin volver a confiar en una ruta mutable del worktree.
- Un Merkle/Git tree puede reutilizar subárboles conocidos. Su formato por sí solo
  no permite saber qué ficheros arbitrariamente mutables cambiaron sin releerlos
  o disponer de una fuente de cambios confiable. No hay medición del i3 que
  demuestre que el recorrido acotado actual sea «computacionalmente hostil».
- No se afirma que runners GitHub sean inmutables o que un workflow por sí solo
  sea un oráculo confiable. Esa futura integración queda diferida por el usuario.

## Registro y trazabilidad

No hubo nueva entrevista skill→asistente en esta auditoría. Una pregunta
operativa real al humano consultó si el CI debía prepararse en el repositorio
accesible; respuesta literal: «no quiero CI todavia». Esa instrucción prevalece
sobre el mandato anterior de implementar CI. No se inventan mensajes de agentes.

Fuente auditada: scripts/requirements_guard.py, hash en results.json. Los tests
adicionales no modifican el candidato 2.1.1 previamente aprobado por RDD ni
constituyen nueva aprobación de producción. Se conserva el recibo anterior.
