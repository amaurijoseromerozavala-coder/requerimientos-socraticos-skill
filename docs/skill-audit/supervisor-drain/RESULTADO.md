# WU-SUP-CORE-002 — R4-1

Estado: IMPLEMENTED_TESTS_PASS_RDD_PENDING. No publicación antes del RDD.

## RED y GREEN

Tres pruebas reales fallaron antes de corregir: diagnósticos ausentes y dos
cierres con -9 cuando se esperaba exit 0. Se conservan red.stderr y red.stdout.
La corrección drena ambos canales durante espera de terminación/recolección,
retiene hasta los límites y descarta exceso. Los plazos no se reinician al recibir
bytes; el motivo original de parada permanece separado del truncado.

Suite final: 14 pruebas OK, incluidas las diez previas y cuatro de cierre. Los
casos nuevos verifican mensajes en ambos canales, volumen mayor que la tubería,
exceso sobre retención y escritor activo que no extiende la gracia. La medición
es local cloud y no calibra hardware objetivo. Logs final-green.stdout/stderr.
observations.json conserva estados, cuenta y hashes de bytes en lugar de expandir
salidas repetitivas; no sustituye el log crudo ni autentica su procedencia.

## Contrato aditivo

capture_complete indica EOF observado en ambos canales, NO ausencia de truncado.
capture_truncated indica exceso observado por canal. Un resultado solo puede
considerarse íntegramente capturado si complete=true y ambos truncated=false.
Si se recolectó el hijo pero faltó EOF al vencer el plazo, puede informarse
cleanup=CONFIRMED y capture_complete=false: recolección y completitud son distintas.
No afirma contención de descendientes ni captura después del presupuesto.

No cambia las políticas de autoridad/QA. Persistencia, recuperación entre reinicios
y adaptación al checker siguen pendientes. La aprobación anterior de R4-1 se
conserva como historia; esta corrección requiere su propio recibo.
