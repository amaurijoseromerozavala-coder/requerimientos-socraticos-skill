# WU-SUP-INT-001 — Adaptador QA interno

IMPLEMENTED_TESTS_PASS_RDD_PENDING. API QASupervisor(report,evidence_root,limits)
con comando fijo al comprobador local, intérprete del llamador y núcleo persistente
por instancia. No acepta comandos desde reportes. Sin entrada CLI ni autorización
de producción. No sustituye el supervisor ampliado pendiente del PRD.

Conserva canales acotados separados y observación de proceso. Solo combina exit
0/2/3 con protocolo consistente;2admite rechazo documental,3/señales/plazos/salida
incompleta son infraestructura. Protocolo inválido no culpa al documento. No infiere
OOM. Preserva resultado del checker como declaración, execution_authorized=false.
PARTIAL/NOT_ASSESSED/FAIL o evento no exitoso requiere revisión humana. Sin alertas
remotas. INFRA_LOCK impide nuevas llamadas en esa instancia; no es bloqueo durable
ni global. Excepción de core sin observación fiable también bloquea instancia.

RED: API ausente. SegundoRED: resolución del enlace del intérprete perdía la ruta
del virtualenv; se conserva ruta absoluta sin dereferenciar. GREEN final28tests,
12del adaptador más16regresiones. Comprobador real sobre documento inválido, proceso
real con stdoutJSON/stderrwarning y casos reales de señal/plazo con limpieza.
Mapeos y limpieza incierta también usan inyección controlada; no simulan estadoD
ni prueban hardwarei3/WSL. Logs originales conservados, no atribuidos a revisor.

Fuera de esta unidad: identidad sellada de entradas/checker, registro durable,
admisión entre instancias, recuperación, reserva de almacenamiento e incorporación.
Confía en checkout/intérprete locales. API devuelve bytes crudos en process; no es
un formato JSON serializable directo ni un recibo durable. Éxito de protocolo no
certifica exhaustividad del reporte, autoridad, verdad semántica ni producción.
