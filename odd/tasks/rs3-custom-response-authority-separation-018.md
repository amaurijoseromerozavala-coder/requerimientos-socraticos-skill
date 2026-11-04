# WU-RS3-CUSTOM-RESPONSE-AUTHORITY-SEPARATION-018

## Objetivo y alcance

Formalizar la decisión humana confirmada: la respuesta personalizada regresa al
interrogatorio, sin código, consumo de coordenada, commit ni recibo en el Git de
autoridad. La siguiente pregunta replanteada recibe nuevo snapshot, hashes y
enlace. Depende del contrato portable WU-017 y conserva D03/D05 sin habilitar
ningún perfil de autenticación.

Unidad documental: FSM y contratos de evidencia de la UI. No crea servidor web,
tarjetas ni cuentas; no afirma que una captura pruebe percepción humana. La UI
para teléfono fuera del host y su origen confiable quedan por decidir/probar.

## Oráculos RED congelados

1. Desde `CUSTOM_RESPONSE` no existe camino hacia recibo de autoridad sin pasar
   por reformulación, nuevo snapshot y selección explícita.
2. La respuesta personalizada solo puede conservarse en el historial de
   interrogatorio; jamás en Git de autoridad, y no solicita ni consume código.
3. El enlace lo emite el guardián y el agente solo lo transporta. Su token no
   confiere autoridad; la UI muestra el texto exacto además de SHA.
4. QA coteja contenido canónico y recibo Git; la imagen es evidencia auxiliar,
   no prueba que el humano la haya visto.
5. Toda ejecución de autoridad y toda prueba física continúan deshabilitadas.

RED → contrato → GREEN/regresión → RDD del candidato exacto → respaldo Git.

## Evidencia RED

Los cuatro controles terminaron exit 1 por `FileNotFoundError` para el contrato
de UI ausente. El fallo antecede a este contrato; no se ensayó navegador real.

## Evidencia GREEN y regresión

Cuatro controles focalizados, exit 0. `PATH=/tmp/ci-runtime-venv/bin:$PATH bash
ci/run_quality.sh` terminó exit 0: 55 CI, 130 supervisor, 62 QA y 350
requisitos. Es una verificación del contrato documental en cloud, no una
prueba de presentación en Firefox/Chrome ni del hardware objetivo.
