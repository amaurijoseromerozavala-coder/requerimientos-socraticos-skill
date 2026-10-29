# Presupuestos de memoria Git y analizador 2.4.4

Desde2.4.5 las entradas públicas aplican además el
[preflight de activación](activation-preflight.md): selección automática y techo
conservador hasta512MiB. El rango256..1024 descrito abajo corresponde a los helpers
internos históricos; un perfil válido de bajo nivel puede ser rechazado por el
gate público. La API no modifica límites de su proceso llamador.

## Alcance y perfil inicial

El perfil es una política técnica provisional, no una capacidad física observada.
La opción `--memory-budget-mib` admite enteros256..1024 múltiplos de8; default512.
Se conserva el límite documental8MiB por archivo/32MiB de blobs: admisibilidad de
bytes y viabilidad bajo un perfil de recursos son obligaciones distintas. No se
promete aceptar todo documento admisible con cualquier perfil.

| Rol con perfil512 | Soft RLIMIT_AS MiB | Hard RLIMIT_AS MiB |
| --- | --- | --- |
| CLI propia, solo metadatos y supervisión |64|256|
| Coordinador dedicado de objetos y transporte |256|256|
| Consumidor de documentos y schemas |128|128|
| Comando Git directo |64|64|

Las proporciones son caller1/8, coordinador1/2, consumidor1/4 y Git1/8. Se suman
los soft configurados para describir el perfil; no existe una cuota kernel
agregada ni una reserva física de512MiB. El hard de la CLI permite que su hijo
configure un soft mayor antes de exec sin elevar un hard heredado. El código
confiable de la CLI mantiene su propio soft64. Cada hijo aplica sus límites
antes de exec; el entorno es Linux, CLI de un hilo, motor/cuenta/kernel confiables.

RLIMIT_AS limita asignación de espacio virtual; no RSS, kernel, archivos cacheados
ni swap del host. Reducirlo no elimina mappings existentes. La CLI comprueba
su VmSize antes de reducirlo: UNKNOWN o VmSize mayor que su rol bloquean con
RESOURCE_BASELINE_UNKNOWN/RESOURCE_BASELINE_EXCEEDS_ROLE_BUDGET. Un perfil válido
puede no ser viable para un runtime dado. No se aumentan límites heredados.

La API `validate_commit` no altera límites de su llamador: inicia un coordinador
limitado y declara caller.scope=EXTERNAL_CALLER_NOT_LIMITED. Su perfil no acota
la memoria total de esa aplicación externa. La CLI fresh propia sí limita su
rol y lo declara OWNED_CLI_PROCESS. Los helpers internos no son una autoridad
de avance; su invocación directa no equivale al contrato de la entrada pública.

## Admisión cooperativa

Antes del trabajo de datos se toma un lock privado por cuenta, no bloqueante,
en /tmp/requirements-admission-UID (directorio700, fichero600, propietario y tipo
comprobados, sin symlinks). RESOURCE_BUSY rechaza una segunda admisión. El FD se
hereda explícitamente al coordinador y sus consumidores; se cierra al terminar,
sin desbloqueo explícito que libere prematuramente un lease heredado. No hay GC
global ni borrado de temporales ajenos.

Se observan MemAvailable y límites/uso de todos los ancestros cgroup-v2 visibles.
Se exige headroom visible >=2x perfil; estados desconocidos/malformados o uso
finito desconocido bloquean. Esta reserva2x es criterio de admisión, no reserva
real ni prueba de que Windows/host físico conserve memoria disponible. Muestras
secuenciales, ancestros invisibles y cambios concurrentes permanecen desconocidos.
No se escriben cgroups, no se cambian privilegios ni se configura CI.

El lock coordina clientes cooperantes de la misma cuenta; no impone una cuota
global a procesos externos ni limita todos los llamadores que arranquen a la vez.
Su coste de arranque y control debe distinguirse del trabajo admitido de datos.
Un kernel que no complete la terminación puede retener el lease: se declara
bloqueo/incompletitud, no disponibilidad garantizada.

## Observación y resultados

memory_budget en la respuesta contiene política, admisión, caller, coordinador
y consumidor. VmSize/RSS proceden de /proc/self/statm; peak_rss_bytes es el
high-water de getrusage(RUSAGE_SELF) hasta el instante de muestra. Se registra
soft/hard real con getrlimit. No sumar picos no simultáneos como pico global.
Las muestras anteriores a serializar/salir no prueban el máximo del resto de
la ejecución. Las métricas no son firmas ni autoridad externa.

