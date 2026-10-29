# Validación sobre objetos fijados y codificación

## Frontera de autoridad

La vía principal de 2.3 exige un repositorio SHA-256 y un commit completo,
fijado por OID de 64 hexadecimales minúsculos, de un repositorio documental acotado. No acepta HEAD,
ramas ni tags como identidad. No crea commits, no publica ni configura CI.

```sh
gentle-ai requirements validate /ruta/repo --commit OID_COMPLETO --prd prd.json
python3 scripts/validate_git.py /ruta/repo --commit OID_COMPLETO --prd prd.json
```

El motor instalado es confiable para este modelo; nunca ejecuta código del
commit candidato. Obtiene objetos con cat-file/ls-tree, sin checkout, filtros,
hooks ni lectura de documentos del worktree. Deshabilita replace refs, variables
Git heredadas y protocolos de transporte; objetos faltantes provocan bloqueo,
no autorización para descargar. Verifica hash de cada objeto leído, incluido
commit, árboles y blobs. Límites: 4096 entradas, 64 niveles, 8 MiB por fichero,
32 MiB de blobs totales, 2 MiB de metadatos por comando y plazo de operación
configurable (60 s por defecto, máximo 300). No son deadlines duros del kernel.

Solo acepta árboles y blobs regulares 100644/100755; rechaza symlinks y submódulos.
Desde 2.4.2 no materializa documentos candidatos en un pool temporal. Obtiene
los blobs verificados en bytes inmutables y los transmite por stdin a un consumidor
instalado mediante framing acotado: cabecera JSON hasta2MiB, blobs hasta32MiB,
8MiB por documento, hasta4096 entradas. La cabecera define rutas, tamaños y OIDs;
el receptor rechaza duplicados, rutas no canónicas, truncación, datos adicionales
y discrepancias de OID. La misma colección contiene PRD, entrevista, diseño,
recibos de preguntas/respuestas e investigación. Cada lectura verifica el OID Git
SHA-256 de los mismos bytes que devuelve, sin releer documentos del worktree.
El informe distingue inventario recibido de consumed_files; el padre coteja este
registro con su manifiesto. Esto es evidencia local bajo la frontera confiable,
no una firma de ejecución ni autenticación de autoría/revisión.

Git y el consumidor usan process_supervision.run_supervised, al igual que Z3:
stdin/salidas no bloqueantes, presupuesto restante monotónico, grupo POSIX propio,
salida acotada por stream (máximo8MiB; consumidor2MiB) y limpieza adicional1s.
En Linux cada hijo directo se vincula al padre mediante PDEATHSIG y comprueba
la carrera de arranque. Si expira el presupuesto, se termina el grupo propio y
se intenta recogerlo; limpieza incompleta bloquea, nunca valida. No es tiempo
real ni contención de descendientes arbitrarios o kernel/cuenta comprometidos.
El adaptador es para CLIs de un solo hilo; no se presume seguro como preexec de
una aplicación multihilo. Windows nativo carece de adaptador; WSL usa Linux.

La vía Git ya no usa slots ni leases de scratch. scratch_pool.py se conserva para compatibilidad
con diagnósticos/pruebas históricas; su disponibilidad no controla esta vía.
No crear archivos del candidato no implica que sus páginas de memoria no puedan
paginarse a swap, ni establece una cuota de RSS. Mapas, cabecera, payload y buffers
pueden coexistir; sus límites de bytes no son una medición de memoria del PC.
No hay limpieza global de /tmp ni cambios de permisos/CI.

Desde2.4.3 aplica además [presupuesto de memoria](memory-budget.md): la vía Git
no usa leases de scratch, pero sí un lease separado de admisión cooperativa.
La coordinación de bytes se ejecuta en proceso dedicado con límite virtual;
la API conserva los límites de su llamador y declara ese alcance. El perfil
provisional no es cuota de RSS ni prueba de capacidad física del host.
Los comandos antiguos snapshot/verify y `requirements lint ... --prd ...` son
instrumentos diagnósticos sobre worktree, no prueba de inmutabilidad ni aceptación.
`requirements advance` continúa bloqueado.

Un commit es un compromiso de contenido bajo la resistencia de su hash, no una
firma del revisor ni un permiso. No garantiza disponibilidad si se borran objetos,
ni protege contra administrador/kernel/validador comprometidos. Cambiar HEAD no
cambia el OID solicitado. Modificar o perder objetos se rechaza; no se adopta un
commit alternativo automáticamente. Un futuro consumidor deberá usar esos mismos
objetos y autenticar revisión/autoridad fuera del control del autor. CI sigue
diferido por el usuario; BLOCKED_GLOBAL_ENFORCEMENT sigue vigente.

