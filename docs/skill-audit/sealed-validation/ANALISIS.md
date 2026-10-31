# Contraste forense y corrección de herramientas documentales

## ANALYSIS

La regla protege terceros, no prohíbe toda falsación. Se aclara su alcance sin
permitir incumplir normas ni dañar hardware ajeno. No CI ni producción.

Hallazgo reproducido: FIFO como PRD principal bloqueaba la lectura directa; el
proceso de prueba se terminó a 0.5s, sin saturación ni lectura infinita de device.
Symlink externo /dev/zero: safe_file anterior lo rechazó (UNSAFE_PATH). No se
presenta esa hipótesis como exploit confirmado. Se endurecen también lecturas
secundarias contra especiales/symlinks y crecimientos, con límites explícitos.

La secuencia «hash antes de watch» no corresponde al código 2.1.1. La creación
bajo un padre vigilado debería provocar rechazo en filesystem Linux soportado;
no se midió WSL/DrvFS y no se inventa latencia ni falso PASS observado.
flock sigue siendo advisory; no se ofrecía exclusividad frente a terceros no
cooperativos. Un timeout no demuestra corrupción y el validador no escribe el
PRD. No hay determinismo temporal absoluto declarado.

## TEST PLAN y VERIFICATION

- 21 pruebas nuevas sobre IO/codificación/objetos Git; 43 de entrevista y 23 de
  guard previas, todas PASS (87 total). Logs separados.
- Lectura directa FIFO y /dev/zero regularidad rechazada antes de leer; symlink
  final y en componente, escape y tamaño se rechazan sin consumo descontrolado.
- Git: commit completo SHA1/SHA256, worktree corrupto y HEAD movido no alteran
  documento fijado. HEAD simbólico, OID de árbol, commit inexistente, symlink
  versionado y ruta relativa que escapa se rechazan. Repositorios/commits de tests
  son sintéticos y temporales; no se hizo commit del proyecto ni se publicó.
- LF: normalizador sobre copia UTF-8, rechazo BOM/UTF8 inválido y sobrescritura,
  secuencias JSON escapadas preservadas. Cambio físico LF→CRLF sigue rechazando
  una referencia de bytes obsoleta como STALE_DEPENDENCY, aunque el JSON tenga
  significado idéntico. No se declara esto como vulneración de seguridad.
- Depuración retenida: importación del helper safe_io faltó en harness importlib;
  se corrigió ruta de importación, no el oráculo. Un primer run descubrió tests
  importados dos veces; se corrigió discovery. No son RED de reglas semánticas.
- RED preexistente real: FIFO. Controles nuevos sobre Git/normalización verifican
  obligaciones nuevas; no se inventan resultados RED anteriores para todos.

## Diseño final 2.2.1

Vía principal `gentle-ai requirements validate repo --commit OID --prd prd.json`.
Cat-file/ls-tree, objetos verificados, protocolos/replace refs deshabilitados,
sin checkout, hooks ni filtros del candidato. Motor instalado confiable, copia
privada acotada. Inotify/flock quedan en lint diagnóstico, no autoridad.
Objeto fijado no autentica autor/revisor ni protege contra root o motor malicioso.
Consumo/producción siguen BLOCKED_GLOBAL_ENFORCEMENT; CI diferido por el usuario.

Normalizar nuevas entradas antes de generar evidencia. Mantener contratos de
hash histórico de bytes: no recertificar mensajes o approvals al normalizar.
Material real i3/WSL: NOT_RUN_TARGET_UNAVAILABLE. No se ejecuta estrés cloud como
sustituto. Sin nueva entrevista skill→asistente; registro histórico preservado.

RDD pendiente del candidato congelado: consultar recibo externo posterior.

## Seguimiento posterior de advisory R4-normalize-retry

La revisión nativa aprobada encontró WARNING: salida parcial tras fallo de escritura
podía impedir reintento. Se conservó aprobación y se abrió candidato independiente.
RED real: RLIMIT_FSIZE=1 en un subproceso, sin llenar disco, produjo salida parcial;
la aserción de ausencia de destino falló. Solución: temporal privado, escritura
completa/fsync y publicación por hard-link atómico sin sobrescribir, con limpieza
en fallos previos. GREEN sobre el mismo límite, reintento posterior válido;
21 pruebas nuevas PASS. El límite simula cuota de fichero, no disco lleno ni
fallo físico del SSD. No se atribuye prueba material i3/WSL a ese ensayo.
