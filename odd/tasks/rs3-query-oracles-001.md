# RS3-WU-QUERY-ORACLES-001

## Entrada y alcance

Solicitud del maintainer: comenzar la implementación del paquete RS3 con
Gentle AI y ODD → TDD → RDD estrictos. ZIP exacto SHA-256:
`83a83c77921f7737e89328b8dae365e7d0e7047f0c3fc7acbf7af2fd8f6c2d7e`.
Sus 107 requisitos siguen marcados PROPOSED en el propio paquete; esta unidad
no los ratifica ni crea `HUMAN_CONFIRMED` o `production_ready`.

## Specs y falsadores

- RS3-AT-001/002: para `A⇒B`, dominio verdadero y salida `P`, la consulta
  normativa `D∧¬∃P:C` es SAT con `A=true,B=false`; la consulta mutante
  `D∧C∧¬∃P:C` es UNSAT. El testigo se comprueba con evaluación booleana
  independiente, sin confiar únicamente en la cadena `SAT`.
- RS3-AT-005: falta de activación de guardas da `gap=SAT`, pero si hay salida
  compatible `no_output=UNSAT`.
- RS3-AT-007/008: un conflicto global produce `no_output=SAT` y consistencia
  existencial UNSAT; un conflicto regional puede coexistir con consistencia
  existencial SAT. Nunca inferir consistencia universal de esta última.
- RS3-AT-013: una variable de salida en guarda es entrada inválida antes de
  realizar consultas; no clasificarla como agotamiento de recursos.
- Un oráculo finito independiente enumera sólo modelos sintéticos pequeños.
  No amplía el contrato del solver ni certifica significado humano o producto.

## Tareas y evidencia

1. Agregar tests RED que requieran el oráculo independiente y comparen la
   salida real del analizador con las expectativas anteriores.
2. Registrar el fallo pertinente antes de crear el oráculo; implementar
   solamente el helper de pruebas y observar GREEN.
3. Ejecutar las regresiones de requisitos y los controles CI pertinentes.
4. Obtener RDD nativo aprobado y reconocido para el candidato exacto antes
   de commit/push; inspeccionar el contenido destinado a publicación.

## Exclusiones

No implementar todavía CandidateIR, UI, DSPy, autenticación, CodeGen ni
semántica de `production_ready`; dependen de decisiones humanas o unidades
posteriores. Sin ensayos de carga ni uso de datos privados en red.
