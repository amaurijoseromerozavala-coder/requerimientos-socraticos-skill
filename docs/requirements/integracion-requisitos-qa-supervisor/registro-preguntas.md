# Registro de decisiones de integración

Modo: entrevista directa asistente-humano. Preguntas resumidas con opciones originales; respuestas literales. Sin diálogo independiente simulado.

## INT-D01

Pregunta/contexto: ¿Confirmas A+B+C al diseño con activación progresiva, sin instalaciones, implementación ni CI/producción?

Respuesta literal: «Confirmo».

Significado registrado: A+B+C incluidas en diseño; activación progresiva; sin autorización operativa.

## INT-D02

Pregunta/contexto: ¿Dónde coordinar: coordinador separado, dentro de requisitos o ampliando supervisor?

Respuesta literal: «Ampliar el supervisor».

Significado registrado: Ampliar el supervisor como coordinador del esquema integrado.

## INT-D03

Pregunta/contexto: ¿Ejecución mediante adaptadores registrados, comandos generales o solo checker actual?

Respuesta literal: «A».

Significado registrado: Adaptadores registrados con contratos explícitos.

Nota: La pregunta numeraba1/2/3; el asistente explicitó A=primera opción. Esta interpretación se conserva como tal; no añade capacidades no enumeradas.

## INT-D04

Pregunta/contexto: ¿Cómo admitir adaptador: A revisión técnica y aprobación humana de versión/permisos; B automática; C lista fija?

Respuesta literal: «A».

Significado registrado: Revisión técnica y aprobación humana de versión y permisos antes de habilitar.

## INT-D05

Pregunta/contexto: ¿A ejecutar dentro de tarea autorizada; B permiso cada ejecución; C autonomía por política?

Respuesta literal: «A».

Significado registrado: Ejecutar dentro de tarea ya autorizada, sin repetir permiso; ampliaciones vuelven al humano.

## INT-D06

Pregunta/contexto: ¿A una ejecución supervisada; B concurrencia adaptativa; C concurrencia fija configurable?

Respuesta literal: «A».

Significado registrado: Una ejecución supervisada a la vez; no implica un único hilo/subproceso interno.

## INT-D07

Pregunta/contexto: ¿A detener tarea sin reintentos, comprobar limpieza; B reintentos idempotentes; C bloqueo global ante todo fallo?

Respuesta literal: «A».

Significado registrado: Registrar fallo, detener tarea y no reintentar automáticamente; otra ejecución exige terminación y limpieza requerida confirmadas.

Q-INT-001 deja de estar pendiente: humano pidió las tres capas y confirmó su incorporación al diseño.

Siguiente dimensión pendiente: ubicación de escrituras de adaptadores de planificación/implementación. No inferir rollback de archivos de la palabra limpieza.

## INT-D08

Pregunta/contexto: ¿Dónde escribir: A espacio aislado; B proyecto directamente; C solo propuestas?

Respuesta literal: «A».

Significado registrado: Adaptadores con escritura trabajan en espacio aislado; incorporación al proyecto es una operación explícita.

## INT-D09

Pregunta/contexto: ¿Ante fallo: A conservar cambios parciales y evidencias; B eliminar parciales; C política por adaptador?

Respuesta literal: «A».

Significado registrado: Conservar cambios parciales y evidencias aislados, sin incorporarlos al proyecto; presupuesto de almacenamiento pendiente.

## INT-D10

Pregunta/contexto: ¿Incorporación: A aprobación humana por conjunto; B automática dentro de tarea autorizada y criterios cumplidos; C exportación manual?

Respuesta literal: «B».

Significado registrado: Incorporación automática dentro de tarea previamente autorizada cuando todos sus criterios verificables se cumplan; sin permiso implícito de commit/push/despliegue.

## INT-D11

Pregunta/contexto: ¿Si cambia el proyecto base: A detener y reevaluar; B integrar automáticamente y repetir verificaciones?

Respuesta literal: «A».

Significado registrado: Detener incorporación, conservar resultado aislado y reevaluar sobre nueva base; no reutilizar evidencia afectada como vigente.

Q-INT-008 resuelta por INT-D08. Siguiente dimensión: recuperación si la incorporación al proyecto queda incompleta; no equivale a reintentar tarea.

## INT-D12

Pregunta/contexto: ¿Recuperación parcial: A restauración automática condicionada; B intervención humana siempre?

Respuesta literal: «A».

Significado registrado: Restaurar automáticamente solo con base recuperable y sin sobrescribir cambios ajenos; si no se puede comprobar, bloquear y escalar.

