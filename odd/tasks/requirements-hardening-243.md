# Requerimientos socráticos 2.4.3 — presupuesto de memoria

Herramientas de la skill; entrega local sin CI ni producción. No commits de producto.
Runner: venv existente, unittest en subprocesos con timeout exterior y fixtures pequeños.

## Specs

S1. Usuario: «Haz las mejoras». Aplica al pendiente aceptado: presupuesto de memoria
de coordinación Git y consumidor, observación y respuesta explícita ante agotamiento.
Separar memoria virtual, RSS observado y capacidad física no demostrada. No prometer
MemoryError universal, ausencia de swap ni una cuota kernel agregada del host.

S2. Implementación propuesta por el coordinador: separar coordinación de datos en
un proceso dedicado; límites RLIMIT_AS antes de exec, respetando límites heredados.
Perfil técnico conservador inicial512MiB por validación: CLI64, coordinador256,
consumidor128, Git64; valores de política provisionales, no calibración i3/WSL.
Configurable total256..1024MiB múltiplo8. La API no reduce límites del proceso
externo que la llama: debe declarar ese alcance y aislar el trabajo de datos.

S3. Admisión cooperativa por cuenta para una validación activa, con archivo privado
y lock no bloqueante heredado a consumidores. Comprobar headroom visible con reserva
2x presupuesto; UNKNOWN o insuficiente bloquean. Es observación parcial y secuencial,
no reserva física ni salud demostrada del host/WSL. Sin cambios a cgroups ni privilegios.

S4. Mantener identidad de bytes2.4.2, límites de documentos, errores anteriores,
0600, CI diferido y BLOCKED_GLOBAL_ENFORCEMENT. Capturar RED/GREEN pertinente,
regresión, ensayos de pocos MiB como máximo, revisión independiente y RDD nativo.
No medir ni simular el hardware inaccesible. Emitir informes y exportación completa.

## Tasks

- T1 [S1,S2] inline: snapshot de2.4.2 y diseño de fronteras — DONE.
- T2 [S2,S3] delegado: política, límites, admisión y tests pequeños — DONE; 11 tests.
- T3 [S1,S2,S4] inline: coordinador dedicado, integración y diagnósticos — DONE; 10 tests.
- T4 [S2,S4] delegado: extensión opcional del supervisor y pruebas — DONE; 26 tests.
- T5 [S4] inline: regresión, revisión independiente, RDD y exportación — DONE; 195/62 pruebas,11diff,recibo exacto y exportación55fuentes.

## Log

L1. 2026-10-28: usuario «Haz las mejoras» tras contraste QA. El perfil numérico es
una decisión técnica inicial del implementador para contener trabajo, no un umbral
de rendimiento aprobado ni una afirmación de capacidad física. No se ejecutan cargas
de agotamiento. RLIMIT_AS actúa sobre espacio virtual; RSS requiere observación aparte.

2026-10-28: perfil inicial basado en política y observación mínima de importjsonschema
Vm42848kB/RSS15892kB; no se identifica como máximo ni se extrapola al PC. RED previo
y GREEN de helper11, supervisor26 y diagnósticos7 preservados. Revisión independiente
inicial59tests detectó normalización del rechazo de hard heredado, baseline CLI ya
superior al soft y transporte coordinador2MiB potencialmente insuficiente. Se
registró RED pertinente de3casos, se corrigió y10casosGREEN. Revisión posterior
62tests y repros reales pequeños confirmaron correcciones, sin pendientes en alcance.
No se generaron fixtures grandes de manifiestos; ese límite se contrastó estáticamente.

2026-10-28: regresión195tests OK6.921s,11diffidénticos,CLIreal localPASS conperfil512.
RDDnativo review-29a23cffb87a1be5,riesgoalto4lentes,approvedyacknowledged para
sha256:d42b9b6eb80a5ef2041bbaac3cfbeab4866699af74361a59cce568a85e1f6717.
92archivos coinciden byteabyte conárbol545a82b676d16a2979f0dfddf765222b14b9d2f5.
Informe externo RESULTADO.md redactado; empaquetado pendiente. No CI/producción,
ni capacidadfísica/RSSglobaldemostrados. Framework conservanormasyautoridadhumana.

2026-10-28: JSON completo2.4.3 y ZIP creados y leídos; hashes contenido y ZIP OK.

2026-10-28: contraste de nuevo QA que cita2.4.2: límites efectivos256KiB/2MiB/8MiB
refutan supuestos depreflight34MiB yarchivoGit30MiB. Fixture262145bytes sale2
INVALID_INPUT/FILE_SIZE_LIMIT. Sin cambios fuente; pendiente propuesto: extender
presupuesto al workerZ3. Reporte CONTRASTE-QA-V242.md y qa-latest-evidence.json.
