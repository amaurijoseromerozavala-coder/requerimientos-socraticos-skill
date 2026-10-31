# ANALYSIS — Contraste de la crítica y registro documental

Fecha: 2026-10-26. QA Inquisidor continúa pausado.

## Hallazgos demostrados y límites

1. **Ceguera del inventario enumerado confirmada en copia aislada.** La
   reconstrucción explícita del algoritmo `all(hash(file)==baseline[file])`
   aceptó un archivo extra. No se atribuye ejecución a un comparador histórico
   cuya versión ejecutable no se conservó. Su lógica es suficiente para el
   contraejemplo; red-baseline.json conserva la observación.
2. **Historia continua no demostrada.** Modificar/restaurar pasó el comparador
   de extremos. Se retira cualquier lectura de «19 archivos intactos» como
   ausencia histórica de mutaciones. Actualmente inventario y contenido coinciden
   con la base, sin añadidos ni eliminados; el pasado sigue NOT_PROVEN.
3. **Validator opcional y autoridad falsa son riesgos reales.** El test conserva
   un READY sintético que supera el comprobador documental. Esto demuestra la
   frontera: schema, hashes y recibos declarados no autentican una aprobación
   nativa. No hay consumidor downstream implementado que podamos probar que lo
   acepte o rechace. La nueva entrada `advance` bloquea siempre por esa ausencia;
   no se anuncia una integración global terminada.
4. **La imputación sobre el fixture no queda demostrada.** El registro antiguo
   muestra STALE_CANDIDATE antes de llegar al oráculo INTERROGATION_INCOMPLETE.
   Recalcular el hash de datos sintéticos modificados permite alcanzar ese
   oráculo, pero no prueba verdad de la especificación. Sigue existiendo un test
   separado que modifica datos sin rehash y exige STALE_CANDIDATE. No se cambió
   el criterio de rechazo de entrevista pausada. Historial original conservado.
5. **Predicción de colapso bajo swap no comprobada.** El PC objetivo no está
   disponible. No se observó su filesystem, latencia, DRAM del SSD ni presión
   de memoria. Ni JSON pequeño ni latencia alta implican por sí solos corrupción
   o fallo. Cinco procesos de lectura no son cinco escritores concurrentes.

## TEST PLAN — Falsación ejecutada

- Copia temporal: inyección y modificación/restauración contra lógica anterior;
  ambas pasaron indebidamente. Nunca se inyectó nada en QA real.
- Árbol completo: adición, eliminación, renombrado, cambio de contenido/modo y
  directorio vacío invalidan la base; symlink y FIFO se rechazan.
- Inotify real: modificar/restaurar, nuevo directorio y renombrar raíz se detectan.
  Overflow es registro kernel sintético inyectado en test, no estrés real.
- Lock real: contención termina en LOCK_TIMEOUT; cinco invocaciones concurrentes
  validan el mismo PRD sintético sobre snapshots, serializadas por raíz.
- READY sintético: `validate` puede verificar estructura/recibos declarados;
  `advance` lo rechaza con DOWNSTREAM_NOT_CONFIGURED. No firma ni certifica READY.
- JSON corrupto, baseline corrupto y límite de bytes bloquean.
- Test inicial de permisos no cambió nada: el umask ya creó 0600 y el fixture
  aplicaba 0600. Fallo retenido en fixture-permission-debug.stderr. Se cambió la
  acción a alternar un bit de ejecución, manteniendo el mismo oráculo de rechazo.
  Esto es reparación del estímulo sintético, no contraejemplo del detector.

## VERIFICATION — Resultados observados

- 23 tests nuevos PASS; 43 existentes PASS. Logs adjuntos.
- QA: inventario completo actual de 19 archivos idéntico a la base enumerada;
  ninguna adición/eliminación/modificación actual. Historia continua NOT_PROVEN.
- Nuevo hash raíz compromete inventario completo; no es un formato Merkle/Git.
- Ventana inotify solo durante cada invocación; no repara auditoría histórica.
- 32 MiB/4096 entradas/64 niveles; timeout de lock y subproceso, sin deadline duro de kernel.
- Stress WSL/RAM/swap: NOT_RUN. No atribuir resultados cloud al hardware objetivo.
- RDD actual: consultar recibo externo posterior; el presente informe se congela
  antes de review y no se reescribe para autodeclarar aprobación.

## Mejoras de diseño y estado pendiente

La skill pasa a 2.1.1 con guía explícita de fronteras y controles acotados. El
launcher local (no binario upstream) expone `gentle-ai requirements`.
No se instala hook «ineludible»: Git permite omitir pre-commit. No se implementa
un daemon como prueba absoluta: inotify puede perder eventos y no registra todo
acceso remoto ni reconstruye pasado. flock solo coordina participantes.

**BLOCKED_GLOBAL_ENFORCEMENT** hasta configurar un consumidor confiable separado
del autor, uso del snapshot exacto y autenticación del recibo RDD nativo. La
solución de diseño preferida es gate del consumidor/CI protegido, comparada con
hook local (omitable) y firma en la misma cuenta (clave controlable por autor).
No hay ese consumidor ni remoto protegido configurado; no fabricar éxito.

## Registro de preguntas y respuestas

No se abrió una nueva sesión de interrogador durante esta auditoría técnica.
No se reconstruyen diálogos ni se atribuyen preguntas a una skill inexistente.
El registro real anterior (dos preguntas del smoke acotado) permanece en
`../requerimientos-repair/smoke/registro-skill-asistente.md`. Sus respuestas son
históricas: el presente documento restringe sus conclusiones de integridad y
READY; COMPLETE no significa completitud global.

## Fuentes consultadas por MCP web

- inotify y limitaciones: https://man7.org/linux/man-pages/man7/inotify.7.html
- flock advisory: https://man7.org/linux/man-pages/man2/flock.2.html
- bypass pre-commit: https://git-scm.com/docs/githooks

Skill-first: SKILL.md local y referencias workflow/validation leídas; runtime
cloud y networking consultados. MCP-first: discovery de herramientas, estado
cloud actual y web por MCP. CodeGraph omitido según AGENTS.md: no hay índice.

## Corrección exigida por RDD

El revisor nativo encontró R3-monitor-gap CRITICAL: el primer recorrido armaba
watches de subdirectorios al alcanzarlos, dejando una ventana mientras se leía
un fichero anterior. Un nuevo test mutó/restauró z-later/file.json al empezar
la primera lectura regular; RED real: GuardError no se produjo (21 tests, 1 fallo).
Se congeló plan nativo de 180 líneas antes de editar. Corrección en dos fases:
armar todos los directorios existentes, comprobar eventos y fijar comienzo de
ventana; después recorrer/leer contenidos. La preparación no se presenta como
historia cubierta. Mismo estímulo/oráculo ahora GREEN, 21 tests. Evidencia RED
retenida en guard-gap-red.stderr; sin borrar hallazgo ni reiniciar su lineage.

## Seguimiento independiente de advisories

RDD aprobó y acknowledged la corrección crítica. Sus avisos posteriores R4-001/
R3-baseline-shape y R2-001 se trabajan como candidato distinto: bases JSON no
objeto bloqueadas con resultado estructurado y profundidad máxima de 64 niveles.
RED previo retenido: 23 tests con errores/fallos por tipos de base y ausencia de
límite. GREEN: 23 tests. No se afirma haber reproducido agotamiento de stack a
1000 niveles: la prueba acotada exige el nuevo límite preventivo a 65 niveles.
El recibo anterior conserva sus warnings históricos; el recibo posterior debe
identificar este delta exacto. No se borran ni reabren revisiones aprobadas.