## INT-D13

Pregunta/contexto: ¿Almacenamiento: A presupuesto por tarea y límite total; B solo límite total?

Respuesta literal: «A».

Significado registrado: Presupuesto por tarea y límite total del supervisor; comprobar ambos antes de iniciar; no borrar automáticamente trabajos conservados.

## INT-D14

Pregunta/contexto: ¿Límite total: A1GiB, B2GiB, C otro valor?

Respuesta literal: «C pero la se ajusta un presupuesto y si se excede se pide autorización para ampliar previo a un prefitgh que confirme disponibilidad del espacio requerido para no autorizar sin que exista la disponibilidad real».

Significado registrado: Presupuesto ajustable; ampliación requiere autorización humana precedida por preflight que compruebe disponibilidad requerida. No se seleccionó una cifra fija.

## INT-D15

Pregunta/contexto: ¿Ampliación de tarea y total: A solicitud conjunta con ambos incrementos explícitos; B aumento global implícito?

Respuesta literal: «A».

Significado registrado: Una solicitud enumera ambos cambios cuando sean necesarios; aprobación explícita de cada monto, sin ampliación global implícita.

## INT-D16

Pregunta/contexto: ¿Presupuesto inicial: A supervisor estima, comprueba y lo incluye en autorización de tarea; B monto indicado por humano?

Respuesta literal: «A».

Significado registrado: Supervisor propone estimación explicada, comprueba disponibilidad e incluye presupuesto inicial en la autorización de tarea.

## INT-D17

Pregunta/contexto: ¿Parte material no estimable: A bloquear hasta información suficiente; B proponer exploración acotada autorizada?

Respuesta literal: «B».

Significado registrado: Proponer exploración con presupuesto propio y sin modificar proyecto principal; requiere autorización suficiente; tarea principal bloqueada mientras falte estimación.

## INT-D18

Pregunta/contexto: ¿Exploración: A inspección y muestras pequeñas con adaptadores habilitados, sin código del proyecto; B comandos del proyecto aislados y autorizados?

Respuesta literal: «A».

Significado registrado: Exploración limitada a inspección y muestras pequeñas mediante adaptadores habilitados; no ejecutar código del proyecto.

## INT-D19

Pregunta/contexto: ¿Exploración agota presupuesto: A detener y declarar desconocidos; B solicitar ampliación previa disponibilidad?

Respuesta literal: «B».

Significado registrado: Detener exploración al agotar presupuesto y preparar ampliación tras preflight; requiere nueva autorización antes de continuar.

## Q-INT-020 — Revocación durante ejecución

Pregunta al humano: Si revocas una autorización durante una ejecución, ¿debe A detener el trabajo mediante parada controlada y conservar evidencias, permitiendo solo limpieza/restauración previamente autorizadas; o B terminar la unidad en curso sin iniciar otra?

Respuesta pendiente. No se infiere permiso de continuar, restaurar o finalizar después de revocación.

## INT-D20

Pregunta/contexto: ¿Revocación durante ejecución: A parada controlada; B terminar unidad en curso sin iniciar otra?

Respuesta literal: «B».

Significado registrado: Revocación diferida: permite terminar la unidad en curso, sin iniciar otra; no amplía alcance, recursos ni permisos.

## INT-D21

Pregunta/contexto: ¿Unidad en curso: A una invocación de adaptador; B tarea completa con varias invocaciones?

Respuesta literal: «B».

Significado registrado: La unidad protegida por revocación diferida es la tarea completa en curso, incluidas varias invocaciones dentro de su autorización existente.

Q-INT-020 resuelta por INT-D20/21: revocación diferida a tarea completa. Q-INT-022 pendiente: elegibilidad de incorporación automática tras revocación.

## INT-D22 / Q-INT-022

Pregunta: ¿conservar resultados aislados y pedir autorización nueva(A), o incorporación automática originalmente autorizada(B), después de revocación?

Respuesta literal: «A».

Confirmado: finalizar tarea no habilita incorporación tras revocación; resultados aislados requieren nueva autorización de incorporación. Excepción explícita a INT-D10, no contradicción ni anulación de su política general.

## INT-D23 — Revocación durante incorporación

Pregunta: A terminar incorporación iniciada, o B detener nuevas escrituras y aplicar recuperación condicionada.

Respuesta literal: «B».

Confirmado: detener incorporación; recuperación solo bajo condiciones de INT-D12; si no se puede comprobar restauración segura, bloquear y pedir intervención. No se interpreta como garantía de interrupción instantánea ni prohibición de las escrituras necesarias para restaurar.
