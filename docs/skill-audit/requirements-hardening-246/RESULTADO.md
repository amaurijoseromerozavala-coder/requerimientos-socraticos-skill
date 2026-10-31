# Resultado — requerimientos-socráticos 2.4.6

Se corrigió R2-001, observación de mantenimiento del cierre RDD2.4.5, con la
autorización explícita del humano. Estado: REVIEWED_WITHIN_LOCAL_SCOPE — APPROVED_AND_ACKNOWLEDGED.

## Cambio

La admisión consulta los roles definidos por memory_budget para cada perfil.
Se eliminó _role_fractions; ya no hay otra tabla de fracciones en el preflight.
Se comprueban hasta33 perfiles soportados mediante comparación entera de bytes.
El modo all toma el máximo de cada rol compartido entre los workloads.
No se modificó memory_budget ni se cambiaron las políticas actuales.

Con512MiB se conservan exactamente:
- Lógica: caller67108864bytes / solver469762048bytes (64/448MiB).
- Git: caller67108864 / coordinador268435456 / consumidor134217728 /
  Git67108864bytes (64/256/128/64MiB).

## Verificación

Tres tests RED contra2.4.5 con políticas sintéticas coherentes (lógica, Git y
caller compartido all); cuatro tests GREEN después del refactor. El cuarto
test conserva el oráculo de512MiB con valores de bytes literales.

Verificador independiente:
-238tests PASS, una ejecución secuencial8.692s, deadline55s.
-194outputs de políticas iguales para97presupuestos256..1024 paso8.
-59280comparaciones de decisiones públicas,0diferencias semánticas, con bordes
 ±1byte. Se excluyen timestamps y tiempos variables; no es stdouttotalidéntico.
-560diferencias de helper privado bajo el mínimo: ahora0 en vez de un perfil
 inviable. No cambiaron los rechazos públicos dentro de la matriz probada.
-RED reproducido contra helpers del árbol aprobado2.4.5.
-Fuentes estables; snapshot y harness propios eliminados por el verificador.

Consultar independent-review.json y independent-tests.log. La matriz finita
no prueba equivalencia para cualquier estado de hardware o software futuro.
Wrapper real activate completado, perfil512; no calibración física.

## Alcance que permanece

0600, CI diferido y BLOCKED_GLOBAL_ENFORCEMENT se conservan. PCi3/WSL no observado.
No se fuerza Z3 hacia448MiB ni se satura RAM/swap. Variar a UNKNOWN por presupuesto
agotado no demuestra una contradicciónSAT/UNSAT. El tiempo de un barrido2MiB en
el i3 sigue sin medirse; esta corrección no lo certifica.

RDD nativo del candidato2.4.6 completado: cuatro lentes aprobadas sin hallazgos.
Acknowledgement exacto admitido, authority=burned; no se reutilizó el recibo2.4.5.
validation.json permanece FROZEN_PRE_REVIEW, con pruebas y hashes actuales.

Risk: items2 y3 — guardas de viabilidad y contratos compartidos; verificación
independiente completada, sin autoridad de producción.


Candidato preparado: sha256:191b26c8700c0c01c19c10ae9f78fa353d5c456ed637c3a75ffd87d044486869.
99archivos coincidenconárbol 27c1bbe85cc05e973c4f934643fd7510d41d606d. El humano
autorizó granted y la revisión terminó aprobada. Consultar CIERRE-RDD.md y
rdd-final.json. La revisión nativa fue de fuentes y no repitió los tests.

Lineage: review-9a99725b8fbf1c6a. El estado FROZEN_PRE_REVIEW es histórico;
el cierre final queda fuera del candidato congelado. Ninguna fuente se modificó
para insertar una aprobación posterior.
