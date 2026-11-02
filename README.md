# Requerimientos Socráticos, QA Inquisidor y Supervisor Local

Proyecto integrado de requisitos trazables, revisión de calidad y diseño de un supervisor local. Incluye fuentes, pruebas, esquemas, decisiones humanas, contratos, modelos y evidencias documentales.

## Estado real

| Componente | Estado |
|---|---|
| Requerimientos Socráticos | Skill 2.4.8: activación portable, alcance de disco y clon verificado |
| QA Inquisidor | Skill 0.1.3-alpha y comprobador documental |
| núcleo | Biblioteca local de procesos implementada; enlace optativo al journal para el lanzamiento, sin integración QA ni contención universal de descendientes |
| adaptador QA | API interna implementada; invoca el comprobador, clasifica salida y bloquea la instancia ante limpieza incierta |
| reserva persistente | Registro cooperativo con RESERVED→ACTIVE→STOPPING→CONFIRMED_TERMINATED; requiere reconciliación antes de reutilizarlo |
| supervisor ampliado | Diseño DRAFT; no implementado como sistema completo: faltan integración QA del enlace optativo, reconciliación, recuperación, admisión global e incorporación |
| Integración | 23 decisiones, modelo booleano de 128 valoraciones y FSM parcial |
| RDD del diseño integrado | R3-001 documental aprobado y reconocido; los componentes ejecutables tienen recibos propios |
| CI | GitHub Actions activado: suites acotadas y verificación de coherencia del cierre RDD; protección de rama aún no configurada |
| Hardware objetivo | Una corrida acotada USER_REPORTED en i3/WSL: 62 pruebas OK sobre `6ca7fe4`; calibración bajo carga y producción pendientes |

El RDD del diseño integrado inspeccionó 13 archivos; los RDD posteriores de cada unidad revisaron sus propios candidatos. Ninguno certifica todo el repositorio ni la ejecución física en el i3/WSL. El [ensayo acotado reportado por el propietario](docs/skill-audit/target-hardware-smoke/observation.json) registra una corrida de la suite, sin logs crudos ni reproducción independiente; no prueba comportamiento bajo saturación. Las brechas de integración bloquean READY. CI activado por solicitud del propietario; producción permanece diferida. El workflow no es todavía un control obligatorio de rama.

## Por dónde comenzar

- [JSON completo para revisión independiente](exports/proyecto-requerimientos-qa-supervisor-completo.json): 893 archivos incluidos como contenido, índice de lectura y hashes. Es una instantánea anterior a esta preparación de publicación; los nuevos archivos de portada y licencia se entregan en el repositorio.
- [Corrección documental R3-001](docs/skill-audit/integration-r3-001/RESULTADO.md).
- [Informe RDD del candidato anterior](docs/skill-audit/integration-candidate-01/RESULTADO.md).
- [Cierre posterior del RDD de WU-SUP-PRE-REAP-007](docs/skill-audit/supervisor-pre-reap/RDD-CIERRE.md): el `RDD: pendiente` del expediente previo describe el estado anterior a la revisión.
- [Diseño integrado](docs/requirements/integracion-requisitos-qa-supervisor/candidato-v0.1/README.md).
- [Decisiones confirmadas](docs/requirements/integracion-requisitos-qa-supervisor/decisiones-confirmadas.json).
- [Catálogo y matriz de integración](docs/requirements/integracion-requisitos-qa-supervisor/matriz-integracion.json).
- [Brechas pendientes](docs/requirements/integracion-requisitos-qa-supervisor/candidato-v0.1/open-gaps.json).
- [Skill Requerimientos Socráticos](skills/requerimientos-socraticos/SKILL.md).
- [Skill QA Inquisidor](skills/qa-inquisidor/SKILL.md).
- [PRD del supervisor anterior](docs/requirements/qa-supervisor/prd.json), conservado como línea base histórica.

## Preparación y portabilidad

Las fuentes Python y sus pruebas están en `skills/`. `requirements.txt` conserva las dependencias de la distribución anterior. La [guía de esa distribución](docs/publication/previous-skill-release/README.md) se conserva como documento histórico; sus afirmaciones sobre contenido distribuido corresponden a aquella versión.

La skill incluye una entrada portable independiente del Gentle AI instalado:

```bash
REQUIREMENTS_PYTHON="$PWD/.venv/bin/python" \
  bash skills/requerimientos-socraticos/scripts/requirements activate --path "$PWD"
```

Este ejemplo supone un entorno `.venv` preparado. La [guía para Gentle Pi/Shell](skills/requerimientos-socraticos/references/gentle-pi.md) explica preparación,
activación desde otro proyecto y diagnóstico sin comandos ficticios.
`bin/gentle-ai requirements ...` es un wrapper opcional que resuelve rutas locales.
Para otros comandos requiere el ejecutable upstream local o `GENTLE_AI_UPSTREAM`
como ruta absoluta; no incluye binarios ni modifica perfiles de autenticación.
No se instala ni se ejecuta nada automáticamente al clonar.

Los documentos históricos pueden incluir rutas locales y estados anteriores: consultar los recibos de cada candidato y el informe actual antes de interpretar un PASS. `VERIFICATION.json` en la raíz corresponde a la publicación anterior de Requerimientos Socráticos, no al sistema integrado.

## Alcance de esta publicación

Se publican código propio, tests, documentos, evidencias, configuración de réplica, exportación y un workflow de GitHub Actions con permisos de solo lectura. Se excluyen credenciales, estados privados de herramientas, respaldos del entorno, cachés, descargas y ejecutables externos. La protección obligatoria de la rama sigue pendiente.

[Licencia del proyecto](LICENSE) y [avisos de terceros](THIRD_PARTY_NOTICES.md).

## Núcleo de procesos WU-SUP-CORE-001

Primera biblioteca ejecutable en `supervisor/process_core.py`, separada de la
evaluación QA. Controla un hijo directo Linux, captura acotada, límites virtuales,
plazos y recolección. Conserva sin recolectar la identidad del hijo mientras
observa su grupo; si quedan miembros activos,
solicita terminación al grupo propio antes de recolectar
al hijo y escala dentro de plazos acotados. Si hubo limpieza del grupo tras la
salida del hijo, marca la tarea como detenida y no admite su resultado como una
salida normal. Una observación o limpieza incierta bloquea la instancia.
Esto no contiene procesos que abandonen ese grupo.
Una limpieza incierta bloquea esa instancia. No implementa
todavía coordinación entre instancias, cuotas globales, incorporación ni
recuperación tras reiniciar. `supervisor/qa_adapter.py` aporta la invocación QA
como API interna. El núcleo admite un enlace optativo al journal: persiste
RESERVED antes de lanzar, ACTIVE con PID/starttime después, STOPPING antes de
solicitar término y CONFIRMED_TERMINATED tras recolectar al hijo y observar
que su grupo no conserva miembros activos. Una falla conserva el estado previo
y bloquea nuevas ejecuciones. El estado terminal sigue sin reconciliación
automática ni integración QA. El
supervisor integrado sigue DRAFT; no es sandbox ni garantía de tiempo real.

Pruebas locales acotadas: `python3 -B -m unittest discover -s supervisor/tests -v`.
La suite combina procesos reales con una inyección explícita de fallo de espera;
esta última no reproduce un estado D del kernel. La corrida USER_REPORTED de
62 pruebas en el i3/WSL no constituye calibración bajo carga ni autoriza producción.

[Cierre RDD de R3-001](docs/skill-audit/integration-r3-001/CIERRE-RDD.md).
