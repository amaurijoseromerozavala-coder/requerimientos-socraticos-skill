# Contraste del QA posterior a 2.4.2

Fecha: 2026-10-28. Análisis de afirmaciones, sin cambios a la skill ni nueva
aprobación RDD. La autorización humana y CI diferido permanecen vigentes.

## ANALYSIS

| Afirmación del QA | Evidencia y clasificación | Decisión técnica |
| --- | --- | --- |
| Se eliminó matemáticamente todo TOCTOU | Se eliminó la materialización de documentos candidatos y se verifica el OID de los bytes consumidos. Cuenta, motor, schemas, dependencias y kernel siguen siendo confiables por hipótesis. | Aceptar la mejora concreta; rechazar la garantía universal. |
| Un PRD de30MiB pasa por ser menor de34MiB | validate_git.py lee cada blob con límite8MiB; git_bundle.py impone MAX_FILE8MiB y MemorySource conserva ese límite. | Refutado para el caso propuesto. No se ensayó un archivo real de30MiB. |
| El transporte entero es un string JSON de34MiB | El framing contiene cabecera JSON hasta2MiB y cuerpos binarios hasta32MiB. validate_prd.py decodifica documentos individuales, cada uno hasta8MiB. | Premisa incorrecta. El overhead de las estructuras resultantes sigue requiriendo medición. |
| El caso produce necesariamente thrashing o más de300MiB RSS | No hay observación de RSS, concurrencia, presión del host ni comportamiento del PC i3/WSL. Los factores5–10 y el fallo se presentan sin medición. | Hipótesis; no resultado de VERIFICATION. |
| No existe cuota explícita de memoria de la cadena | Los límites son de bytes/tiempo/transporte; no hay admisión ni cuota agregada de memoria del padre, objetos Git y consumidor. | Carencia real de gestión de recursos, pendiente de diseño y calibración. |
| RLIMIT_AS garantiza RSS controlado y MemoryError determinista | Linux lo define como límite de espacio de direcciones virtuales. Asignaciones pueden fallar con ENOMEM y la expansión de pila puede terminar el proceso. No garantiza un diagnóstico Python ni limita por sí solo todo el árbol de procesos. | Evaluar como mecanismo parcial de contención, nunca como solución universal. |
| La revisión nativa no ejecutó las pruebas, por tanto toda la evidencia es simulada | La revisión nativa fue de código/contratos/pruebas como fuentes. Por separado se ejecutaron168 pruebas locales y35 se reprodujeron en copia independiente. Sus evidencias y alcances están separados en RESULTADO.md. | Confirmar el alcance estático de RDD; rechazar la eliminación de la evidencia experimental independiente. |
| 0600 hace imposible cualquier integración futura | Es OWNER_ONLY. Lectura directa por otro UID sin autorización fallará según permisos; no se definió ese consumidor y CI sigue diferido. Transferencia o acceso mínimo pueden resolverse cuando exista ese requisito. | Sin cambio; no imponer0644 ni desobedecer la decisión humana. |
| PDEATHSIG no alcanza descendientes arbitrarios | Limitación real, ya declarada. Linux limpia ese ajuste en el hijo creado por fork. No hay una ejecución demostrada que convierta los documentos JSON en instrucciones para crear procesos. | Conservar límite de alcance; la ruta hipotética propuesta no es un fallo reproducido. |

La revisión estática aporta evidencia sobre código y contratos. No sustituye
ejecución, calibración física ni prueba formal. La experimentación acotada tampoco
demuestra ausencia universal de fallos. Bunge y Popper requieren clasificar las
premisas y observaciones; no convierten predicciones en resultados ni obligan a
incumplir normas o decisiones humanas.

## TEST PLAN

Comprobación pequeña ejecutada en este contraste: construir únicamente una
cabecera que declara un blob de30MiB, con un stream de167bytes, sin cuerpo.
read_bundle devolvió FILE_SIZE_LIMIT antes de leer contenido. Esto comprueba
rechazo de esa declaración en el receptor, no mide RSS ni reproduce presión
de memoria. La lectura Git también tiene un límite propio8MiB por objeto.

Antes de añadir límites de memoria conviene definir el presupuesto por validación
y por conjunto concurrente, incluyendo padre/consumidor, Python, schemas y Git.
Después perfilar muestras representativas pequeñas con límites exteriores y
parada; verificar clasificación del agotamiento, ausencia de aprobación parcial
y terminación/recogida de procesos propios. El equipo físico sigue sin acceso.

Un eventual RLIMIT_AS tendría que establecerse en el proceso adecuado antes de
las asignaciones controladas y considerar su memoria virtual de base. También
requiere compatibilidad de plataforma y tratamiento de fallos que no presuponga
que siempre habrá memoria para construir un JSON de error. Un límite solo en el
worker no presupone controlar la memoria ya usada por el padre.

Este plan es una propuesta técnica; no instala límites, no cambia permisos,
no configura servicios ni autoriza cargas de agotamiento. No se adopta ningún
valor numérico nuevo de memoria sin su justificación.

## VERIFICATION

- Observado en este contraste: rechazo de metadatos30MiB con FILE_SIZE_LIMIT,
  fixture167bytes y sin asignación de cuerpo.
- Releído: independent-review.json contiene35 ejecuciones, códigos0, sin skips,
  copia y hashes sin drift en el momento de aquella revisión.
- Evidencia histórica separada: full-tests.log168tests; RDD nativo aprobado y
  acknowledged para su identidad exacta. Ninguno certifica disponibilidad física.
- No ejecutado aquí: RSS de documentos grandes, presión de memoria, ensayo en
  i3/WSL, cambio de identidad de usuario ni creación hipotética de descendientes.
- Versión2.4.2 sin modificaciones; BLOCKED_GLOBAL_ENFORCEMENT conservado.

Conclusión: se incorpora como pendiente técnico el presupuesto de memoria y su
contención. No se acepta la certeza de los tres fallos proyectados ni la garantía
universal atribuida a la validación en memoria. Hay trabajo de ingeniería pendiente;
no se reduce todo a una limitación física inevitable.

## Fuentes primarias

- Código local: scripts/git_bundle.py, validate_git.py, validate_prd.py,
  document_source.py y process_supervision.py dentro de la skill.
- Evidencia local: RESULTADO.md, full-tests.log, independent-review.json,
  rdd-final.json e integrity-final.json de este directorio.
- Linux límites: https://man7.org/linux/man-pages/man2/getrlimit.2.html
- Linux señal del padre: https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html

No hubo nuevas preguntas al humano ni respuestas semánticas inventadas. Este
contraste no reabre ni da por completada una entrevista de requisitos.
