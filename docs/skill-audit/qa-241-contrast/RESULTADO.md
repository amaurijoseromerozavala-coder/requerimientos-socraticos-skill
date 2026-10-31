# Contraste del informe QA sobre requerimientos-socraticos 2.4.1

Fecha: 2026-10-27. Alcance: contraste de afirmaciones, revisión estática independiente
y regresión local acotada. Sin cambios al código, permisos ni versión de la skill.
Gentle AI real 4.2.0 observado; modo RDD global ON. Esto no constituye una nueva
aprobación RDD ni amplía la aprobación histórica del candidato 2.4.1.

## ANALYSIS

El output QA es evidencia de afirmaciones propuestas por un revisor, no una orden
humana ni una reproducción experimental. Se separan hechos, inferencias y pendientes.

| Afirmación QA | Contraste | Disposición |
| --- | --- | --- |
| Git carece del control de muerte del padre aplicado al analizador lógico | Confirmado por lectura: `validate_git.py:120` invoca al consumidor sin ese control ni grupo propio. | Mejora técnica justificada: unificar supervisión. Pendiente de implementación y ensayos específicos. |
| Git carece de timeout y cuatro ejecuciones quedan permanentemente retenidas | El mismo renglón sí pasa `timeout=remaining`; `Objects.run` también limita plazo/salida y termina su proceso al fallar. No se aportó un caso actual de consumidor indefinido. | Rechazar la certeza del resultado; conservar hipótesis condicionada a pérdida del padre y consumidor que no termina. |
| Una copia temporal puede diferir de los objetos verificados | Se verifican objetos antes de escribir; el manifiesto usa esos bytes. No se cotejan criptográficamente todos los bytes efectivamente consumidos después. | Limitación real de correspondencia bajo modificación concurrente; no presentar metadatos como prueba de identidad. |
| Modificar la copia refuta la identidad del commit Git | Cambia la copia, no el objeto original ni su OID. La correspondencia entre entrada consumida y candidato es otra obligación. | Corregir la conclusión. |
| `utimensat` restaura arbitrariamente mtime y ctime | El contrato Linux permite atime/mtime; ctime se actualiza al tiempo actual. | Premisa incorrecta. Esto tampoco convierte la heurística en prueba de lectura atómica. |
| stdin es la única solución demostrable y elimina todo problema de aislamiento | Puede evitar materialización de los documentos, pero requiere verificar y consumir exactamente los mismos bytes, incluir todas las dependencias y limitar recursos. No aísla por sí solo cuenta, motor o kernel. | Propuesta útil, garantía universal rechazada. |
| 0600 vuelve inútil todo pipeline CI | 0600 es el contrato actual OWNER_ONLY. Otro principal sin acceso no podrá leer directamente, pero no se ha definido ese consumidor y CI está expresamente diferido. | No es un defecto actual demostrado ni una autorización de integración. |
| 0644 es necesario para integrar | Añade lectura para todos; no es condición necesaria para grupo autorizado, ACL o transferencia controlada. | No ampliar permisos por defecto. Diseñar acceso cuando exista requisito autorizado. |

La cuenta, el kernel y el motor instalados integran la frontera confiable declarada
en `sealed-validation.md` y en el resultado de `validate_git.py`. La versión actual
no satisface un requisito de independencia frente a otros procesos arbitrarios de
la misma cuenta. Esa capacidad sigue no soportada: no se redefine como verificada
por confianza documental, por memoria o por permisos locales.

La retención del lease evita reutilizar datos todavía consumidos. Si el consumidor
termina, el descriptor se cierra y el slot puede reutilizarse; no exige reiniciar
el sistema. Si pierde al padre y no termina, su duración deja de estar limitada
por el timeout ejecutado en el padre. Son escenarios distintos.

### Correcciones que pasan el filtro técnico

1. Extraer una primitiva compartida de supervisión y aplicarla a la cadena Git y
   al consumidor documental, conservando el plazo restante, los leases y el contrato
   de error. Definir manejo de interrupciones, muerte del padre, grupos propios y
   estado de limpieza incompleta. Linux no equivale a todas las plataformas ni a
   tiempo real; el control del hijo directo no cubre descendientes arbitrarios.
