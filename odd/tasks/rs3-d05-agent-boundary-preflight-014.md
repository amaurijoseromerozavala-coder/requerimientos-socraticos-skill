# WU-RS3-D05-AGENT-BOUNDARY-PREFLIGHT-014

## Objetivo y alcance

D05 eligió cuenta local separada, pero la frontera no está verificada en el i3
con WSL. Crear un sondeo de **solo lectura**, ejecutado desde la cuenta real de
Pi/Codex, para detectar errores locales observables antes de instalar una
credencial real: UID real/efectivo, cuenta de autoridad distinta y no root,
capacidades Linux efectivas, dueño/modo del directorio privado y posibilidad
de acceso desde el agente. No crear cuentas, archivos, claves ni servicio.

El resultado global siempre queda `SECURITY_BOUNDARY_UNMET`: una inspección de
metadatos no prueba ausencia de sudo, elevación futura, control del terminal o
del host Windows. El path no se imprime; el usuario suministra UID y directorio
de autoridad para el ensayo objetivo posterior. Un dato faltante o inaccesible
produce `NOT_ASSESSED`, no PASS.

## Oráculos RED congelados

1. El sondeo rechaza UID iguales, UID autoridad 0 y UID real/efectivo distintos.
2. Directorio inexistente, symlink, dueño incorrecto o modo distinto de 0700
   no permite observar una separación local.
3. Si el agente puede leer, escribir o atravesar el directorio, el resultado
   local es fallo.
4. Si no puede observar metadatos o capacidades, el resultado es inconcluso.
5. Aun con controles locales favorables, la salida no afirma D05 verificada,
   autenticidad humana ni ejecución autorizada; no incluye rutas ni secretos.

RED → implementación mínima → GREEN/regresiones → RDD exacto → respaldo Git.
La ejecución en el WSL objetivo queda NOT_RUN hasta que el humano corra el
comando allí. No se usa sudo ni credencial real en esta unidad.

## Evidencia RED/GREEN local

- RED: el nuevo test terminó exit 1 por `ModuleNotFoundError` del sondeador ausente.
- GREEN focalizado: 5 pruebas del sondeador terminaron OK. La prueba de
  condiciones favorables es una simulación etiquetada; solo verifica que la
  salida global permanece bloqueada.
- Ejecución local de solo lectura con directorio inexistente: `local_status=NOT_ASSESSED`,
  `real_authority_gate=SECURITY_BOUNDARY_UNMET`, `execution_authorized=false`.
  Es observación del entorno cloud, no del i3/WSL del propietario.
- Regresión: `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh`
  terminó exit 0: 55 CI, 127 supervisor, 62 QA y 342 requisitos.
