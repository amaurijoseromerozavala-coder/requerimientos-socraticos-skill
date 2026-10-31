# Falsación y endurecimiento de las garantías documentales

## Specs

Petición humana: comprobar ceguera de inventario, mutación y reversión, evasión de READY, concurrencia; árbol completo, inotify, gate bloqueante y locks. QA Inquisidor permanece pausado. No se autoriza afirmar determinismo absoluto ni ejecutar una saturación destructiva del host cloud como si fuera WSL objetivo.

## Tasks

- [x] Auditar fuentes, skill y artefactos históricos; RED en copia aislada.
- [x] Implementar comprobación del árbol completo y observación fail-closed en ventana explícita.
- [x] Probar bloqueo con timeout, mutaciones, evasión y controles negativos.
- [x] Documentar frontera del orquestador, conservar recibos, RDD nativo y resultados.

## Log

- Dos hashes de extremos no prueban historia continua. Inotify no reconstruye pasado ni garantiza un monitor sin pérdida. flock es advisory; hook local omisible. Fuentes primarias man7 inotify/flock y git githooks consultadas por MCP web.
- Web primer intento usó argumento search_query no admitido y devolvió isError; segundo intento open con esquema correcto devolvió las tres fuentes. No se cita el fallo como investigación válida.
- Pruebas agresivas sobre copia temporal, nunca sobre directorio QA real. RED conserva reconstrucción explícita del algoritmo enumerado; no se atribuye ejecución de comparador histórico no retenido.

- Nuevos controles: hash canónico de árbol completo, inotify acotado fail-closed,
  snapshot privado y flock exclusivo cooperativo por raíz; 20 tests PASS y 43
  regresiones PASS. Nuevo launcher local requirements; advance siempre bloquea
  por ausencia de consumidor/autoridad confiable (no integración global ficticia).
- RDD: primera selección omitió tres evidencias retenidas en el baseline y las
  mostraba como eliminadas del snapshot (no del disco). Antes de ejecutar ningún
  revisor se invalidó nativamente el candidato pristine review-73e74d37c54be335,
  reason literal registrado en autoridad. Dos intentos recover fueron rechazados
  por restricciones de overlay/base-diff, sin mutación. Se declaró otro candidato
  con inventario completo review-5d232f3e231361be, no repetición de revisión adversa
  ni eliminación de findings; cuatro lentes nativos en curso.

- R3-monitor-gap reproducido con RED genuino (mutación/restauración en subárbol
  tardío durante primera lectura regular). Corrección de 76 líneas, dentro del
  plan 180/budget200; fase arm de todo el árbol antes de lectura; 21 tests PASS;
  validación dirigida nativa aprobada y acknowledged. Recibo rdd-final.json.
- Advisories R2-001/R3-baseline-shape/R4-001 corregidos como trabajo posterior,
  sin reabrir recibo aprobado. RED retenido; 23 tests guard PASS + 43 existentes
  PASS; versión2.1.1. Nuevo overlay64 líneas, lineage review-69b5e127cef65086:
  cuatro lentes findings vacíos, aprobado y acknowledged; fuente congelada sin
  discrepancias. Recibo rdd-followup-final.json.
- Inventario completo QA19 coincide con baseline, sin cambios actuales; ventana
  inotify final limitada y verificada. Historia anterior NOT_PROVEN. No remoto
  Git configurado, sin CI protegido/consumidor: BLOCKED_GLOBAL_ENFORCEMENT.
- Registro de preguntas/respuestas histórico preservado, sin nueva sesión de
  interrogador durante auditoría. No reconstruir mensajes ni equiparar COMPLETE
  acotado con cierre global. Documentación y logs en docs/skill-audit/integrity-challenge.