2. Mejorar la unión entre bytes consumidos y manifiesto Git. Un proveedor acotado
   de blobs verificados en memoria es una alternativa razonable: cada documento y
   dependencia debe verificarse antes de interpretar esos mismos bytes, sin releer
   rutas mutables. No basta cambiar el archivo principal a stdin. Deben medirse
   las copias de memoria, la serialización y la salida; 32 MiB de blobs no equivale
   a 32 MiB de RSS. Esta propuesta no constituye implementación aprobada ni prueba
   de aislamiento ante procesos de la misma cuenta.
3. Mantener 0600 y CI diferido. Si aparece un consumidor externo autorizado,
   acordar principal, canal y acceso mínimo; no imponer 0644 como solución universal.

## TEST PLAN

Ejecutado: suite existente `test_sealed.py`, con datos temporales y límites de sus
harnesses. Incluye identidad del commit frente a cambios del worktree/HEAD,
rechazo de objetos y rutas no admitidos, normalización 0600, publicación sin
sobrescritura y recuperación después de terminar un proceso propio durante extracción.
No se alteraron los tests ni sus oráculos.

Pendiente para la futura corrección: terminar de forma controlada el padre durante
un consumidor de prueba que espera; confirmar terminación y recogida del hijo,
liberación y posterior reutilización del lease. Usar un fixture pequeño, acotado y
con limpieza propia; no construir cargas de agotamiento. Cubrir también timeout
con padre vivo, éxito normal, errores y plataformas sin adaptador.

Para un eventual backend en memoria: comprobar identidad de cada dependencia,
rechazo de bytes distintos/incompletos, límites de bytes/profundidad, semántica
equivalente a los validadores actuales y ausencia de lecturas de documentos desde
rutas temporales. Ninguna ejecución en el PC físico se da por realizada.

## VERIFICATION

- Observado: 23 tests existentes OK, comando:
  `/home/agent/.local/share/requerimientos-socraticos/venv/bin/python -B -m unittest discover -s skills/requerimientos-socraticos/tests -p test_sealed.py -v`.
- Observado: fuente instalada de CPython `subprocess.run` termina y espera al hijo
  al vencer el timeout; coincide con su documentación. Necesita que el padre pueda
  ejecutar ese manejo; no promete un deadline estricto del sistema operativo.
- Revisión independiente: agente `qa241_claim_triage`, solo lectura, corroboró las
  tres disposiciones. No ejecutó ensayos ni aprobó una nueva versión.
- No reproducido: terminación del padre durante `validate_prd.py`, retención
  permanente de cuatro slots, cambio concurrente de la copia durante consumo.
- No ejecutado: estrés de recursos, hardware i3/WSL, CI o producción.
- Versión permanece 2.4.1; `BLOCKED_GLOBAL_ENFORCEMENT` se conserva.

Los 23 casos no demuestran ausencia de fallos globales. La aprobación RDD previa
es evidencia de su candidato y alcance; no resuelve automáticamente estos pendientes.

## Registro de preguntas y respuestas

No se formuló una nueva pregunta al humano ni se inventó una respuesta suya.
La pregunta técnica al revisor independiente fue clasificar supervisión Git,
correspondencia de bytes y permisos CI contra el código actual. Su respuesta fue:
limitación real de supervisión con impacto no demostrado; garantía de identidad
acotada a la frontera confiable; 0600 es el contrato actual y CI una necesidad
futura si el humano la autoriza. Este registro no es una entrevista de requisitos
ni cierra preguntas semánticas anteriores.

## Fuentes

- Código local: `scripts/validate_git.py:18`, `:57`, `:87`, `:120`, `:123`;
  `scripts/safe_io.py:6`; `scripts/scratch_pool.py:1`;
  `scripts/normalize_text.py:22`, `:41`, dentro de la skill.
- Contrato local: `references/sealed-validation.md`, `AGENTS.md`.
- Python 3.12: https://docs.python.org/3.12/library/subprocess.html#subprocess.run
- Linux utimensat: https://man7.org/linux/man-pages/man2/utimensat.2.html
- Linux permisos: https://man7.org/linux/man-pages/man2/fchmod.2.html

Los hashes de fuentes de esta lectura constan en `evidence.json`. No son una
firma, un recibo RDD ni una garantía de inmutabilidad continua.
