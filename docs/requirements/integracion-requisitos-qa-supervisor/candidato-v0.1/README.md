# Supervisor ampliado: primer candidato documental

Estado: DRAFT; diseño parcial, no implementación ni PRD canónico aprobado.

Este candidato formaliza las23decisiones del humano dentro del esquema
Requerimientos Socráticos + QA Inquisidor + supervisor ampliado. No ratifica
indiscriminadamente el catálogo externo de140requisitos ni instala herramientas.

## Archivos

- requirements.json:23obligaciones EARS con falsadores, ligadas al registro humano.
- contracts.json: contratos de adaptadores, autoridad, recursos, incorporación y
  orden de aceptación de revocación/escrituras; mecanismos técnicos propuestos.
- incorporation-gate.json: tabla lógica de admisión,7booleanos derivados de
  evidencia externa; no aceptar booleanos arbitrarios como autoridad.
- fsm.json: proyección parcial del control de incorporación,9estados/13aristas
  locales y handler global de revocación; no es FSM global del supervisor.
- open-gaps.json: pendientes que impiden READY y habilitación.

## Evidencia acotada

Gentle AI4.2.0 observado; RDD ON; preflight cloud admite evaluación local con sus
límites. No equivale al i3/WSL del humano. RED documental de4artefactos ausentes
registrado antes de crearlos. Verificación local:23trazas,128valoraciones del gate,
9estados alcanzables en grafo y13aristas únicas. Control negativo al quitar regla de
revocación detecta1valoración incorrecta. UNKNOWN se rechaza sin convertirlo aFalse.

Estos resultados no prueban correspondencia del modelo completo con el sistema,
relojes, archivos, exclusión de escritores, recepción real de permisos, recuperación,
seguridad física ni ejecución de adaptadores. Tests de implementación:NOT_RUN.

La revisión independiente de documentos y el recibo nativo RDD se registran en
../../../skill-audit/integration-candidate-01/. La aprobación de un borrador parcial,
si llega a obtenerse, no cierra sus desconocidos ni autoriza implementar.

## Autoridad y alcance conservados

Una tarea en aislamiento puede terminar tras revocación diferida; incorporación
posterior necesita nueva autorización suficiente. Si la revocación se acepta
mientras se incorpora, detener nuevas escrituras bajo el epoch revocado y recuperar
solo si es seguro. Operaciones ya emitidas o de resultado incierto no se presumen
canceladas. Registrar nuevo epoch invalida elegibilidad anterior de incorporación.

La retención32MiB/manual solo cubre salidas QA. Los presupuestos de workspaces
son ajustables con preflight antes de pedir ampliación; montos/mecanismos concretos
siguen pendientes. CI, producción, instalación e implementación no autorizadas.
