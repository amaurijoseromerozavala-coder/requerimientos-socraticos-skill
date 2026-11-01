# WU-WSL-STORAGE-001 — Skill 2.4.8

Estado: IMPLEMENTED_TESTS_PASS_REVIEW_PENDING; instalación nueva todavía planificada.

La evidencia humana confirma una discrepancia guest/host: ext4 reportó878GiB
libres; Windows C:, donde resideUbuntu,14.59GiB. Se registra como histórica, no se
inyecta a métricas actuales. Swap configurado0, zRAM no observada; no se cambian.

Probe conserva free_bytes por compatibilidad, pero lo etiqueta VISIBLE_FILESYSTEM_ONLY;
host_volume UNKNOWN, free_bytes null, expansion_authorized false. Preflight1.1.0
separa storage_admission. Solicitar --storage-required-bytes N bloquea con exit3
si falta capacidad anfitrión actual; sin solicitud, NOT_ASSESSED y alcance de
viabilidad provisional de memoria, nunca permiso de almacenamiento. No hay aún
recolectorWindows, margen ni reserva física. Este bloqueo es explícito, no cierre
de esa brecha de medición. La versión1.0 antigua no cumple el nuevo schema.

source_checkout comprueba raízGit, origin oficial y HEAD legible de la skill,
no del proyecto examinado. Si no acredita clon local, bloquea workers y conserva
entrevista. Es metadato local, no autenticación ni identidad de archivos sin commit.
No ejecuta clone/fetch/pull/reset. Disponibilidad futura no se puede garantizar.

RED almacenamiento:5 tests con errores de campos/API faltantes. RED clon:2casos
faltantes. GREEN:7 tests nuevos y8 regresiones de activación. Dos invocaciones
reales cloud (sin/con solicitud1024bytes) satisfacen schema1.1.0 y estados esperados.
No prueba de acceso al equipo del usuario ni calibración física.

Registros .agents/.codex apuntan aún a réplica antigua. installation-plan.json
prevé reenlazarlos al clon oficial verificando precondiciones solo trasRDD. No
modificar ni publicar el candidato retained-pipe, que conserva consentimiento
pendiente separado. Entrevista independiente real: interview.json.

## Revisión independiente posterior
El revisor /root/wsl_review_final detectó dos P2: HEAD sin comprobar objeto commit
y schema sin invariantes suficientes entre admisión y estado. Se corrigieron usando
HEAD^{commit} y condiciones del schema. Controles negativos: review-red.stderr
registra4fallos esperados; review-green.stderr registra9testsPASS. También se
reejecutaron8regresiones de activación y9de entorno:PASS. Sin calibración del i3.
