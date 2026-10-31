# Correcciones filtradas y autorizadas — 2.3.0

## Alcance y autoridad

El humano autorizó ejecutar las correcciones que pasaron el filtro del análisis.
No se ejecutaron mandatos QA por su mera redacción. Se mantienen normas de
OpenAI/terceros, protección de hardware, QA/producción bloqueados y CI diferido.

## Cambios

- Perfil de validate_git exclusivamente SHA256: formato de repositorio y OID64,
  hash SHA256 de objetos, sin compatibilidad SHA1 implícita ni migración automática.
- Pool fijo de cuatro slots privados con leases. Recolección solo del bundle de
  un slot exclusivo, no glob de /tmp ni PID/TTL. Locks persistentes fuera del
  bundle; consumidor Python hereda fd, protegiendo sus datos tras muerte del padre.
- Salida normalizada0600 explícita en descriptor y contrato JSON OWNER_ONLY.
  No universal0644; lectura por otra cuenta/canal requiere integración autorizada.
- safe_io deja explícito el carácter heurístico de los metadatos; lectura directa
  no es transacción atómica frente a escritores adversarios. Sin fingir fix mágico.

## Evidencia

RED real SHA1: nueva aserción SHA256_REQUIRED falló antes del cambio porque se
aceptaba SHA1; sha1-red.stderr. Defecto de orfandad previamente reproducido en
la auditoría QA: docs/skill-audit/qa-output-review/ANALISIS.md (SIGKILL,41bytes).
No se inventa RED por regla para un módulo de lifecycle que todavía no existía.

Pruebas actuales: 23 sealed +12 scratch +43 interview +23 guard =101 PASS.
Incluyen SIGKILL real de proceso propio durante extracción del motor, recuperación
al reutilizar slot; padre muerto con consumidor vivo/lease heredado no se limpia;
tras salida del consumidor se recupera. Capacidad de cuatro slots: quinto intento
bloquea, sin borrar slots activos; symlink/bundle inseguro/lease hardlinked/modos
abiertos se rechazan; namespace ajeno no se toca. Los tests son acotados y usan
repositorios/commits sintéticos temporales. No hay OOM ni agotamiento de disco.

## Límites

Mitigación de acumulación del motor, no limpieza inmediata tras SIGKILL ni cuota
kernel. Máximo cuatro bundles x32MiB de blobs más metadatos por UID/ancla TMPDIR
cooperativa; una cuenta hostil puede ignorar protocolo y queda fuera del modelo.
La limpieza resistente a symlinks exige soporte Linux de shutil.rmtree; si falta,
se bloquea. Temporales legacy y los de otros comandos no se borran automáticamente.
El lease no garantiza integridad contra el mismo UID hostil; objetos SHA256 fijados
identifican contenido pero no revisión auténtica ni autoridad de producción.
Permisos entre cuentas siguen siendo decisión del consumidor futuro, no 0644 global.
Material i3/WSL: NOT_RUN_TARGET_UNAVAILABLE. No hubo nueva entrevista skill→asistente.

RDD nativo pendiente del candidato congelado: ver recibo externo posterior.
