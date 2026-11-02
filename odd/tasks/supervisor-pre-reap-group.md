# WU-SUP-PRE-REAP-007 — limpieza acotada del grupo propio

## Solicitud y frontera

El propietario pidió desarrollar la siguiente unidad técnica tras revisar QA. El núcleo Linux debe atender a miembros activos de su grupo cuando el hijo directo termina primero. La identidad del grupo solo se usa para enviar señales mientras el hijo directo sigue sin recolectarse; un resultado incierto mantiene `INFRA_LOCK`. No se promete contener procesos que cambian de sesión ni recuperación del journal.

## Oráculo

- Un hijo directo que termina con código 0 y deja un miembro del mismo grupo debe dar lugar a solicitud de terminación al grupo antes de recolectar al hijo. Si ese miembro no atiende la primera solicitud, debe aplicarse la escalada acotada antes de recolectar.
- El resultado solo declara `CONFIRMED` si el hijo fue recolectado y no queda miembro activo observado en el grupo. Si la observación falla, conserva `INFRA_LOCK`.
- Un hijo normal sin miembros activos conserva salida normal y no recibe señales innecesarias.
- Las pruebas usan procesos breves y limpieza explícita, sin presión de CPU, RAM o disco. La prueba en i3/WSL sigue pendiente.

## Secuencia

1. RED: adaptar prueba real de miembro persistente y su control de captura; conservar salida del fallo.
2. GREEN: observar salida del hijo sin recolectarlo, terminar el grupo vinculado, recolectar y verificar regresiones.
3. RDD de Gentle AI del candidato exacto; solo con recibo aprobado/reconocido, commit y respaldo GitHub.

## Registro

- 2026-11-02: ODD abierto antes de modificar código y pruebas.
- RED de grupo: el hijo terminó y el miembro del grupo siguió activo; `signals_requested=[]` (control en `group-red.stderr`).
- RED de admisión: la limpieza del grupo tras la salida del hijo se presentaba como `EXITED`; ahora debe ser `STOPPED/GROUP_CLEANUP` (`admission-red.stderr`).
- RED de observación: una lectura activa inmediatamente después de la escalada producía `UNCONFIRMED` sin agotar el plazo de limpieza (`escalation-red.stderr`).
- RED documental: README aún describía la política previa (`readme-red.stderr`).
- GREEN: suite local acotada, 64 pruebas OK en 12.412 s (`full-green.stderr`). La prueba de hardware objetivo sigue NOT_RUN para esta unidad.
- RDD del candidato exacto pendiente.
