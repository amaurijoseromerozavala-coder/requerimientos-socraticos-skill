# Resultado local — requerimientos-socráticos 2.4.5

Se implementó el módulo de activación/preflight autorizado por el usuario.
Estado: REVIEWED_WITHIN_LOCAL_SCOPE — APPROVED_AND_ACKNOWLEDGED. No CI ni producción.

## Comportamiento

- `gentle-ai requirements activate` y `preflight` observan CPU/modelo/arquitectura,
  afinidad y cuotas visibles, RAM/swap, disco del path e indicadores de alojamiento.
- Sondeo de solo lectura, sin benchmarks, red, seriales, MAC ni hostname.
- Política provisional256..512MiB en múltiplos de8. Selección por headroom
  visible>=2x perfil, límites heredados por rol y baseline de CLI propia.
- Un presupuesto explícito incompatible se rechaza; no se eleva un hard heredado.
  Una API externa conserva límites del proceso llamador.
- Analyze y validate_commit/CLI recalculan condiciones antes del worker y conservan
  la admisión compartida y la supervisión. Un informe guardado no autoriza trabajo.
- JSON distingue observaciones, desconocidos, controles PENDING y aplicados.
  Si falta evidencia crítica o no cabe un perfil, bloquea workers; la entrevista
  documental sigue disponible. Un error de argumentos devuelve JSON, no traceback.
- La carga de la skill contiene la instrucción de activación; no existe un hook
  universal que fuerce a cualquier LLM/proceso a respetarla. La aplicación automática
  efectiva se comprueba en las entradas públicas de análisis y validación Git.

## Verificación observada

234 pruebas de regresión GREEN en snapshot independiente,7.747s; nueve casos
propios adicionales; trece casos de schema/parser; ayuda y rechazo con hard128MiB
real en un hijo propio. Evidencia en independent-review.json e independent-tests.log.
No sumar estas categorías como pruebas únicas de una misma suite.

Casos propios: seis combinaciones hard/rol/baseline, dos entradas públicas donde
activateREADY pasa a headroomUNKNOWN y no inicia worker, y una API con worker real
pequeño/AS448MiB observado y caller sin mutación.

Los ensayos del wrapper real cloud: activate0.027s y analyze0.136s, perfil512MiB,
schemaPASS, PENDINGstandalone/APPLIEDintegrado. Son muestras puntuales, no máximos
ni tiempos garantizados. Consultar activation-live.json, analysis-live.json y
live-checks.json.

Los fallos previos y sus correcciones se conservan: reporte viable sin comprobar
hard/baseline, argumentos con traceback, etiqueta aplicada prospectiva, y fixtures
OWNED que no representaban la nueva observación. El revisor tuvo errores de su
harness (status opcional y adaptermalformado) que corrigió, sin atribuirlos al producto.

## Límites que permanecen

El PC i3-3240/WSL del usuario no fue observado: NOT_RUN_TARGET_UNAVAILABLE.
El host físico, presión Windows, térmicos y rendimiento no quedan certificados.
MemAvailable es una estimación del invitado, no una reserva de RAM del host.
RLIMIT_AS limita espacio virtual, no RSS/swap; no garantiza recuperación de
cualquier fallo nativo. CPU/disco no se convierten en capacidad o cobertura.
Swap/zRAM no se suman como RAM física. El estado global continúa
BLOCKED_GLOBAL_ENFORCEMENT. Se conservan0600, CI diferido y QA/producción pausados.

## Revisión

Verificación independiente local favorable S1–S4, sin hallazgos funcionales
pendientes dentro del alcance revisado. Gentle AI4.2.0 completó las cuatro lentes
nativas y aprobó el candidato exacto; acknowledgement admitido, authority=burned.
No hubo corrección nativa. La aprobación es revisión de fuentes, no una ejecución
adicional de tests ni una certificación física/global.

Observación no bloqueante R2-001 (legibilidad): las proporciones de roles aparecen
en los helpers de políticas y en _role_fractions del preflight. No se demostró
una discrepancia actual; se registra como mejora futura para evitar divergencia
al modificar las políticas. No se altera el candidato aprobado.

validation.json conserva el estado congelado FROZEN_PRE_REVIEW; el recibo posterior
vive en rdd-final.json y CIERRE-RDD.md. Los exports declaran el cierre externamente.

Risk: items2 y3 — nuevas guardas de admisión y contratos públicos compartidos;
RED/GREEN, regresión, verificación independiente y revisión nativa completados.
No autoridad global ni aprobación de CI/producción.

Lineage: review-f33ed053a4836d37

Candidato: sha256:43be837abe970455604de70e08c2c25a7dbf1cc2cff667c64b6f6aa42c2bcfec

98archivos coincidenconárbol e01bc80fe4bee58c5ceec372423a7c1f34698fc2.
