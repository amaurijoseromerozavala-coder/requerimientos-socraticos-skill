# WU-SEC-EVIDENCE-GATE-001 — admisión de nueva evidencia pública

## Specs

Solicitud humana: continuar la corrección local de exposición de datos
sensibles con ODD → TDD → RDD estricto y sin push ni reescritura histórica.

El árbol público contiene evidencia histórica pendiente de remediación. La
compuerta nueva debe evaluar los blobs de evidencia que cambia un candidato,
no convertir la ausencia de cambios en una declaración de seguridad del
historial. La selección usa un commit base explícito y el HEAD exacto; un base
inválido, objeto ausente, symlink, archivo excesivo o estructura ambigua bloquea.
El resultado solo comunica conteos, nunca valores ni contenido. El alcance es
`docs/skill-audit/` y `exports/`. El workflow proporciona el base de push o PR;
el primer push usa árbol vacío. La compuerta no autoriza publicación ni cierra
alertas existentes.

## Oráculos y tareas

1. RED: commit sintético con nuevo archivo de evidencia y valor ficticio;
   el workflow actual carece de verificación y la entrada de comprobación no
   existe. Control negativo de base inválido y symlink.
2. Implementar selección de blobs Git por diferencia base→HEAD y evaluación
   con el detector existente, sin imprimir valores. Integrar en CI.
3. GREEN: controles positivos/negativos; suite completa y `git diff --check`.
4. RDD nativo del candidato exacto, reconocimiento y commit solo local.

## Límites

No se consulta ni modifica el historial remoto; los valores históricos siguen
pendientes. No hay push, cierre de alertas ni automatización de remediación.
