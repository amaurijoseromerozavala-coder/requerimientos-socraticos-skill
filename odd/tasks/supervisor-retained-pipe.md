# WU-SUP-CORE-003 — Hijo recolectado y captura incompleta

Solicitud: «Continua el desarrollo». Cerrar observación
review-7f20158690dc0591/R3-001, distinta del antiguo R3-001 de revocación.

## Alcance y criterio

Añadir prueba real Linux, sin modificar el núcleo si ya cumple el contrato.
Un hijo directo termina con código 0 mientras su descendiente mantiene stdout y
stderr abiertos. Exigir cleanup=CONFIRMED, capture_complete=false, código 0 y
retorno dentro del presupuesto con tolerancia de planificación explícita.

El fixture se ejecuta en proceso aislado con subreaper Linux para adoptar y
recolectar al descendiente. Se conserva su PID observado y evidencia waitpid;
solo se envían señales a un hijo propio confirmado por waitpid. Espera auxiliar
finita, sin consumo intensivo; el proceso de test no cambia su rol subreaper.

TDD: registrar falta de cobertura, probar candidato actual; si pasa, no inventar
RED funcional. Ejecutar control negativo sobre copia temporal que falsee
capture_complete=true y exigir rechazo por la aserción precisa. No alterar fuentes
reales para fabricar resultados. RDD antes de respaldo a GitHub.

## Log
Caso real pasa sin modificar núcleo. Control negativo de copia temporal falla con aserción específica. Fixture recolecta todos sus hijos. Suite completa 16 tests OK. No RED funcional inventado; RDD pendiente antes de respaldo.
