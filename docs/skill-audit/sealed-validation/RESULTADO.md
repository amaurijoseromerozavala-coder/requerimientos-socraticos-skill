# Resultado 2.2.1 — Gentle AI nativo

Se usó la skill instalada, registro Gentle AI y RDD nativo real. Primer candidato
review-c82a0ca0d69af142 aprobado/acknowledged; corrección posterior del normalizador
review-f412da4c5db898a9 aprobada/acknowledged. Recibos rdd-final.json y
rdd-followup-final.json. No se atribuye ejecución de tests al revisor: tests
locales ejecutados, revisión independiente de patches/logs por el proveedor.

## Cambios comprobados

- Vía principal valida un commit Git completo fijado por OID y verifica sus objetos,
  sin leer documentos de worktree, ejecutar hooks/filtros ni configurar CI.
  Inotify y flock permanecen solo en diagnóstico/lint local.
- Lecturas directas con ancla de directorio, componentes O_NOFOLLOW, descriptor
  regular y presupuesto. Se reprodujo espera en FIFO principal y se corrigió;
  symlink externo /dev/zero ya era rechazado y no se presenta como exploit probado.
- Normalización UTF-8/LF explícita sobre nuevas copias, con hashes de bytes
  original/canónico separados. No se reescriben recibos ni se convierten hashes
  históricos de bytes en hashes semánticos. Rechazo por CRLF de referencia obsoleta
  permanece intencionado; normalizar antes de crear nueva evidencia.
- Fallo de cuota de fichero reproducido con RLIMIT_FSIZE=1 en un subproceso:
  salida parcial en RED. Temporal, fsync y publicación por hard-link sin overwrite
  corrigen el caso, con limpieza y reintento GREEN. No se llenó disco ni memoria.
- 21 pruebas nuevas,43 entrevista,23 guard =87 PASS. Casos Git SHA1/SHA256,
  HEAD movido/worktree corrupto, symlinks, especiales, límites y normalización.
- Fuente congelada verificada sin diferencias; inventario actual completo de los
  19 archivos QA coincide con la base, sin cambios. No se afirma historia continua.

## Aviso RDD retenido, sin ocultar ni reabrir aprobación

R3-001 WARNING: la salida publicada del normalizador tiene modo0600, heredado del
 temporal privado. Un consumidor de otra cuenta no puede leerla sin ajuste explícito.
No hay consumidor multiusuario configurado; sus permisos quedan como decisión de
integración pendiente. No se ensanchan permisos ni se afirma prueba de consumo entre
cuentas. El aviso está en el recibo nativo, no es cero findings ni fallo bloqueante.

## Reglas y estado

Se aclaró AGENTS.md y .codex/AGENTS.md: la protección de normas y hardware de
terceros sigue obligatoria. No prohíbe ensayos propios o autorizados conformes,
con límites/observación/parada. No se elimina protección para justificar QA.

BLOCKED_GLOBAL_ENFORCEMENT sigue vigente. Objetos Git fijados no prueban firma,
autoría confiable o permiso, ni protegen contra kernel/root/motor comprometidos.
No se hizo commit del proyecto, despliegue ni cambio remoto; commits en tests son
fixtures temporales. CI permanece diferido. i3/WSL físico: NOT_RUN_TARGET_UNAVAILABLE.
Sin nueva entrevista skill→asistente; registro real histórico preservado. Las
hipótesis sobre latencia, pérdida inotify y corrupción bajo swap no son resultados.
