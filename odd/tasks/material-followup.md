# Contraste posterior de QA — bloqueo material y CI diferido

## Specs

- Mantener BLOCKED_GLOBAL_ENFORCEMENT y no avanzar QA/producción.
- Contrastar hipótesis sobre inotify, CI falso y concurrencia sin fabricar
  resultados de hardware físico inaccesible.
- Instrucción humana más reciente: «no quiero CI todavia». No preparar ni
  configurar CI, no modificar GitHub ni elegir un remoto en su nombre.

## Tasks

- [x] Inspección de código, skill y herramientas primero; GitHub consulta en
  lectura únicamente, sin cambios. Workspace sin remoto.
- [x] Ensayos acotados: variables CI falsas + consumidor exit0, orden watches/
  lecturas y mutación/restauración con fork C, veinte validadores cloud.
- [x] Conservar resultados y límites en docs/skill-audit/material-followup.
- [ ] Test de thrashing en i3/WSL2 real: pendiente de acceso operativo al equipo.
- CI externo: DIFERIDO_POR_USUARIO; no ejecutable hasta nueva instrucción.

## Log

- Fake CI/consumer no avanzó; orden watches antes de contenido comprobado en
  tres directorios; fork real MODIFY/restauración rechazado. Veinte validadores
  sin presión completaron: no se usan como aceptación material.
- Skill instalada 2.1.1 y candidato revisado no se modificaron. QA sin cambios
  actuales; no afirmar historia continua. No nueva entrevista skill→asistente;
  la única pregunta fue operativa al humano y respondió no CI todavía.
