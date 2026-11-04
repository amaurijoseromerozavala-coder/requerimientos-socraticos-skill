# WU-RS3-D03-CONFIRMATION-POLICY-013

## Autoridad de la decisión y alcance

El maintainer eligió en esta conversación la opción **A — Cada confirmación**
para D03. Registrar exactamente esa política en el contrato RS3. Una propuesta,
pregunta o interpretación pendiente no es confirmación. Toda transición que
acepte semántica o autorice una operación requiere una comprobación PBKDF2
nueva vinculada al contenido y snapshot exactos; la segunda transición es un
gate separado. Una categoría desconocida cierra por defecto.

Esta unidad registra la **decisión de diseño**, no habilita autoridad. No crea
cuenta, credencial real, servicio ni recibo; D05 y el canal humano siguen sin
verificar. `human_confirmation_enabled=false` y
`real_authority_gate=SECURITY_BOUNDARY_UNMET` continúan.

## Oráculos RED congelados

1. La decisión D03 está presente, selecciona `EVERY_CONFIRMATION`, y ya no
   figura entre decisiones humanas pendientes.
2. Confirmación semántica, confirmación de excepción y autorización de una
   operación concreta requieren comprobación nueva vinculada al contenido.
3. Propuestas y aclaraciones pendientes no se convierten en confirmaciones.
4. Una categoría no mapeada bloquea; no hereda el permiso de otra categoría.
5. El documento conserva la separación entre decisión D03 y frontera D05, sin
   afirmar que la contraseña o el RDD autentiquen ya al humano.

RED documental → contrato mínimo → GREEN y regresión → RDD exacto → Git.

## Evidencia RED/GREEN local

- RED inicial: 3 tests del contrato terminaron exit 1 por ausencia de `d03` y texto ADR pendiente.
- RED de consistencia pública: el test de README terminó exit 1 porque aún decía `resolver D03`.
- GREEN: 4 controles documentales terminaron OK.
- Regresión: `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh` terminó exit 0: 55 CI, 122 supervisor, 62 QA y 342 requisitos.
