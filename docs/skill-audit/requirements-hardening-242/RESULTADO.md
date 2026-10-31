# Requerimientos socráticos 2.4.2 — mejoras aceptadas

Fecha: 2026-10-28. Cambios en la skill local y sus herramientas. Gentle AI real
4.2.0 empleado para revisión; upstream no modificado. Autorización humana:
«Entonces solo mejora lo que pasé tu analisis». El output QA se contrastó antes
de seleccionar mejoras; no se ejecutaron sus propuestas como órdenes humanas.

## ANALYSIS

El analizador lógico, las lecturas de objetos Git y el consumidor documental
usan `process_supervision.run_supervised`. Tiene entrada/salida no bloqueante,
presupuesto monotónico, grupos propios POSIX y vinculación del hijo directo al
padre en Linux. Al vencer el plazo o exceder la salida se detiene el grupo propio
y se intenta recogerlo dentro de una gracia adicional de1s. Limpieza incompleta
se declara; la vía Git bloquea ese resultado. No se garantiza tiempo real,
respuesta del kernel ni control de descendientes arbitrarios. El adaptador
preexec se limita a las CLIs de un solo hilo.

La vía Git ya no crea archivos temporales del candidato ni usa slots/leases.
Transmite una cabecera acotada y blobs por stdin. El receptor verifica tamaños,
rutas, OIDs SHA-256 de Git, truncación y datos adicionales. PRD, entrevista,
diseño y todos sus recibos se resuelven desde el mismo proveedor de bytes
inmutables. Cada lectura verifica y devuelve esos mismos bytes. El registro
consumed_files se compara con el manifiesto del padre.

Límites conservados:4096 entradas,8MiB por blob,32MiB de blobs totales y plazo
Git configurable hasta300s. Transporte: cabecera hasta2MiB, entrada del
supervisor hasta34MiB+8, salida por stream configurable hasta8MiB; consumidor2MiB.
Estos límites no equivalen a una cuota de RSS: mapas, payload y buffers pueden
coexistir. No materializar archivos del candidato tampoco impide swap del SO.
No se afirma aislamiento frente a modificación del motor/cuenta/kernel.

Se conservan APIs legacy de validación directa y errores existentes. Esa vía
filesystem sigue siendo lint sobre archivos mutables. Los schemas instalados
siguen formando parte del motor confiable. scratch_pool.py queda para pruebas
y compatibilidad histórica; no controla la vía Git actual.

normalize_text.py permanece idéntico a2.4.1 y conserva salida0600. CI continúa
diferido. No se creó QA Inquisidor ni se habilitó producción o avance global.

## TEST PLAN

Se registraron RED pertinentes antes de implementar: nuevas opciones del
supervisor ausentes; proveedor documental inexistente; transporte inexistente;
y rechazo explícito de la materialización de candidatos en la vía Git anterior.
Los logs se conservaron. El RED de transporte por módulo inexistente comprueba
ausencia de API, no demuestra individualmente todas sus futuras propiedades.

Después se comprobaron límites de entrada/salida, progreso simultáneo de pipes,
rechazo de metadatos/rutas, cambio de bytes, datos truncados/adicionales,
dependencias y recibos, OIDs por lectura y ausencia de archivos candidatos.
El caso específico de terminación del padre Git se añadió tras integrar y no
se presenta como RED previo: un fixture Linux pequeño verificó terminación y
recogida de su consumidor directo. Los harnesses tienen límites exteriores y
solo operan sobre procesos y datos propios.

Al reanudar, el fixture pendiente se corrigió antes de ejecutarse: Popen falla
explícitamente para entradas inválidas y no entrega un PID simulado a señales
reales. La inspección de procesos visibles no encontró el unittest anterior;
no se infiere de ello su historia de terminación ni la causa de la desconexión.

La prueba histórica de extracción se adaptó a la nueva obligación de no crear
un pool: interrupción durante colección de blobs y validación posterior no
dejan archivos candidatos. No se borraron los resultados históricos anteriores.

## VERIFICATION

- Regresión local completa: **168 tests OK**, `full-tests.log`,6.536s observados,
  con límite exterior45s. La duración no se promete como invariante.
- Contraste con copia de2.4.1: **10 casos con stdout/stderr/exit idénticos**,
  `differential.json`; cubre comandos de documentos y argumentos del analizador
  y sondeador. No equivale a comprobar todas las combinaciones de argumentos.
- CLI real `gentle-ai requirements validate`: PASS local, transporte
  VERIFIED_BYTES_STDIN y avance bloqueado, `public-git-validation.json`.
- Revisión independiente en copia separada: **35 tests OK,0 skips**, cuatro
  subsets con límite exterior20s, sin hallazgos materiales dentro del alcance.
  Hashes y detalles en independent-review.json/independent-manifest.json.
- RDD nativo: riesgo alto y cuatro lentes; lineage `review-c7092036da2c5504`.
  Estado approved en último evento y acknowledgement exacto completado.
  Candidato: `sha256:4e5755c816af2357d5f9e2f60235e0f3b2f27f108bfcb1d3adab8c2d11f4dc1b`.
- Los87 archivos seleccionados coinciden byte a byte con el árbol revisado
  `d5f96ce4a6b9e8130e0cd6d7c3940e0dd83ce82a`, `integrity-final.json`.

El intento inicial que incluía los logs íntegros excedió el presupuesto nativo y
no creó autoridad: rdd-over-budget.json. Se preparó otro candidato que conserva
código, schemas, contratos y pruebas completos; los logs permanecen externos y
sin truncar. No atribuir a la revisión nativa reproducción de168tests: esa
ejecución es local; la reproducción independiente tiene su propio alcance35.

validation.json conserva FROZEN_PRE_REVIEW y el marcador anterior al cierre;
no se modificó tras aprobar para insertar una autoaprobación. El estado final
se acredita mediante los recibos externos rdd-final.json y CIERRE-RDD.md.
Este informe es posterior y no se incluye como documento autoaprobado.

Hardware físico i3/WSL: NOT_RUN. Lean: NOT_RUN. Windows nativo: sin adaptador de
supervisión; macOS no ensayado. No certificación DO-178C, prueba universal de
ausencia de fallos ni determinismo absoluto. Se mantiene
BLOCKED_GLOBAL_ENFORCEMENT y la autoridad humana sobre requisitos y avance.

## Registro de preguntas y respuestas

Este ciclo repara herramientas; no reabre ni simula la entrevista de requisitos.
No se preguntó al humano ni se inventaron nuevas respuestas suyas. Las consultas
técnicas de implementación se resolvieron con el runtime y el código: venv local
existente; proveedor con scope y bytes inmutables; registro de archivos consumidos
ligado al manifiesto. Esas respuestas técnicas no crean decisiones de negocio.
