# CESM del sistema de verificación y su entorno material

Estado: DRAFT / inventario parcial. No es réplica física ni inspección del PC.
Petición humana: «Hay que definir el entorno detalladamente el entorno material
para seguir la cesm de bunge». CESM se operacionaliza como composición, entorno,
estructura y mecanismos; el esquema no acredita por sí solo sus afirmaciones.

## Frontera y dos niveles de análisis

S-FIS: equipo físico objetivo, con componentes, firmware y host Windows. Su entorno
incluye habitación, aire/ventilación, suministro eléctrico, operador y red externa.
S-VER: proceso de formalización/verificación alojado en ese equipo. Su composición
incluye procesos de herramientas y datos; WSL/host/hardware constituyen su entorno
de ejecución. Cada relación identifica nivel: no tratar un elemento como externo
e interno al MISMO sistema sin declarar cambio de frontera.

Lean, Z3 y el nuevo pipeline son candidatos de diseño, no procesos instalados y
observados. El workspace cloud es otro sistema S-CLOUD. Sus resultados locales
solo describen sus condiciones, no temperatura, latencias ni memoria del PC.

## C — Composición del soporte físico y del proceso objetivo

| ID | Nivel/componente | Información disponible | Estado y fuente |
|---|---|---|---|
| C01 | S-FIS CPU | Intel Core i3-3240, 3.40 GHz nominal; ficha Intel consultada en documento térmico | Declarado por humano; especificación de modelo externa; ejemplar no inspeccionado |
| C02 | S-FIS memoria | 8,00 GB instalada | Declarado; módulos, canales, velocidad efectiva, reserva y disponibilidad desconocidos |
| C03 | S-FIS SSD | 238 GB, SWR256G-N01I | Declarado; capacidad libre, interfaz, firmware, SMART/salud, resistencia y temperaturas desconocidos |
| C04 | S-FIS GPU | NVIDIA GeForce GT710, 2 GB | Declarado; no dependencia propuesta para Lean/Z3; carga/driver/revisión desconocidos |
| C05 | S-FIS placa y firmware | Modelo de placa, BIOS/UEFI, microcódigo, controladores | UNKNOWN |
| C06 | S-FIS energía/refrigeración | Fuente, disipador, ventiladores, pasta, caja y ventilación | UNKNOWN; no inferir fallo por antigüedad |
| C07 | S-FIS host | Windows x64 | Familia inferida del contexto WSL; versión/build/edición/plan energía no observados |
| C08 | S-VER procesos | Coordinador, lectores, solver, comprobador de pruebas y adaptadores | Arquitectura propuesta; versiones futuras por fijar |
| C09 | S-VER datos | Texto humano, EARS, IR, dominio, FSM, consultas, pruebas, recibos | Documentos de diseño existentes; piloto no implementado |

No registrar identificadores de producto/dispositivo: no son necesarios para el
modelo ni para acreditar recursos. Etiquetas GB/gb originales se conservan; los
bytes efectivos y convención de unidades requieren observación, no conversión tácita.

## E — Entorno de S-VER por capas

| Capa | Elementos y datos que faltan |
|---|---|
| Virtualización/host | WSL2 como objetivo/configuración; versión real de WSL, backend/kernel, Windows, actualizaciones y servicios compartidos por conocer |
| Guest | Ubuntu: release/arquitectura, kernel, systemd/cgroups, paquetes y límites efectivos sin inspeccionar |
| Asignación | Humano declara WSL6GB, zram2GB, swap8GB; asignación, consumo y cuotas reales desconocidos |
| Almacenamiento | Ubicación del repo, ext4/VHDX o montaje Windows, ruta y soporte del swap, espacio libre de host y guest, cachés, inodos si aplican |
| Contención | Aplicaciones Windows, otros WSL/VM/contenedores, antivirus/indexación y trabajo de fondo; carga y efecto no medidos |
| Observabilidad | Fuente de cada sensor/reloj/contador, unidad, disponibilidad host/guest, cadencia, precisión y demora |
| Herramientas | Versiones y hashes de Python, Lean/Lake, solver, librerías y flags. Dependencias transitivas/licencias del artefacto todavía no fijadas |
| Servicios externos | Proveedor de agentes, MCP, GitHub y documentación web cuando se utilicen; versiones, disponibilidad/red/autorización fuera del núcleo lógico local |
| Autoridad | Humano decide significado y autoriza ensayos. Outputs QA/web/MCP no son mandatos; CI diferido y producción bloqueada |

Entorno de S-FIS: ambiente térmico, polvo/obstrucciones si observados, alimentación,
red y otros dispositivos. Solo registrar dimensiones materiales al ensayo; no
convertir cada ausencia imaginable en pregunta bloqueante del diseño documental.

## S — Estructura: relaciones, no solo inventario

