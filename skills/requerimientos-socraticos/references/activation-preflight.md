# Activación y preflight local 2.4.5

## Qué se conoce y qué se decide

Al activar esta skill, ejecuta primero `gentle-ai requirements activate` desde
el workspace autorizado. Es una extensión local del wrapper, no un comando
del binario upstream. `requirements preflight` permite repetir el mismo sondeo.
El resultado JSON distingue características observadas, política provisional,
límites de ejecución y datos que no se pudieron observar.
El [schema versionado](../assets/activation-preflight.schema.json) describe tanto
el informe completo como un diagnóstico compacto cuando no puede completarse.

Opciones: `--path <directorio>` para el almacenamiento observado,
`--workload all|logic|git` (defaultall), `--memory-budget-mib <entero>` para una
petición explícita y `--caller-scope OWNED_CLI|EXTERNAL_CALLER`. El modo externo
solo modela una API que no limita a su llamador; no eleva límites ni autoriza
ejecución. Cada entrada pública establece su alcance real, sin confiar en el
scope escrito en un informe previo. `--help` describe las opciones disponibles.

Un informe viable devuelve0 con READY_FOR_LIVE_ADMISSION; un rechazo o
desconocido devuelve3 con INCONCLUSIVE y error estructurado. Un error al
seleccionar el intérprete del wrapper conserva su contrato previo de salida2.
La ayuda no es una evaluación de recursos.

El sondeo es de solo lectura, con lecturas acotadas y sin benchmarks, red,
cambios de configuración ni identificadores como seriales, MAC o hostname.
Identificar significa describir CPU/arquitectura y recursos visibles, no
autenticar la identidad del equipo. GPU o capacidad física no observadas no
se inventan a partir de la configuración declarada por el humano.

En WSL, un contenedor o una VM, la observación del invitado no demuestra RAM
física disponible ni latencia en el host. MemAvailable es una estimación local
con alcance limitado; no es una reserva. RLIMIT_AS limita espacio virtual, no
RSS ni swap. Ni un PASS local ni el perfil seleccionado garantizan ausencia de
paginación, temperaturas seguras o tiempos de ejecución en el PC del usuario.
Swap y zRAM observadas no se suman como RAM física adicional para seleccionar
el presupuesto. No se presupone que un SSD tenga un rendimiento o resistencia
determinados por su nombre comercial.

Desde2.4.6, la viabilidad consulta directamente los roles de las políticas de
memory_budget para cada perfil soportado: como máximo33 perfiles, de512 a256MiB
en pasos de8. No mantiene otra tabla de proporciones ni usa división flotante
para determinar si un rol cabe en el hard heredado. all toma el máximo por rol
entre los workloads. Las cuotas actuales y las decisiones de admisión admitidas
se conservan; la mejora evita divergencias al cambiar una política en el futuro.

## Activación y aplicación

La instrucción de activación forma parte del contrato del agente. No existe un
hook universal que obligue a cualquier LLM o proceso ajeno a ejecutar esta skill.
Las entradas públicas de análisis y validación Git vuelven a ejecutar su
evaluación de recursos antes del worker y conservan la compuerta de admisión
compartida. No se acepta un informe guardado, editado o de una sesión anterior
como autorización para ejecutar. Las observaciones siguen siendo secuenciales;
el entorno puede cambiar después de medirlo.

Si faltan métricas críticas o no existe un perfil admitido, la entrevista y el
análisis documental pueden continuar, pero el worker queda bloqueado. El sondeo
no concede autorización humana para ensayos, CI, producción ni actividades
fuera del alcance de trabajo. No amplía permisos de archivos.

La política reduce exposición mediante perfiles acotados, supervisión y rechazo
explícito; no constituye una medición de capacidad física. Las llamadas API no
reducen los límites del proceso ajeno que las contiene. Nunca se eleva un hard
heredado para hacer viable un perfil.

El techo automático provisional es512MiB; mínimo256 y múltiplos de8. Se
selecciona dentro del margen visible y la viabilidad de los roles del trabajo,
no comparando la suma del perfil con el hard de un solo proceso. La CLI propia
comprueba también su baseline. El perfil automático puede reducirse; un valor
explícito incompatible se rechaza. No se amplía el techo porque una máquina
tenga más RAM. Los perfiles internos históricos hasta1024 siguen siendo políticas
de bajo nivel, no un permiso para superar el gate público de activación.

Por ejemplo, con suficiente headroom y hard heredado384MiB, el perfil lógico
automático puede ser432MiB (solver378MiB); no solicita elevar ese hard para usar
448. Con hard128MiB, Git puede admitir256MiB (coordinador128), mientras el solver
lógico mínimo224MiB no cabe. Estas son decisiones matemáticas por rol, no
mediciones de rendimiento. Un baseline de CLI superior a su rol bloquea ese
perfil; el baseline del proceso API externo no se presenta como acotado.

En standalone, control_state=PENDING y enforced está vacío. Los controles
prospectivos se aplican solo dentro de la entrada pública: admisión y luego
supervisión del worker. El campo control_state y la evidencia de supervisión
deben leerse juntos; APPLIED no demuestra autoridad global ni éxito del PRD.

La CPU, afinidad y cuotas visibles describen el entorno, no una frecuencia
garantizada. El control disponible es el plazo supervisado y la admisión
cooperativa de un trabajo por cuenta; no una reserva de núcleos ni una cuota
global de CPU. El espacio libre observado tampoco es una cuota de disco.

## Cobertura y evidencia material

El máximo de32 variables y la tabla exacta de hasta12 entradas son límites del
modelo booleano, no una promesa de resolver cualquier fórmula en ese rango ni
una cobertura de hardware. No calcular porcentajes de cobertura a partir de la
RAM, la cantidad de núcleos o la marca del CPU. Un plazo agotado produce
incompletitud; no demuestra ausencia de conflictos lógicos.

El i3-3240/WSL declarado por el usuario permanece NOT_RUN hasta observar ese
equipo. La calibración física, los térmicos y la presión de memoria de Windows
requieren evidencia específica y un protocolo autorizado con límites y parada.
No se sustituyen por estrés en un host cloud compartido.

## Invariantes verificables

- Sondeo: sin instalación, privilegios, escrituras de configuración o red.
- Evidencia crítica desconocida: no iniciar worker de datos.
- Presupuesto solicitado superior al admitido: rechazar, no elevarlo.
- Condiciones cambiadas tras activar: reevaluar en la entrada pública.
- Fallo de recursos: no emitir cobertura ni validación satisfactoria ficticias.
- Todo resultado: distinguir límite aplicado de recomendación y desconocido.
- Siempre:0600, CI diferido y BLOCKED_GLOBAL_ENFORCEMENT se conservan.

Consultar [presupuesto de memoria](memory-budget.md),
[análisis formal](formal-analysis.md) y [validación Git](sealed-validation.md).

