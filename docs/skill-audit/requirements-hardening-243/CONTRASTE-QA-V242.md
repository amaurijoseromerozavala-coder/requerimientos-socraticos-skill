# Contraste de QA que cita 2.4.2 frente al estado 2.4.3

Fecha: 2026-10-28. Revisión de afirmaciones; no cambios de código ni nueva versión.
Se conservan las instrucciones humanas y los recibos del candidato aprobado.

## ANALYSIS

El informe identifica la versión2.4.2. La entrega actual es2.4.3, identidad nativa
sha256:d42b9b6eb80a5ef2041bbaac3cfbeab4866699af74361a59cce568a85e1f6717.
Comparar versiones diferentes puede servir para historia, pero no demuestra el
estado del código actual. Tampoco se acepta la garantía universal de eliminación
de TOCTOU: se verifican bytes y se evita materializar documentos candidatos bajo
la frontera confiable declarada de cuenta, motor, schemas y kernel.

| Afirmación | Código y evidencia | Clasificación |
| --- | --- | --- |
| El preflight del analizador recorre34MiB | logic_engine.MAX_BYTES=262144; read_regular rechaza exceso antes de preflight. preflight_json también comprueba longitud antes del bucle. | Premisa falsa para esta vía. |
| El preflight Git recorre todos los blobs | read_bundle llama al preflight solo sobre cabecera JSON, máximo2MiB. Los cuerpos son bytes separados y cada archivo máximo8MiB. | Confunde transporte con documento/cabecera. |
| Un archivo30MiB llega al parser lógico y agota5s | Excede256KiB. Un fixture de256KiB+1 fue rechazado con INVALID_INPUT/FILE_SIZE_LIMIT, exit2, no WALL_CLOCK_LIMIT. | Escenario propuesto no alcanza la etapa que pretende evaluar. |
| Un documento30/32MiB pasa por Git y supera1GiB de RSS | Excede8MiB por archivo. Además2.4.3 ya aplica límites virtuales de roles antes de exec. | No demuestra ese resultado en la versión actual. |
| Cada1/2 del array ocupa un entero nuevo de28bytes | En esta ejecución CPython, json.loads('[1,2,1,2]') produjo dos identidades de enteros, no cuatro. getsizeof tampoco mide por sí solo RSS de todo el proceso. | La cuenta de expansión y1.5GiB no está demostrada; overhead general sí es un riesgo real. |
| No se está usando RLIMIT_AS | Ya se usa en CLI/coordinador/consumidor/Git2.4.3 con alcance y excepciones documentados. | Desactualizado para la vía Git. |
| Falta un presupuesto de memoria en analizador/Z3 | analyze_logic usa supervisor con plazo/salida acotados, pero no solicita address_space_limit para su worker.2.4.3 declara que su perfil es de validación Git. | Pendiente técnico válido para un próximo alcance, no una corrección ya implementada. |
| Un regex o código C garantiza el comportamiento requerido | El lenguaje/backend no demuestra tiempos, equivalencia del tratamiento de strings/escapes ni complejidad de cualquier patrón. | Optimización requiere perfilado y pruebas de equivalencia; no adoptar automáticamente. |
| 0600 hace imposible integrar y el QA puede ignorar política humana | OWNER_ONLY restringe lectura directa por otros principales. No impide diseñar una transferencia o acceso mínimo futuro. CI está explícitamente diferido y el QA no redefine esa decisión. | No hay autorización ni defecto actual demostrado para ampliar a0644. |

El coste O(N) es real; el tiempo5–15s en el i3 no fue medido y usa un N no
admitido por esas rutas. Tampoco se demuestra su negación para todo estado del
hardware. El preflight debe evaluarse con sus tamaños y presupuestos efectivos,
no con todos los bytes del transporte sumados como si fueran un único JSON.

json.loads construye objetos Python; no es por sí mismo el AST lógico formal del
modelo. El tamaño de esos objetos depende de tipos, valores, estructura y runtime.
Que los enteros pequeños se compartan aquí no elimina el overhead de listas,
diccionarios, strings y otras entradas ni prueba viabilidad del equipo objetivo.

RLIMIT_AS limita espacio virtual, no una reserva de RAM ni RSS. No garantiza un
MemoryError capturable para toda terminación. Esta distinción sigue vigente al
evaluar una posible extensión a Z3; el perfil no debe elegirse suponiendo que su
runtime nativo tiene la misma memoria inicial que el consumidor documental.

## TEST PLAN

Se realizaron dos comprobaciones pequeñas sin construir archivos de30MiB:

1. Subclase de bytes de9bytes con iteración prohibida y max_bytes8: rechazo por
   longitud antes de intentar iterar. Este fixture instrumentado prueba el orden
   de controles; no es un perfil de rendimiento.
2. Archivo temporal de262145bytes pasado a analyze_logic.py --timeout5, con
   timeout exterior8s: exit2, INVALID_INPUT, FILE_SIZE_LIMIT. Duración observada
   aproximada0.119s en cloud; una sola muestra, no benchmark ni extrapolación i3.

También se inspeccionó un array de cuatro elementos para comprobar la premisa
sobre identidad de enteros en el runtime actual. No se ejecutó una expansión
grande ni se midió un máximo de RSS con esa observación.

Para una futura mejora: perfil pequeño de importación/uso de Z3, límites virtuales
en el worker y diagnóstico bloqueado ante rechazo, conservando compatibilidad,
plazos e identidad de inputs. Optimizar el preflight solo si una medición en su
envolvente válida identifica un coste material, sin sacrificar strings/escapes.
Son propuestas, no mandatos de QA ni cambios implementados en este contraste.

## VERIFICATION

Resultados nuevos y límites exactos: qa-latest-evidence.json. Se comprobó además
que los92 archivos del conjunto aprobado mantienen sus SHA256. La versión sigue
siendo2.4.3; no se reejecutó sin motivo la suite195 ni se emitió otro recibo RDD.
No se probaron presión de RAM/swap, UID distinto, i3/WSL ni payloads enormes.

La evidencia anterior conserva alcance:195 pruebas locales,62 reproducción
independiente y revisión nativa estática del candidato exacto. Ninguna equivale
a disponibilidad física global. Mantener BLOCKED_GLOBAL_ENFORCEMENT no valida
automáticamente los razonamientos o resultados proyectados de este nuevo QA.

Fuentes locales: scripts/logic_engine.py, json_preflight.py, git_bundle.py,
validate_git.py, git_validation_engine.py, process_supervision.py y
references/memory-budget.md; recibos y evidencia de esta carpeta.

No hubo preguntas nuevas de requisitos al humano ni respuestas inventadas.
El siguiente revisor debe recibir el JSON completo2.4.3 y distinguir versión,
ruta alcanzable, límite efectivo, observación ejecutada e hipótesis pendiente.
