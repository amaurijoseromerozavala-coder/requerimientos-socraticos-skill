# WU-SUP-INT-001 — Adaptador interno de QA

Solicitud: continuar integración supervisor/QA. Incremento: API interna local que
invoca exclusivamente validate_report.py con rutas fijadas al construir instancia.
Sin CLI de producción, admisión global, journal durable, incorporación ni recuperación.
Conserva la instancia del núcleo para propagar INFRA_LOCK; nunca autoriza ejecución.

Oráculos: stdout y stderr separados; exit0 no equivale PASS; salida2 solo admite
REJECT_INPUT con protocolo coherente; exit3/señal/plazo/captura incompleta se
clasifican INFRA_FAILURE. Señal no demuestra OOM. JSON duplicado, inválido, profundo
o incoherente se rechaza como protocolo/infraestructura, no culpa documental.
PARTIAL/NOT_ASSESSED o declaraciones FAIL requieren revisión humana. Preservar
bytes originales acotados y observación declarada sin convertirla en evidencia.

TDD: RED de API ausente, GREEN con procesos locales acotados y comprobador real;
inyección de estados prueba mapeo y bloqueo, no reproduce fallo físico del kernel.
RDD nativo exacto antes de commit/push. Límites del núcleo sin ampliación.

## Log
RED de API ausente registrado. RED de ruta venv observado y corregido. GREEN final
28tests (12adaptador+16núcleo); RDD pendiente. API interna sin integración durable.
