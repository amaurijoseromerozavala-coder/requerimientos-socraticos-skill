# Arquitectura portable y detección del entorno

Estado: DRAFT. Decisión humana: «el sistema debe ser agnóstico al hardware pero
debe correr eficientemente en mi hardware entonces debe tener un proceso para
conocer en donde está alojado». La separación siguiente implementa esa decisión
solo en el diseño documental; no hay detector ni runtime nuevo instalado.

## Alcance y frontera CESM

El i3/8GB/WSL es objetivo de aceptación de eficiencia, no requisito de identidad
del equipo anfitrión. El sistema puede proponer ejecución en entornos soportados
mediante adaptadores. «Agnóstico» no significa compatible con cualquier máquina,
ISA, SO o dependencia sin verificar. Matriz de soporte real todavía pendiente.
Los perfiles CESM describen cada alojamiento observado; el documento CESM previo
sobre el PC es un perfil objetivo, no el esquema universal de todas las máquinas.
Las recetas wsl/ son específicas del objetivo, no configuración obligatoria global.

## Componentes y flujo propuestos

Núcleo semántico portable (IR/propiedades/trazabilidad) → contrato de capacidades.
Adaptadores de plataforma → perfil observado → política de recursos → plan fijado.
Ejecutor separado consume plan/autoridad; observador verifica condiciones necesarias.
No modificar significado, obligaciones o criterio de PASS según potencia disponible.

Estados: UNPROFILED → DISCOVERING → PROFILED/PARTIAL/UNSUPPORTED.
PROFILED + operación soportada + presupuesto y autorización suficientes → PLANNED.
PLANNED → RUNNING → COMPLETED/STOPPED/INCONCLUSIVE.
PARTIAL permite solo operaciones cuyos prerrequisitos sí estén establecidos;
UNSUPPORTED conserva informe y evita invocar herramientas incompatibles.
Si cambia una capacidad material, marcar PLAN_STALE y replantear antes de nuevo
trabajo; no prolongar ni aumentar recursos automáticamente. Transiciones no
especificadas no habilitan ejecución. FSM propuesta, no enforcement implementado.

## Descubrimiento inicial de bajo impacto

Inspección limitada de solo lectura, sin benchmark automático, escaneo de red,
secretos ni identificadores de hardware personales. No instalar herramientas,
elevar privilegios ni alterar host/WSL para completar un dato ausente.

| Dimensión | Observación útil y límite |
|---|---|
| Plataforma | SO/release, arquitectura, tamaño de palabra, runtime y versiones de herramientas; verificar compatibilidad de artefactos |
| Alojamiento | Indicios de nativo/WSL/VM/contenedor; múltiples capas posibles y UNKNOWN si no concluyente; no inferir proveedor por hostname |
| CPU efectiva | Afinidad, CPUs lógicas accesibles y cuota si existen; no confundir host total con capacidad asignada ni hilos con núcleos físicos |
| Memoria | Límites de proceso/contenedor/guest aplicables, memoria disponible y reservas; no sumar capacidades anidadas |
| Almacenamiento | Espacio disponible en rutas reales de datos/temporales, tipo de montaje cuando se conozca, permisos; no asumir SSD por rendimiento |
| Interfaz de ejecución | Capacidad de crear proceso, imponer límites admitidos y observar/recuperar recursos; no asumir supervisión tras muerte del coordinador |
| Telemetría material | Sensores/contadores accesibles, componente observado, unidad y antigüedad; no heredar temperatura del cloud al PC ni inventar sensores |
| Servicios | Capacidades remotas requeridas, contrato/versión y autorización; no enumerar credenciales ni llamar servicios solo para identificarlos |

Un perfil distingue capacidad nominal, límite configurado y disponibilidad dinámica.
Si varios límites de memoria aplican a la misma asignación, tomar el más restrictivo
con unidades normalizadas, manteniendo aparte consumo y reserva; no usar esa cifra
como memoria libre garantizada. Registrar límites ausentes/no aplicables/desconocidos.
No deducir presupuesto de trabajo únicamente de frecuencia, marca o RAM nominal.

## Contrato del perfil y selección determinista

Profile: schema_version, observed_at/window, platform, hosting_layers,
capabilities[], constraints[], sources[], missing[], supported_operations[].
Cada valor conserva tipo, unidad, alcance host/guest/proceso, método, confianza
justificada y frescura. Ausencia != cero ni ilimitado. Política y fuentes tienen
revisión. No guardar datos privados innecesarios en perfil, Engram ni logs.

Separar manifest estable (herramientas/configuración) y observaciones dinámicas
(memoria/carga/temperatura). El hash del manifest no acredita estabilidad continua.
Selección: función explícita de perfil congelado, operación y versión de política,
con prioridades y desempates definidos. Registrar razón del plan y capacidades
no utilizadas. Misma entrada/perfil/política → mismo plan; distinto alojamiento
puede generar otro plan sin cambiar semántica de las conclusiones.

Perfil objetivo económico inicial: un trabajador propuesto, modelos pequeños,
análisis simbólico antes de enumeración extensa y dependencias mínimas. No asumir
que más CPU/RAM autoriza más procesos o elimina límites humanos. Umbrales numéricos
aún pendientes de piloto, no convertidos en política por el detector.
No prometer mismo primer testigo, duración o completitud bajo timeouts en equipos
distintos. Fijar versiones, orden, parámetros y casos concretos para reproducir.

## Eficiencia, falsación y aceptación futura

Métricas por carga representativa: duración, memoria pico, escrituras/espacio,
trabajo completado, condiciones de parada y tiempo de reproducción. Registrar
presión del host y observabilidad suficiente. Sin umbral acordado no afirmar
«eficiencia comprobada»; mediciones del cloud no aceptan eficiencia en el i3.

Casos de contrato especificados NOT_RUN:
1. Entorno soportado distinto del i3: no se rechaza por identidad del CPU.
2. Guest limitado: el plan no usa la memoria total del host como disponible.
3. Memoria o sensor necesario desconocido: no se inventa valor favorable.
4. Cambio de cuota material: invalidar plan; no reescribir evidencia previa.
5. Mismo perfil/política/operación: misma selección de plan.
6. Arquitectura o herramienta incompatible: UNSUPPORTED explícito, no ejecución.
7. Perfil económico: no se omiten obligaciones para producir un PASS más barato.
8. Incumplimiento de presupuesto: detener según contrato y registrar límites,
   sin diagnosticar fallo de lógica automáticamente ni aumentar recursos sin permiso.

Falsador arquitectónico: decisiones centrales dependen del nombre del i3, un
perfil reduce alcance para aprobar, o UNKNOWN produce capacidad ficticia.
Dependencias y soporte deben probarse por plataforma antes de declarar portabilidad.

## Estado y próximos pasos

Fijar contrato de capacidades y primer adaptador del entorno disponible;
definir piloto/umbrales representativos del i3 y comprobar plan/ejecutor/observador
por separado. No exigir inventario exhaustivo del universo para empezar.
Núcleo Lean/Python/Z3 sigue propuesto, no instalación; CI permanece diferido.
Este documento precisa el alcance general del sistema sin borrar perfil CESM
objetivo ni resultados históricos. Revisión RDD documental no acredita detector,
portabilidad ni eficiencia física: esas propiedades requieren evidencia futura.
