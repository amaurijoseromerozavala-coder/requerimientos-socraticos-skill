# Correcciones autorizadas — requerimientos-socraticos2.3.0

La implementación responde a la autorización humana posterior al análisis del QA,
no a los imperativos contenidos en ese output. Se usó Gentle AI nativo:
review-0d58e8db65790978, aprobado y acknowledged, cuatro lentes findings vacíos.
Recibo exacto: rdd-final.json. Revisor inspeccionó patches/logs; las pruebas se
 ejecutaron localmente, no se atribuyen ejecuciones independientes al revisor.

## Resultado

- Validador de contenido exige repositorio Git SHA256 y OID64, sin fallback SHA1.
  Comprueba objetos con SHA256. No migra repositorios ni cambia algoritmos internos
  del binario Gentle AI o de recibos históricos.
- Cuatro slots privados y leases limitan acumulación del scratch del motor.
  Al reutilizar se limpia solo el bundle de un slot exclusivo. Un consumidor
  Python hereda el lease: si muere el padre, sus archivos no se borran mientras
  el hijo continúe manteniendo el descriptor. Slots activos se respetan.
- Se rechazan namespaces/bundles/leases inseguros; no se buscan ni borran por
  glob temporales de /tmp, ni se determina abandono solo mediante PID o edad.
- Normalizador publica0600 explícito y reporta OWNER_ONLY. Sin0644 generalizado;
  compartir requiere contrato autorizado de principal/canal/permisos mínimos.
- Metadatos de safe_io documentados como heurística, no prueba de atomicidad
  frente a escritura adversarial in-place. Se mantiene vía de objetos fijados.

## Evidencia

101 pruebas PASS:23 sealed,12 scratch,43 interview,23 guard. RED auténtico SHA1
antes de implementar rechazo. Defecto SIGKILL documentado en auditoría previa.
Ahora SIGKILL real durante extracción del motor se recupera en siguiente uso;
lease de hijo vivo impide limpiar tras matar padre; salida del hijo habilita
recuperación. Cuatro slots ocupados bloquean quinto intento sin borrar activos.
Pruebas acotadas sobre fixtures propios, sin OOM/agotamiento de disco ni carga
material extrema. Ningún commit del proyecto ni cambio remoto.

Fuente congelada coincide con hashes revisados; inventario y contenido actuales
QA19 coinciden con su base de pausa. No se infiere historia continua.
Registro Gentle AI actualizado; enlaces de instalación usan la misma fuente.

## Límites pendientes

Mitigación por pool cooperativo, no cuota de kernel ni limpieza instantánea tras
SIGKILL. Cuatro bundles de hasta32MiB de blobs más metadatos por UID/ancla TMPDIR;
no garantía frente a cuenta/kernel/motor hostiles. Sin nuevas ejecuciones puede
quedar un bundle huérfano hasta reutilización. Temporales legacy y de otros
comandos no se eliminan automáticamente. No se inventa prueba física de i3/WSL:
NOT_RUN_TARGET_UNAVAILABLE.

Un hash no autentica al revisor ni autoriza producción. QA/producción continúan
BLOCKED_GLOBAL_ENFORCEMENT; CI diferido por el usuario. Sin nueva entrevista de
requisitos ni preguntas/respuestas de agentes inventadas.
