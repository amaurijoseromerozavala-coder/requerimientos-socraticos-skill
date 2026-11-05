# WU-RS3-UNVERIFIED-INTERROGATION-HISTORY-030

## Objetivo

Continuar WU-029: transformar un handoff de una pregunta propuesta en un
registro serializable WAITING_USER y añadir una respuesta literal retransmitida
como INTERPRETATION_REVIEW. No autenticar a quien envió el texto ni elevarlo
a decisión. La entrada y salida son documentos JSON acotados; el invocador
decide su custodia privada. No escribir al almacén de autoridad ni a Git.

## Alcance y precedencias

Exigir identidad y estructura del handoff; validar la transición y rechazar
repeticiones. Conservar bytes semánticos del texto recibido (Unicode sin
normalización), sin inventar sellos temporales. El CLI lee archivos regulares
acotados, o stdin para una respuesta; stdout devuelve el registro completo.
No existe canal humano autenticado: toda respuesta tiene origen
UNVERIFIED_RELAY. No capturar código de tarjeta, contraseña ni token.
No implementar D03/D05, persistencia, UI ni producción.

## Oráculos RED congelados

1. Handoff real de WU-029 crea exactamente un evento de pregunta pendiente;
   una respuesta añade un segundo evento literal y deja interpretación abierta.
2. Una mutación de pregunta con digest antiguo se rechaza antes de registrar.
3. Una respuesta que afirma confirmar o autorizar sigue siendo no verificada;
   el registro carece de permiso y el segundo envío se rechaza.
4. JSON malformado, duplicados, tamaño excesivo o transición inválida no
   producen registro parcial en stdout.

RED focal → GREEN/regresión → RDD exacto → respaldo Git.

## Evidencia

RED inicial: 3 tests, 2 fallos pertinentes por script ausente (exit 1).
GREEN inicial: 3 tests, exit 0. El control adversarial adicional recalculó
la identidad tras insertar campos de autoridad anidados: RED con 2 fallos
pertinentes (exit 1); tras cerrar las claves permitidas, GREEN de 4 tests
(exit 0). Regresión integral final `ci/run_quality.sh`: exit 0; CI 55,
supervisor 130, QA 62 y requisitos 391 tests. Hardware i3/WSL: NOT_RUN.
Un control posterior detectó que `QUESTION_PRESENTED` atribuía una entrega
no observada: RED de 1 test (exit 1), GREEN al usar `QUESTION_PROPOSED`.