Ante MemoryError capturado se intenta emitir un registro fijo predefinido
MEMORY_BUDGET_EXCEEDED. No se presupone poder recuperar cualquier fallo nativo,
escritura de diagnóstico o agotamiento del sistema. Una señal o respuesta
ausente produce fallo bloqueado con causa no demostrada, nunca un OOM afirmado
por inferencia. El padre conserva plazo y límite de salida; el transporte final
del coordinador permite8MiB para manifiesto completo, el consumidor2MiB.

## Invariantes y falsadores

- Perfil inválido: rechazar antes de crear procesos de datos.
- Admisión desconocida/insuficiente/ocupada: no ejecutar validación documental.
- API normal: RLIMIT del llamador antes/después idéntico.
- Hijo iniciado: aplicar soft/hard solicitados antes de exec o bloquear.
- Error explícito de memoria: no emitir DOCUMENT_VALIDATED_GIT.
- Señal sin diagnóstico: no etiquetar como agotamiento demostrado.
- Cualquier resultado válido: identidad de bytes y avance bloqueado se conservan.

Pruebas: test_memory_budget, test_validation_budget, test_process_supervision,
test_git_memory y regresión de validadores. Ensayos reales pequeños en procesos
propios; nunca llenar RAM/swap del host como sustituto de medir el equipo objetivo.
El perfil anterior de roles se aplica a validación Git. Desde2.4.4 el analizador
dispone de un perfil propio, descrito a continuación; no se declaran cuotas para
todas las herramientas o todos los procesos del host.

## Perfil del analizador/Z3

logic_memory_policy utiliza el mismo rango256..1024MiB, múltiplo8, default512;
roles caller1/8 y solver7/8. Con512: CLI soft64/hard448, worker soft448/hard448MiB.
El marcadorworkload=BOOLEAN_ANALYSIS distingue el perfil del Git, que no cambia.
Ambos usan el mismo gate por cuenta; no se habilitan dos trabajos pesados por
usar perfiles distintos. Headroom visible requerido2x total y UNKNOWN bloqueado
se conservan. No hay cgroup escrito, reserva física ni cuotaRSS agregada.

La CLI analiza su baseline antes de limitarse. Su main(_own_cli=False) desde un
llamador externo no reduce límites propios; aun así configura el worker antes
de exec. El hard heredado nunca se eleva. La entrada CLI exige soft/hard observado
del worker igual a lo solicitado para aceptar una respuesta satisfactoria. La
respuesta de la API externa conserva observaciones; no convierte datos locales
en una autoridad autenticada fuera de la cuenta/kernel/motor confiables.

El worker informa memory_observation al terminar el análisis satisfactoriamente.
Son muestras por proceso, anteriores al final de serialización, no máximos de
toda la ejecución ni del host. Error MemoryError capturado intenta emitir un
registro fijo INCONCLUSIVE/MEMORY_BUDGET_EXCEEDED, exit3, sin queries/table/coverage.
El supervisor también descarta esos resultados si recibe un error explícito de
memoria. Un error nativoZ3 conserva SOLVER_ERROR; una señal o JSON ausente conserva
WORKER_FAILED sin afirmar OOM. Se mantienen INVALID_INPUT y SOLVER_UNAVAILABLE.

El tiempo total incluye identidad del runtime, preparación y admisión. Si se
agota antes del worker, no se crea éste y se devuelve WALL_CLOCK_LIMIT. La
limpieza adicional del supervisor y sus límites de SO siguen siendo los mismos.
El perfil no garantiza que un fallo nativo siempre se convierta en MemoryError.

El helper valida tipos canónicos y regenera un snapshot del perfil para el
criterio de headroom. Coerciones float/int o bool/int y cambios posteriores del
dict externo no modifican silenciosamente ese criterio. El dict y validación de
memory_policy() Git permanecen iguales; no cambia la intención de sus requisitos.

Pruebas adicionales: test_logic_memory, test_logic_worker_memory y regresión de
lógica/supervisión. Los ensayos de CLI se ejecutan secuencialmente por el gate
compartido: contención esperada no se etiqueta como fallo de lógica del producto.

Fuentes primarias: https://man7.org/linux/man-pages/man2/getrlimit.2.html y
https://docs.python.org/3.12/library/resource.html . Los resultados y perfiles
medidos deben acompañar las afirmaciones; el i3/WSL sigue NOT_RUN.
