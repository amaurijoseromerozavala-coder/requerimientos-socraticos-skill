# Requerimientos Socráticos, QA Inquisidor y Supervisor Local

Proyecto integrado de requisitos trazables, revisión de calidad y diseño de un supervisor local. Incluye fuentes, pruebas, esquemas, decisiones humanas, contratos, modelos y evidencias documentales.

## Estado real

| Componente | Estado |
|---|---|
| Requerimientos Socráticos | Skill 2.4.6 y tooling existente |
| QA Inquisidor | Skill 0.1.3-alpha y comprobador documental |
| Supervisor local ampliado | Diseño DRAFT; no implementado |
| Integración | 23 decisiones, modelo booleano de 128 valoraciones y FSM parcial |
| RDD del candidato integrado | Candidato anterior aprobado; corrección documental R3-001 probada, nuevo RDD pendiente |
| Calibración del hardware objetivo | No realizada |

La revisión RDD inspeccionó 13 archivos; no certifica todo el repositorio ni ejecutó pruebas físicas. El diseño conserva brechas técnicas que bloquean READY. CI y producción permanecen diferidos.

## Por dónde comenzar

- [JSON completo para revisión independiente](exports/proyecto-requerimientos-qa-supervisor-completo.json): 893 archivos incluidos como contenido, índice de lectura y hashes. Es una instantánea anterior a esta preparación de publicación; los nuevos archivos de portada y licencia se entregan en el repositorio.
- [Corrección documental R3-001](docs/skill-audit/integration-r3-001/RESULTADO.md).
- [Informe RDD del candidato anterior](docs/skill-audit/integration-candidate-01/RESULTADO.md).
- [Diseño integrado](docs/requirements/integracion-requisitos-qa-supervisor/candidato-v0.1/README.md).
- [Decisiones confirmadas](docs/requirements/integracion-requisitos-qa-supervisor/decisiones-confirmadas.json).
- [Catálogo y matriz de integración](docs/requirements/integracion-requisitos-qa-supervisor/matriz-integracion.json).
- [Brechas pendientes](docs/requirements/integracion-requisitos-qa-supervisor/candidato-v0.1/open-gaps.json).
- [Skill Requerimientos Socráticos](skills/requerimientos-socraticos/SKILL.md).
- [Skill QA Inquisidor](skills/qa-inquisidor/SKILL.md).
- [PRD del supervisor anterior](docs/requirements/qa-supervisor/prd.json), conservado como línea base histórica.

## Preparación y portabilidad

Las fuentes Python y sus pruebas están en `skills/`. `requirements.txt` conserva las dependencias de la distribución anterior. La [guía de esa distribución](docs/publication/previous-skill-release/README.md) se conserva como documento histórico; sus afirmaciones sobre contenido distribuido corresponden a aquella versión.

`bin/gentle-ai` es el wrapper local original, con rutas absolutas de `/workspace/replica-gentle-ai`; no es un instalador portable. El binario upstream y las credenciales no están incluidos. Las invocaciones del revisor tampoco deben asumirse operativas al clonar. Para usar los helpers, preparar explícitamente un entorno Python compatible y ejecutar sus rutas con el intérprete elegido. No se ejecutan instalaciones, calibraciones ni servicios automáticamente.

Los documentos históricos pueden incluir rutas locales y estados anteriores: consultar los recibos de cada candidato y el informe actual antes de interpretar un PASS. `VERIFICATION.json` en la raíz corresponde a la publicación anterior de Requerimientos Socráticos, no al sistema integrado.

## Alcance de esta publicación

Se publican código propio, tests, documentos, evidencias, configuración de réplica y exportación. Se excluyen credenciales, estados privados de herramientas, respaldos del entorno, cachés, descargas y ejecutables externos. No se incorporan workflows de GitHub Actions.

[Licencia del proyecto](LICENSE) y [avisos de terceros](THIRD_PARTY_NOTICES.md).
