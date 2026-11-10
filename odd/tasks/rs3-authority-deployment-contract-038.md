# WU-RS3-AUTHORITY-DEPLOYMENT-CONTRACT-038

## Objetivo y origen

Tras una ejecución sintética local de WU-037, definir en la skill un contrato
portable de preparación y evaluación del despliegue D05. El humano eligió
Linux/WSL con cuenta de guardián separada como primer destino. La decisión no
autoriza crear cuentas, credenciales reales, UI, servicios o claves de firma.
El humano precisó después que la skill debe reconstruir el mismo **runtime
lógico** independientemente del hardware. La identidad física y las barreras
del SO se sondean en cada host; no se copian con Python ni con una imagen.

## Evidencia material actual

HEAD inicial: `83707f7f78046140aeb0384ab24063d429e4472b`, árbol limpio.
En este cloud env el proceso agente tiene UID 1000. Se ejecutó en un directorio
temporal privado un flujo con códigos exclusivamente sintéticos: reserva
PENDING, mutación de nonce rechazada, coincidencia que produce SPENT, replay
rechazado y `execution_authorized=false`. El mismo UID pudo leer el archivo
de verificadores y escribir en el almacén 0700/0600. El sondeo D05 existente
con UID 1000 para ambas partes devolvió `local_status=FAIL` y
`SECURITY_BOUNDARY_UNMET`. No existe UI ni Git privado del guardián en esta
ejecución. No se imprimieron códigos ni se conservaron credenciales.

## Alcance y límites

Añadir una referencia de despliegue y un contrato JSON a la skill. Distinguir
perfil objetivo POSIX con UID separado, perfil UID único, cloud gestionado
genérico por evaluar, Windows con ACL y entorno desconocido. Especificar las evidencias mínimas de
cuentas, permisos, privilegios, interop WSL, canal humano/UI, código de un solo
uso, recibo auténtico, Git privado, recuperación y revocación. Todo perfil
permanece no operativo hasta pruebas materiales y revisión posterior.
Definir además la reconstrucción reproducible de código, ABI, dependencias
transitivas y herramientas, y registrar sus brechas actuales. Un cloud
distinto no se rechaza por etiqueta: se evalúa su frontera; esta instancia
con UID compartido sí quedó bloqueada por prueba.

No implementar guardián, UI, Git privado, provisionar cuentas, emitir tarjeta,
enviar enlaces ni conceder autoridad. La skill de requisitos sigue siendo
documental; su activación no se convierte en autorización de procesos.

## Oráculos RED congelados

1. Un perfil con UID único, cloud gestionado sin frontera probada o entorno
   desconocido no puede producir READY, HUMAN_CONFIRMED ni permiso.
2. El perfil POSIX separado conserva D05 bloqueado aunque el preflight de UID
   observe dos usuarios; exige controles negativos desde el agente, ausencia
   de elevación, y en WSL prueba específica de interop Windows.
3. Git commit o SHA sin autenticación independiente del guardián no es recibo;
   UI/captura no demuestra percepción humana; el enlace no es autorización.
4. Falta de cualquier evidencia crítica, reloj, cuenta, custodia, recuperación
   o canal humano mantiene `NOT_ESTABLISHED` y `execution_authorized=false`.
5. La skill debe remitir a este contrato al hablar de despliegue, sin prometer
   instalación automática ni sustituir el gate D05 por `requirements activate`.
6. Ausencia de lock con hashes, ABI incompatible o controles de host no
   ensayados no permite afirmar que el mismo entorno fue reproducido.

## Proceso

ODD → falsadores documentales RED → referencia/contrato GREEN → regresión →
revisión independiente y RDD nativo del candidato exacto → respaldo Git.
Ensayo en i3/WSL, cuentas separadas y UI real: NOT_RUN.

## Evidencia RED/GREEN documental

RED inicial: `python3 -B -m unittest discover -s
skills/requerimientos-socraticos/tests -p
'test_rs3_authority_deployment_contract.py' -q` terminó con tres errores
`FileNotFoundError` por contrato y referencia ausentes. Tras crear ambos,
tres pruebas pasaron. La revisión independiente señaló que faltaban gates de
reloj, nonce, recomputación del desafío, control de UI y custodia de clave.
Al añadir los falsadores al test antes del contrato, la prueba falló porque
`CORE_GATES` no estaba cubierto; los subcasos de mutación todavía no podían
ejecutarse contra esos campos ausentes. GREEN posterior: tres pruebas `OK`,
incluidas mutaciones en memoria que intentan habilitar un UID único o retirar
controles críticos. Regresión completa con dependencias declaradas:
`PATH=/tmp/rs3-wu037-venv/bin:$PATH
REQUIREMENTS_PYTHON=/tmp/rs3-wu037-venv/bin/python bash ci/run_quality.sh`,
exit 0: 55 CI, 162 supervisor, 62 QA y 412 requisitos, todos `OK`.
La revisión independiente no encontró bloqueos críticos para RDD. La última
corrección editorial aclaró cloud genérico frente a esta instancia bloqueada;
no alteró tests ni contrato. RDD y hardware objetivo: pendientes.
