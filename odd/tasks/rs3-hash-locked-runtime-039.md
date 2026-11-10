# WU-RS3-HASH-LOCKED-RUNTIME-039

## Objetivo y precedente

Desde WU-038, construir una primera instalación reproducible del runtime
Python de Requerimientos Socráticos sin Docker obligatorio y sin fijarlo al
i3-3240. El usuario autorizó continuar. El alcance no incluye cuenta de
guardián, UI, Git privado ni autoridad D05.

## Contrato y límites

- Resolver dependencias directas y transitivas para CPython 3.12 en un lock
  universal con versiones y hashes SHA-256 de distribuciones. Instalar solo
  ruedas binarias verificadas; arquitectura sin rueda compatible bloquea.
- La entrada de instalación usa Python absoluto proporcionado por el
  operador, verifica ABI CPython 3.12 y digest del lock, exige destino nuevo
  en un directorio escribible y espacio visible mínimo. No actualiza otro
  entorno ni modifica requisitos, cuentas, shell global o red fuera de pip.
- Construir en staging privado, ejecutar `pip` con `--require-hashes` y
  `--only-binary=:all:`, comprobar dependencias/importaciones y promover solo
  tras éxito. Fallo/timeout deja destino ausente y salida no autoritativa.
- Es una reconstrucción de dependencias lógicas en cada plataforma compatible,
  no una promesa de identidad byte a byte de Python, kernel o hardware. La
  disponibilidad física y D05 se comprueban por separado. El lock puede
  incluir hashes de artefactos no ensayados; otros OS/arquitecturas: NOT_RUN.
- Actualizar la referencia portable de instalación y el contrato de
  despliegue: ya habrá lock transitivo, pero CI y otros OS/arquitecturas aún
  no se habrán verificado con él. El Dockerfile sin digest no cambia.

## Oráculos RED congelados

1. No hay instalador ni lock; una solicitud de preparación debe bloquear.
2. Lock alterado, Python no 3.12/CPython, destino ya existente, ruta no
   absoluta o espacio insuficiente bloquean antes de llamar a pip.
3. Comando de instalación nunca omite `--require-hashes` ni
   `--only-binary=:all:`; error o timeout de pip no promueve el destino.
   Limpia staging cuando la limpieza del proceso está confirmada; ante
   incertidumbre lo conserva y bloquea.
4. Instalación real en directorio temporal: versión de paquetes directos y
   transitivos del lock, `pip check` y smoke import; resultado conserva
   `authority_verification=NOT_ESTABLISHED` y `execution_authorized=false`.
5. Mismo lock y fuente no autorizan cuentas, UI, códigos, recibos o producción.
6. La skill señala el instalador propio y no conserva como brecha la ausencia
   de lock transitivo después de incorporarlo; faltas de prueba en CI y otras
   plataformas siguen explícitas.
7. El lock instalado procede de los bytes verificados, no de una segunda lectura
   del archivo mutable; la promoción no reemplaza un destino creado en carrera.
   Fallos de staging o limpieza producen bloqueo estructurado.
8. Lectura del lock acotada por descriptor; `pip` aislado de configuración
   ambiental y fijado al índice público. Registrar hashes de las ruedas
   efectivamente seleccionadas. Ante timeout se envía SIGKILL al grupo y se
   recolecta el líder; no confirma cada descendiente ni equivale a sandbox
   contra procesos que abandonen el grupo.
9. Las invocaciones de Python del instalador usan `-I` para ignorar
   `PYTHONPATH`/`sitecustomize`. Un error al señalar el grupo conserva el
   staging y emite `PROCESS_CLEANUP_UNCONFIRMED`, sin afirmar recolección de
   descendientes arbitrarios.
10. Los scripts de un venv contienen rutas absolutas; reescribir referencias
    de staging en sus entradas de texto antes de promover y comprobar `pip`
    y activación desde la ruta final. Si la verificación posterior falla,
    retirar el destino o bloquear si la limpieza es incierta.

## Proceso

ODD → RED pertinente → lock e instalación mínima → GREEN/regresión → revisión
independiente → RDD exacto → respaldo Git. Perfil POSIX Linux/WSL es el
primer destino; esta corrida cloud no sustituye i3/WSL. No declarar
reproducción universal ni D05 resuelto.

## Evidencia observada del candidato local

- RED inicial: importación de `prepare_runtime` falló con
  `ModuleNotFoundError`; el control de guía falló por falta de instalador.
- RED tras revisión independiente: cinco fallos/errores focales por ruta
  mutable del lock, falta de promoción no-replace, excepción de limpieza sin
  estructura y guía desactualizada. El test de fallo de instalación ahora
  falla en la segunda llamada (pip), no en la creación del venv.
- GREEN focal inicial: 10 pruebas, `OK`; tras falsadores adicionales,
  15 pruebas, `OK`. La instalación en directorio temporal con
  CPython 3.12 Linux x86_64 devolvió `PREPARED_RUNTIME_NOT_AUTHORITY`,
  `pip check` exit 0, imports jsonschema 4.26.0 y Z3 4.15.4.
- Regresión completa inicial `ci/run_quality.sh`: exit 0; 55 pruebas CI, 162 de
  supervisor, 62 de QA y 422 de requisitos. Repetición posterior: exit 0,
  55 CI, 162 supervisor, 62 QA y 427 requisitos. Instalación real posterior
  al aislamiento `-I`: exit 0, siete ruedas registradas.
- RDD nativo del candidato `sha256:ae8f2c421f990d6cf2cb9d45c19db98086e2139fda2a5d273900aae967e43ccd`
  encontró R3-relocated-venv y R4-001 (CRITICAL): al mover staging,
  `pip` y activación conservaban la ruta antigua. Estado `correction_required`;
  no se respaldó ese candidato. Plan acotado de 120 líneas capturado en
  lineage `review-785d080dffb7ecb3`.
- RED de corrección: nueva prueba de pip y activación tras promoción falló por
  `_repair_relocation` ausente. GREEN focal corregido: 17 pruebas `OK`.
  Instalación temporal real: siete ruedas, `pip` final exit 0 y activación
  apunta al destino final. Regresión y RDD del candidato corregido pendientes.
  Otros sistemas y D05: `NOT_RUN`/`NOT_ESTABLISHED`.