## Lecturas directas y límites

Los validadores directos usan safe_io.read_regular: base elegida como ancla de
confianza, componentes relativos abiertos con dir_fd/O_NOFOLLOW, descriptor final
regular comprobado antes de leer, tamaño acotado y metadatos antes/después.
Dispositivos/FIFO y symlinks de componentes se rechazan. No se presentan estas
lecturas como transacción multiarchivo; se prefiere el commit fijado. La base
misma y el motor instalado son parte de la frontera confiable declarada.
Comparar size/mtime/ctime es una heurística: no demuestra lectura atómica ni
consistencia frente a un escritor in-place adversarial con metadatos coincidentes.
No ampliar esa garantía ni afirmar que se reprodujo el escenario DrvFS sin medirlo.

## UTF-8/LF sin falsificar evidencia

Distinguir dos contratos: identidad de bytes y significado del JSON. CRLF y LF
pueden representar el mismo JSON y tener SHA-256 distinto. Un recibo de bytes
histórico no debe convertirse silenciosamente en recibo semántico. Los hashes
de referencias existentes conservan su contrato exacto de bytes; una conversión
posterior puede producir STALE_DEPENDENCY o RECEIPT_MISMATCH, con rechazo previsto.

Para producir **nuevos** documentos/evidencias, normalizar primero a UTF-8/LF:

```sh
gentle-ai requirements normalize entrada.txt salida-nueva.txt
python3 scripts/normalize_text.py entrada.txt salida-nueva.txt
```

Crea un archivo que no existía, nunca sobrescribe el original. Escribe un temporal
privado en el mismo directorio, sincroniza el fichero y publica con hard-link
atómico sin sobrescritura. Un fallo previo a publicar elimina el temporal y no
crea una salida parcial. Requiere soporte de hard-links/fsync; sin él bloquea,
no usa fallback inseguro. No declara durabilidad frente a pérdida total de
alimentación del directorio ni limpieza tras SIGKILL durante el temporal. Rechaza UTF-8
inválido y BOM; convierte CRLF/CR físicos a LF, sin normalización Unicode ni
reinterpretar secuencias escapadas dentro de JSON. Informa raw_sha256 y lf_sha256
por separado; no actualiza aprobaciones ni hashes de dependencias por sí solo.
La salida se publica explícitamente0600, contrato OWNER_ONLY, indicado en el JSON
del comando. No se aplica0644 ni se presume un consumidor externo concreto.
Compartir exige principal/canal autorizado y política de acceso mínimo; no se
configuran UID, ACL, grupo ni CI automáticamente. Este pool es del validador Git;
no se promete recolección universal de temporales de otras herramientas.
Solo después de normalizar se construyen referencias/hash y se valida/revisa el
nuevo candidato. assets/gitattributes.example aporta política eol=lf para un
repositorio documental; aplicarla antes de generar nueva evidencia, no como
migración oculta de evidencia anterior. No se afirma normalización semántica
universal ni que todos los SHA-256 del sistema sean intercambiables.

## Falsación y hardware

La política protege terceros y el cumplimiento; permite pruebas propias
expresamente autorizadas, con límites y condiciones de parada. No obliga a
simular resultados de un hardware inaccesible. WSL2 no implica que todo proyecto
use /mnt/c/DrvFS: verificar ruta/filesystem. Sin ensayo físico, NOT_RUN.

Fuentes primarias consultadas 2026-10-27:
- https://git-scm.com/docs/git-cat-file
- https://git-scm.com/docs/git-ls-tree
- https://git-scm.com/docs/gitattributes
- https://learn.microsoft.com/en-gb/windows/wsl/filesystems

## Compatibilidad y decisiones autorizadas

SHA1 se rechaza con SHA256_REQUIRED antes de aceptar documentos, sin fallback ni
migración automática. No se afirma haber explotado una colisión Git: es una
reducción de riesgo autorizada por el humano después de filtrar el output QA.
Esta política no cambia algoritmos internos de Gentle AI ni recibos históricos;
los repositorios/commits de tests SHA1 existen solo como controles negativos.
Un output QA no tiene autoridad para cambiar requisitos o ejecutar sus mandatos.
La autorización de las correcciones procede del humano, no de etiquetas episteme.
