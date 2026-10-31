# Revisión independiente documental

Revisor: `/root/integration_interrogator`. Alcance: cinco JSON de
`docs/requirements/integracion-requisitos-qa-supervisor/candidato-v0.1/`, contrastados
con INT-D01–23, diseño integrado e intercambio real Q-INT-T01. Revisión estática
del directorio mutable; no es revisión sellada, recibo RDD ni prueba de ejecución.

Resultado: **CHANGES_REQUESTED**. La etiqueta PARTIAL_NOT_GLOBAL_FSM y el alcance
del gate se respetan; los hallazgos afectan a la correspondencia interna de esta
proyección. No requieren nuevas decisiones humanas para corregir el borrador.

1. **HIGH — Revocación fuera de READY/INCORPORATING.** `fsm.json:98` establece
   rechazo conservando estado por defecto. `revocation_accepted` no tiene handler
   en ISOLATED, VERIFYING, REBASE_REQUIRED o WAIT_AUTHORIZATION. La nota ortogonal
   (`:104`) conserva un latch pero no especifica quién lo establece en esos casos.
   Definir recepción global prioritaria que registre revocación y actualice su
   estado ortogonal antes de resolver la transición local. Falsador: revocar
   durante VERIFYING y alcanzar admisión usando autoridad anterior.

2. **HIGH — Nueva autorización y prohibición permanente incompatibles.**
   `contracts.json:112` prohíbe nuevas escrituras después de aceptación sin
   expresar cómo una autorización nueva restablece incorporación; el gate sí
   permite revoked=true con fresh_incorporation_authorized=true. Vincular
   prohibición y autorización a identidad/época de autoridad, tarea y alcance
   aplicable; fresh debe quedar inválido ante una revocación posterior. No es
   necesario aumentar las siete variables: definir cómo se derivan sus valores
   de recibos y del último evento aceptado. Falsador: reutilizar fresh=true de
   una autorización anterior a una segunda revocación.

3. **MEDIUM — Ambigüedad de task_authorized.** `incorporation-gate.json:18` y
   `contracts.json:99` podrían exigir que la autorización original siga activa
   además de la nueva autorización de incorporación. Eso impediría ejercer la
   salida prevista por INT-D22 después de revocar la original. Definir
   procedencia de tarea y autoridad operativa suficiente, incluyendo la nueva
   autorización aplicable, sin exigir reautorizar operaciones no necesarias.
   Falsador: nueva autorización válida de incorporación, criterios vigentes y
   recursos admitidos, pero bloqueo perpetuo por revocación histórica.

Q-INT-T01 está conservado adecuadamente como propuesta: orden local, acuse
durable, operaciones emitidas pendientes y crash UNKNOWN. La recuperación deberá
mantener la prohibición de emitir restauraciones mientras haya escrituras
inciertas, no solo comprobar esa condición al declarar restauración terminada.

No se demuestra implementación, cobertura global, durabilidad ni exclusión real
de escritores. READY permanece bloqueado. No se editaron fuentes del candidato.

## Seguimiento de correcciones

Relectura independiente limitada a los cambios en `fsm.json`, `contracts.json`
y `incorporation-gate.json`; se conservan arriba los hallazgos originales.

- **F1 RESOLVED_DOCUMENTARY:** `global_handlers` aplica revocation_accepted en los
  nueve estados antes de transición local, establece latch y época, e indica que
  el evento global no se rechaza por carecer de transición local.
- **F2 RESOLVED_CORE_WITH_RESIDUAL:** `revocation_order.after_acceptance` y
  `authorization_epoch` vinculan bloqueo a la autoridad revocada y permiten nueva
  autorización suficiente; otra revocación invalida autorizaciones anteriores.
  La definición del gate deriva frescura de aprobación identificada y vigente.
  Permanece por ajustar C01 en `negative_scenarios`: su condición todavía dice
  cualquier escritura posterior a revocación y exige DENY_WRITE, sin distinguir
  incorporación con autoridad revocada, autorización posterior válida ni
  recuperación. Precisar ese escenario para que no contradiga la regla corregida.
- **F3 RESOLVED_DOCUMENTARY:** `task_authority.scope` y la definición explícita de
  `task_authorized` admiten una autorización nueva suficiente sin exigir que siga
  activa la autorización original revocada.

Estado de seguimiento: **CHANGES_REQUESTED_LIMITED_TO_C01**. Los resultados
reportados por el coordinador sobre 128 valuaciones y grafo no se ejecutaron ni
se validaron en esta revisión; no se presentan como prueba independiente.
Los límites de propuesta, proyección parcial y ausencia de READY permanecen.

## Cierre del seguimiento C01

Verificación limitada a `contracts.json:126`: C01 ahora rechaza una escritura de
incorporación basada en época revocada sin autorización posterior suficiente y
aplicable, excluyendo escrituras de recuperación autorizadas separadamente.
`expected` permanece DENY_WRITE. Es conforme a la corrección F2 y a INT-D22/23.

**F2 RESOLVED_DOCUMENTARY**, incluido su residual C01. Estado final de esta
revisión: **NO_OPEN_FINDINGS_IN_REVIEWED_SCOPE**. Los tres hallazgos originales
quedan resueltos documentalmente; sus registros históricos se conservan.
Este cierre no convierte el candidato en READY ni acredita ejecución, revisión
sellada, cobertura global o mecanismos implementados.
