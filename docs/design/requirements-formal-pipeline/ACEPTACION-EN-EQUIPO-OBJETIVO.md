# Primer objetivo material de aceptación

Estado: DRAFT; diseño y plan, no implementación ni ensayo nuevo.
Fuente humana: «lo diseñaremos para que corra sin conflicto en mi hardware el reto
es hacerlo investigando para que no colapse y esa será la prueba de que la
planificación y el proceso funciona».

## Significado operativo propuesto

Hardware agnóstico; primer objetivo de aceptación es el PC i3/8GB/WSL declarado.
«Sin conflicto/no colapse» se descompone en propiedades observables, no en una
garantía absoluta ni obligación de terminar cualquier problema matemático:
- Resolver una carga representativa acordada dentro de presupuesto.
- Conservar las obligaciones y exactitud del resultado, sin reducir alcance.
- Si falta capacidad o vence presupuesto, devolver INCONCLUSIVE/RESOURCE_LIMIT,
  detener trabajo propio y recuperar recursos conforme al contrato.
- No modificar configuración del equipo ni afectar datos ajenos al ensayo.
- Mantener capacidad de interacción del host según métrica/criterio por acordar.
  CPU/RAM bajos por sí solos no demuestran que el host siga respondiendo.

Una finalización controlada por límite prueba solo ese control, no eficiencia ni
finalización satisfactoria de la carga representativa. Ausencia de cuelgue en un
ensayo aporta evidencia acotada; no demuestra todos los escenarios ni toda la
metodología. Una parada de hardware no se usa como criterio deseable de falsación.

## Investigación de contención y supervisión

Fuentes primarias consultadas: Linux kernel, Control Group v2
https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
Microsoft, Job Objects
https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects

Son mecanismos candidatos del adaptador, no un cambio instalado: Linux permite
controles jerárquicos de recursos; Windows permite agrupar procesos y aplicar
límites. Hay que verificar capacidad/delegación efectiva y descendientes, no
asumir permisos por detectar la plataforma. No gestionar procesos ajenos.
Distinguir límite de advertencia/presión de límite máximo, tiempo CPU de tiempo
transcurrido, y memoria comprometida de memoria residente. Una cuota observada
no demuestra aislamiento completo ni ausencia de impacto en infraestructura.
Para WSL, configuración del guest no sustituye observación y presupuesto del host.

Preferir supervisor exterior a la tarea acotada, con contrato sobre plazo,
cierre, descendientes y limpieza. Si no puede acreditarse esa capacidad para
un ensayo que la necesita, bloquear ese ensayo; no habilitar límites aparentes.
Nunca quitar protecciones del SO/firmware ni elevar privilegios automáticamente.

## Secuencia de aceptación propuesta

1. Completar solo los datos CESM materiales al primer caso; inspección de lectura.
2. Definir carga y oráculos antes de observar: tabla pequeña y propiedad formal,
   entradas identificadas y criterio de finalización/respuesta correcta.
3. Acordar memoria, plazo, concurrencia, I/O y condiciones de parada/reanudación
   con fuentes y observabilidad aplicables. Ningún umbral se inventa aquí.
4. Verificar primero instrumentos con cargas pequeñas y temporales. Casos de
   límite se inducen mediante un presupuesto pequeño controlado o sustituto
   observable, no llenando RAM/SSD ni sobrecalentando el equipo. Un sustituto
   no acredita aislamiento real del SO; ese caso queda pendiente hasta comprobarlo.
5. Ejecutar secuencialmente el piloto autorizado; observar tarea y host, preservar
   trazas. No aumentar tamaño automáticamente hasta un colapso.
6. Repetir con versiones/entradas/perfil identificados y documentar variación.
   Reproducción independiente se registra por separado de RDD documental.

## Resultados de aceptación por dimensión

| Dimensión | Evidencia futura requerida | Estado actual |
|---|---|---|
| Corrección lógica | Tabla/solver/propiedad concuerdan en alcance y oráculos | NOT_RUN |
| Terminación útil | Carga representativa termina con resultado justificado | NOT_RUN |
| Uso de recursos | Mediciones del PC dentro del presupuesto acordado | NOT_RUN |
| Comportamiento bajo límite | Resultado explícito y recuperación de recursos propios | NOT_RUN |
| Entorno | Host observado satisface criterio acordado durante la ventana | NOT_RUN |
| Reproducibilidad | Repeticiones registradas y diferencias explicadas | NOT_RUN |

No condensar esas dimensiones en PASS porque una sola salió favorable.
Hipótesis bungeana: los mecanismos y particiones propuestos permiten la carga
bajo condiciones definidas. Falsación: resultado contrario fiable bajo esas
condiciones obliga a revisar planificación, instrumentos, modelo o implementación;
no atribuye automáticamente una causa única ni autoriza ensayos de mayor impacto.

Pendientes: acceso al equipo objetivo, baseline de versiones/capacidades,
carga representativa, presupuesto y métricas de host. Ya existe autorización
humana de ensayos delimitados; no pedirla de nuevo para la misma operación
suficientemente cubierta. Autorizar ensayos no habilita instalar QA, CI ni producción.
