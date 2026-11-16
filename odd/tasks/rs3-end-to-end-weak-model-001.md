# RS3-END-TO-END-WEAK-MODEL-001

## Objetivo y precedencias

Comprobar un primer flujo vertical con datos exclusivamente sintéticos sobre
componentes ya existentes: respuesta de proveedor débil → admisión
`CandidateIR` → EARS provisional → propiedad booleana construida desde el AST
validado → Z3 y testigo → pregunta por hueco de guardas → nueva propuesta.
Depende de las unidades de IR, oráculo semántico, gate de modelo débil, análisis
supervisado y pregunta de gap ya publicadas. Los requisitos del paquete RS3
siguen propuestos; este ensayo no cambia su aceptación individual.

## Alcance permitido

Un módulo de sondeo sintético y pruebas de integración. El modelo de dominio,
reglas y glosario es una entrada independiente, explícita y de prueba; solo la
propiedad se inserta desde el AST comprobado. No se inventa una guarda ni se
presenta un contraejemplo de propiedad como un hueco de guardas. No hay LLM
externo, cuenta humana, confirmación, código real, UI confiable ni despliegue.

## Oráculos RED congelados

1. El caso positivo vincula bytes fuente y propuesta; IR, EARS y propiedad
   formal comparten el mismo AST y digest de propuesta. Z3 entrega un
   contraejemplo de la propiedad revalidado por un evaluador booleano; el gap
   de guardas se identifica por separado, con un testigo revalidado.
2. La pregunta de retorno conserva identidad de modelo, glosario y testigo,
   permanece `PROPOSED_FOR_INTERROGATION`, y una respuesta sintética posterior
   produce otra propuesta sin confirmar al humano ni consumir códigos.
3. JSON malformado, fuente distinta, dirección invertida, propiedades
   preinyectadas, glosario inválido, salida incompleta y respuesta sin vínculo
   con la pregunta bloquean sin emitir una decisión ni un PASS.
4. Ningún resultado afirma que el modelo formal se derivó por completo del
   requisito humano. `NO_OUTPUT` y `GAP` conservan significados diferentes.
5. Todo resultado conserva `authority_verification=NOT_ESTABLISHED` y
   `execution_authorized=false`.

## Método y límites

ODD → RED semántico → implementación mínima → GREEN → regresión afectada →
RDD Gentle AI del candidato exacto → respaldo Git. El ensayo usa un intérprete
con dependencias fijadas y plazos acotados. Una corrida en CI Linux no prueba
precisión de modelos gratuitos reales, intención humana ni hardware Windows.
