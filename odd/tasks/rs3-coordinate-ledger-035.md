# WU-RS3-COORDINATE-LEDGER-035

## Objetivo

Materializar un registro local acotado para coordenadas **sin códigos**:
`AVAILABLE → PENDING → SPENT`. La reserva duradera debe anteceder a cualquier
solicitud de código en una integración futura. Una coordenada pendiente o
gastada nunca vuelve a disponible. El registro vincula `challenge_sha256`.

## Alcance y límites

Solo almacén sintético POSIX: directorio 0700, archivos 0600, bloqueo de
proceso, lectura acotada, escritura por etapa + reemplazo + fsync. Sin emisión,
almacenamiento ni verificación de códigos; sin recibos, Git de autoridad, UI,
cuenta real o `HUMAN_CONFIRMED`. No asumir resistencia a un actor con el mismo
UID ni a fallas del almacenamiento que mientan sobre fsync. D05 sigue
`SECURITY_BOUNDARY_UNMET`.

## Oráculos RED congelados

1. Dos reservas concurrentes de la misma coordenada: como máximo una retorna
   `PENDING`; la otra bloquea/observa ocupación. Reiniciar no libera PENDING.
2. `spend_pending` quema la coordenada, incluso si el recibo aún no existe.
   Reintento o cambio de `challenge_sha256` se rechaza. Otra coordenada sigue
   disponible.
3. Archivo incompleto, symlink, permisos erróneos, UID incorrecto, etapa
   sobrante o fsync fallido bloquean; no devuelven éxito incierto.
4. Respuesta y archivo no contienen códigos, autoridad ni permiso de ejecución.
   Estado desconocido o campo extra bloquea.

## Secuencia

ODD → RED ejecutado → implementación mínima → GREEN/regresión → RDD exacto →
respaldo. Los ensayos en el i3/WSL objetivo quedan NOT_RUN. Una integración
posterior probará que no solicita código antes de `PENDING` duradero.

## Evidencia local

- RED: el test nuevo terminó exit 1 por `ModuleNotFoundError` del registro
  ausente.
- GREEN focalizado inicial: 5 pruebas de concurrencia, reinicio, etapa
  interrumpida, fsync fallido y corrupción terminaron exit 0.
- La revisión independiente pidió dos falsadores adicionales: competencia
  entre procesos y fallo de fsync del directorio posterior a `os.replace`.
  Ambos se añadieron y 7 pruebas focalizadas terminaron exit 0. El segundo
  observa el estado visible tras la excepción; no simula pérdida de energía
  ni prueba durabilidad de un dispositivo que miente sobre fsync.
- Regresión con dependencias declaradas:
  `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh`, exit 0:
  55 CI, 145 supervisor, 62 QA y 409 requisitos.
- RDD del candidato final: pendiente. Equipo i3/WSL: NOT_RUN.
