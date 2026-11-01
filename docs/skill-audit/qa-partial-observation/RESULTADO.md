# WU-SUP-INT-002 — Candidato pendiente de RDD

Observación review-b830a36d94741974/R3-001. RED original: exigir ACCEPTED al
fixture incoherente obtiene REJECT_INFRA. Es defecto del test, no de producción.
Fixture corregido: NOT_ASSESSED/PARTIAL, cero declaraciones en128registros;
exit0 con propuesta de éxito y exit2 con rechazo documental. Ambos se admiten
como protocolo y requieren revisión humana. Resultado no autoriza ejecución.
Caso anterior preservado como rechazo explícito de protocolo incoherente.

GREEN13tests del adaptador. Control negativo en copia temporal elimina ambas
condiciones de observación de la escalada; exit0 falla exactamente por
PARTIAL_MUST_REQUIRE_REVIEW. El runner del control devuelve0 solo si detecta
ese fallo previsto; stderr conserva FAILED del mutante, no fallo de producción.
No cambia qa_adapter.py, process_core.py, políticas ni versiones. Inyección de
resultado controlada verifica mapeo; no afirma ensayo físico ni calibración.
RDD pendiente. Recibos posteriores se asociarán al candidato exacto.
