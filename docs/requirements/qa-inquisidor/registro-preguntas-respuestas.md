> **Aclaración posterior:** este archivo registra la conversación usuario-asistente. No es el registro skill-asistente solicitado; ese registro está en `registro-skill-asistente.md`.

# Registro de preguntas y respuestas — QA Inquisidor

Estado de la entrevista: **incompleta**. PRD: **DRAFT**.

Este registro cubre la entrevista de requisitos y sus aclaraciones; no toda la
conversación previa sobre instalación. Las citas distinguen respuestas del
usuario y del asistente. Se actualizará y entregará con las próximas respuestas
sobre esta entrevista. Su versión estructurada está en
`registro-preguntas-respuestas.json`.

## Aclaración de alcance — CL-001

**Usuario, literal:**

> En gentle aí

**Respuesta del asistente, literal:**

> Sí, lo prepararé dentro de la instalación de **Gentle AI**, usando `requerimientos-socraticos`. El entregable será el PRD de `qa-inquisidor`; todavía no crearé ni activaré esa nueva skill.

Esta aclaración no autoriza instalar la futura skill.

## Pregunta de requisitos — Q-001

**Asistente, pregunta literal:**

> Para convertir «determinismo absoluto» en un requisito comprobable, ¿qué criterio debe usar QA Inquisidor?

**Opciones ofrecidas, literales:**

1. Exigir repetibilidad con entradas, versiones y entorno fijados, y declarar lo no demostrado (recomendado).
2. Mantener la exigencia absoluta y bloquear el cierre mientras no pueda demostrarse.

**Usuario, respuesta literal:**

> Exigir repetibilidad con entradas, versiones y entorno fijados, y declarar lo no demostrado (recomendado).

**Asistente, respuesta posterior literal:**

> Queda confirmado: QA Inquisidor exigirá **repetibilidad con entradas, versiones y entorno fijados**, y declarará lo no demostrado.
> 
> El PRD también exigirá cubrir el sistema completo mediante un inventario de componentes y contratos. La economía de tokens podrá cambiar cómo se consulta ese inventario, pero no permitirá presentar una revisión del último diff como una revisión integral.

**Decisión confirmada:** evaluar repetibilidad bajo entradas, versiones y entorno
fijados, y declarar lo no demostrado. Esta respuesta no fija tolerancias ni
aprueba el resto del PRD. El segundo párrafo del asistente trata otro requisito
original; no amplía la decisión sobre determinismo.

## Pregunta sobre el proceso — Q-002

**Usuario, pregunta literal:**

> Una pregunta la skill requerimientos solo hizo una sola pregunta??

**Asistente, respuesta literal:**

> Sí. Solo hizo una pregunta: cómo interpretar **«determinismo absoluto»**.
> 
> Fue insuficiente para el alcance que planteaste. Avancé demasiado en la redacción y resolví por interpretación temas que necesitaban contrastarse contigo: qué incluye «todo el sistema», qué significa «no tolerar happy paths», cuándo detener la búsqueda y cómo evaluar una arquitectura como mejor.
> 
> La skill pide **una pregunta por turno**, no una pregunta en total. El PRD sigue siendo un borrador; la revisión RDD de sus documentos no sustituye esa entrevista ni confirma tu intención.
> 
> Debemos continuar la entrevista antes de considerarlo endurecido.

Esta pregunta la formuló el usuario; no cuenta como otra pregunta socrática del
asistente.

## Petición de este registro — REQ-LOG-001

**Usuario, literal:**

> Ok cuando respondas tu dame un documento con el registro de las preguntas y las respuestas que diste

**Cumplimiento:** se crean este documento y su versión JSON. Los documentos
anteriores del PRD y sus recibos de revisión no se modifican con este registro.

## Temas pendientes: todavía no preguntados

Estos son temas por aclarar, no preguntas ya realizadas ni respuestas atribuidas
al usuario:

- P-001: frontera y componentes de «todo el sistema objetivo».
- P-002: significado de «no tolerar happy paths» y controles positivos.
- P-003: parada, presupuesto y tratamiento de pendientes.
- P-004: criterios para comparar arquitectura, diseño, bibliotecas y tecnologías.
- P-005: condiciones observables de cierre de cada fase.

No hay respuestas registradas para estos temas. Se abordarán de uno en uno.

## Balance

- Preguntas de requisitos formuladas por el asistente: **1**.
- Respuestas humanas a esas preguntas: **1**.
- Entrevista completa: **no**.
- Una revisión RDD documental no confirma la intención del usuario ni sustituye
  sus respuestas.
