# WU-SUP-INT-002 — Oráculo de observación parcial

Resolver review-b830a36d94741974/R3-001. Solo pruebas, no código de producción.
Exigir admisión de protocolo antes de afirmar escalada. RED sobre fixture previo
incoherente; corregir status a NOT_ASSESSED con PARTIAL. Cubrir exit0/evento de
éxito y exit2/rechazo documental. Conservar caso incoherente como rechazo explícito.
Control negativo: copia temporal elimina las condiciones de observación de la
escalada; el caso exit0 debe fallar precisamente por pérdida de revisión humana.
No atribuir RED del test a defecto de producción. Regresión adaptador y RDD exacto
antes de commit/push. No cambios de permisos, runtime, hardware o CI.

## Log
RED del fixture antiguo confirmado. GREEN13tests. Control negativo detectado con
una sola aserción pertinente. Código de producción sin cambios; RDD pendiente.