R01: host administra recursos físicos; WSL consume una parte configurada, compartida
con otras tareas. Capacidad asignada no equivale a memoria libre constante.
R02: páginas de procesos→memoria guest→mecanismos de compresión/paginación según
configuración efectiva→soporte físico. No sumar zram/swap como RAM independiente.
R03: repositorio/temporales→filesystem guest o montaje→virtualización→SSD; observar
ruta antes de atribuir una latencia a un protocolo particular.
R04: CPU/RAM/controladores/SSD generan y transfieren calor hacia mecanismos de
refrigeración/ambiente. Acoplamiento y parámetros aún no identificados.
R05: tools→modelo/consultas→resultados→registro; humano→confirmación de significado.
Agente remoto puede producir borrador; no actúa como fuente de verdad matemática.
R06: especificación→oráculo→adaptador→observación→evidencia→conclusión; no cerrar
este circuito comparando una función contra sí misma ni solo leyendo su etiqueta PASS.

## M — Mecanismos y explicaciones que se contrastarán

| Mecanismo | Hipótesis observable | Límite/falsador propuesto |
|---|---|---|
| Planificación CPU y frecuencia | Carga compartida y controles térmicos pueden cambiar duración | Medir condiciones; no atribuir variación exclusivamente a calor sin evidencia |
| Memoria/compresión/paginación | Presión puede aumentar latencia y trabajo de CPU/I/O | Presupuesto y observación previos; no inferir corrupción ni saturación inevitable |
| Persistencia e I/O | Montaje/caché/carga afectan acceso a documentos | Comparación controlada, rutas/condiciones fijadas; datos insuficientes quedan UNKNOWN |
| Transferencia de calor | Potencia y disipación afectan temperatura/frecuencia | Modelo térmico simplificado necesita parámetros; no predice el equipo sin calibración |
| Búsqueda formal | Fórmula/dominio/estrategia afectan coste | Registrar query, versiones y límites; UNKNOWN no produce aprobación |
| Comprobación de pruebas | Núcleo, axiomas y declaración determinan qué se acredita | Política de axiomas y enunciados por revisar; no equiparar prueba formal a medición física |

Definir mecanismos con hipótesis rivales: si una consulta tarda más, examinar
cambio de fórmula, caché, scheduling, paginación y temperatura antes de afirmar causa.
Ni Bunge ni una correlación entre dos sensores aportan causalidad automáticamente.

## Configuración local disponible: evidencia limitada

Se leyeron, sin ejecutar, wsl/.wslconfig, wsl/wsl.conf y wsl/setup-zram.sh:
- .wslconfig propone memory=6GB, processors=2, swap=8GB.
- wsl.conf propone systemd=true.
- setup-zram.sh propone dispositivo2G, algoritmo lz4 y prioridad100.
Estos archivos son recetas del workspace, NO configuración observada del PC.
processors=2 no demuestra asignación de dos núcleos físicos ni acceso exclusivo.
Tamaño lógico2G de zram no equivale a ocupación física2G garantizada.
No ejecutar el script de configuración como si fuera una inspección de solo lectura.
Base histórica: docs/requirements/qa-inquisidor/environment-target.json,
usuario declaró hardware; no modificar ese documento para aparentar nueva medición.

## Perfil de evidencia y plan de caracterización

Cada registro: system_id, capa/componente/relación, nombre, valor/unidad, fuente,
clase epistémica, instante/ventana, método, revisión, incertidumbre y vigencia.
Identidad de entorno combina versiones/configuración identificadas y estado
observado en la ventana; un hash no representa temperatura/carga continuamente.

Orden propuesto: inventario de solo lectura del objetivo → confirmar configuración
host/guest y ubicación del proyecto → seleccionar telemetría disponible → acordar
presupuestos y parada → piloto pequeño → evidencia y contraste. No instalar
herramientas de sondeo ni requerir privilegios nuevos sin necesidad y autorización.
No se necesita forzar límites para empezar la caracterización.

READY documental del perfil no equivale a equipo apto ni ensayo aprobado.
Diseño puede avanzar con UNKNOWN explícitos; piloto físico exige resolver las
condiciones materiales que necesita, no todas las características irrelevantes.
La imposibilidad de observar el objetivo se declara NOT_RUN. No generar valores
sintéticos y etiquetarlos como mediciones.

## Pendientes materiales para seleccionar el primer ensayo

Versión/build Windows, WSL y Ubuntu; kernel y configuración efectiva; ruta del repo;
recursos disponibles y tareas compartidas durante la ventana; observabilidad
requerida, presupuesto y parada. Ambiente/refrigeración/sensores se detallarán
según el alcance térmico del ensayo. Temperatura máxima, plazo y memoria no se
adoptan de una ficha sin comprobar su aplicabilidad al criterio y medición.

Estado actual: perfil CESM parcial, target NOT_OBSERVED; formalización propuesta,
NO replica equivalence, NO hardware acceptance, NO CI ni cambios en el PC.
