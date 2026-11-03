# RS3-WU-PROPOSAL-IR-001

## Alcance

Entrada de diseño: ZIP RS3-HANDOFF-001, SHA-256
`83a83c77921f7737e89328b8dae365e7d0e7047f0c3fc7acbf7af2fd8f6c2d7e`.
Se implementa un comprobador de **propuestas** IR booleanas con contrato
explícito, sin resolver aún el significado humano de `production_ready` ni
emitir autoridad humana. Corresponde a una parte acotada de T013–T016.

## Oráculos RED

- `NECESSARY_CONDITION(P,Q)` compila solamente `P→Q`; el testigo P=true,
  Q=false la falsifica. `SUFFICIENT_CONDITION(Q,P)` compila `Q→P`.
  `EQUIVALENCE` compila P↔Q. Dirección inconsistente es rechazada.
- `MAY`, `SHOULD`, `UNDETERMINED`, excepción o supuesto no modelado nunca
  produce AST normativo; conserva propuesta/clarificación.
- `human_confirmation=HUMAN_CONFIRMED`, campos de autoridad extra, fuente
  vacía, rol variable inválido y campo desconocido son rechazados antes de
  compilar. Un valor booleano desconocido no se convierte en False.
- Ningún resultado del helper contiene `HUMAN_CONFIRMED`, READY o permiso de
  producción. El hash de la fuente identifica bytes; no autentica al humano.

## Plan

Escribir tests negativos y observar RED pertinente; añadir schema propuesto
versionado y helper de validación puro; observar GREEN y regresiones; revisar
mediante Gentle AI el candidato exacto, reconocer recibo y hacer respaldo
normal tras inspección de confidencialidad. Sin red de LLM ni credenciales.

## No cubierto

Parser de lenguaje natural, ratificación de intención, gate externo de
identidad, temporalidad, unidades, excepciones, CodeGen, EARS completo ni
conexión a despliegue. Son unidades futuras con decisiones pendientes.
