# RS3-WU-PROPOSAL-IR-UNICODE-001

## Origen

Observación informativa `R3-unicode-validation` del RDD nativo
`review-6b2b1cc6b2d87590` sobre el candidato de IR provisional. Esta unidad
separa la corrección del candidato ya aprobado.

## Especificación y RED

Una cadena con sustituto Unicode aislado puede llegar desde JSON escapado y
fallar al codificar UTF-8. El comprobador de propuestas debe rechazarla con
`CandidateError`, sin traceback de `UnicodeEncodeError` ni AST. Controlar
`source_text`, `source_ref`, contexto y cualquier otra cadena serializable que
se conserve o se use para producir salida.

## Tareas

1. Agregar controles negativos de sustitutos aislados y observar RED.
2. Corregir solo la validación de límites/UTF-8; observar GREEN.
3. Ejecutar regresiones pertinentes y RDD nuevo para los archivos exactos.
4. Respaldar en GitHub solo tras recibo reconocido y verificación de contenido.

No cambia dirección lógica, autoridad ni estados de producto.
