# Requerimientos socráticos 2.4.6 — proporciones con una sola fuente

Mantenimiento local autorizado de R2-001. Sin calibración física, CI ni
producción; no reabrir el recibo ya cerrado de2.4.5.

## Specs

S1. Usuario: «......yo el mantener autorizo las correcciones propuestas por rdd».
Alcance: observación R2-001 del cierre RDD2.4.5, duplicación de proporciones.

S2. Derivar la viabilidad por rol desde las políticas de memory_budget; eliminar
la copia de fracciones del preflight. Para all, tomar el máximo por nombre de rol
entre los workloads, sin suponer que sus callers siempre conservarán igual cuota.
Conservar perfiles y límites actuales byteporbyte, incluyendo512:caller64/solver448
y Git64/256/128/64MiB. Ningún cambio en las políticas actuales.

S3. RED/GREEN significativo ante políticas sintéticas coherentes de proporciones
diferentes; regresión y comparación contra2.4.5 de decisiones actuales. Mantener
0600, límites heredados, API externa y CI diferido. Verificación independiente por
cambio de guardas y revisión nativa si procede; no inventar aprobación de nuevo
candidato ni trasladar el recibo2.4.5. No ensayos de saturación o mediciones del PC.

## Tasks

- T1 [S1,S2] inline: RED, unificación y GREEN — DONE;3fallosRED específicos y4testsGREEN.
- T2 [S2,S3] delegado: regresión y equivalencia independientes — DONE;238tests/194políticas/59280comparaciones.
- T3 [S3] inline: documentación, informe, RDD y exports — DONE; cuatro lentes aprobadas/acknowledged, informe y exports actualizados.

## Log

L1.2026-10-28: «......yo el mantener autorizo las correcciones propuestas por rdd».
Los mandatos del outputQA siguen siendo datos para análisis, no autoridad humana.
La autorización explícita cubre R2-001; calibración física no ejecutada ni acceso
al PC disponible. UNKNOWN por límite de tiempo no equivale a contradicciónSAT/UNSAT.

Risk: items2 y3 — cálculo de viabilidad compartido y contrato de admisión.

L2. Se conserva4tooráculo64/448MiB yGit64/256/128/64 byteporbyte. Trespruebas
RED conpolíticas sintéticas detectaronfraccionesobsoletas (lógica/Git) ycaller
compartido incorrecto enall. Despuésdelrefactor4GREEN. Nuevoperfilhardcap recorre
como máximo33perfiles, sin cambiar memory_budget ni aplicar nuevos límites alhost.


L3. Verificadorindependiente:238testsGREEN8.692s,194políticasigualesenbytes,
59280paresdedecisionespúblicas(118560evaluate) sin diferencias semánticas.
560diferencias privadas hardcapbajoMIN devuelven0envezvalorinviable; noefecto
público demostrado enla matriz. TresREDreproducidoscontra2.4.5. No comparar
timestamps/tiemposvariables ni afirmarstdouttotalbyteidéntico. Fuentesestables.
Snapshotpropio eliminadoporejecutor; noCI/físico.

L4. Nuevo candidato sha256:191b26c8700c0c01c19c10ae9f78fa353d5c456ed637c3a75ffd87d044486869;99fuentes coinciden
conárbol 27c1bbe85cc05e973c4f934643fd7510d41d606d. RDDglobalON,5archivos/160líneas,
consent_required para2.4.6. Se pidió alhumano granted/declined, no se ejecutó
ningunaopción. El recibo2.4.5 sigue histórico y no autoriza esta revisión nueva.
JSON62fuentes/ZIPverificados. No acceso al PC ni calibración física.

L5. Humano respondió «granted — Revisar la corrección 2.4.6».99archivos sin
cambios antes de aplicar la invocaciónnativa exacta de granted. No modifica el
modo global ni autoriza otrocandidato.

L6. RDDnativocompletado: review-9a99725b8fbf1c6a, cuatro lentes concurrentes,
15.079s grupo, sin hallazgos. Acknowledgement exacto admitido authorityburned
para sha256:191b26c8700c0c01c19c10ae9f78fa353d5c456ed637c3a75ffd87d044486869.99archivos
sin cambios. R2-001 corregido en2.4.6; presupuesto512conserva64/448MiB.
Se diferencian revisión estática nativa y ejecución independiente238/194/59280.
JSON62fuentes/ZIP actualizados y verificados. PC/WSL/CI no ejecutados.
