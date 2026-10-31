# Envolvente térmica y de recursos

Estado: PROPOSED / DRAFT. Extensión del filtro de fundamentos. Sin mediciones ni
ensayos nuevos. Petición humana: «Tomar en cuenta la termodinámica y si interaccion
para los límites fijos y funcionamiento del cpu ram disco etc».
Interpretación operacional propuesta: considerar interacción entre energía, calor,
recursos y rendimiento; no fijar cifras físicas sin fuente y medición aplicable.

## Límites de distinta naturaleza

- Fabricante: especificaciones de cada componente y condiciones de medición.
  TDP no es consumo máximo instantáneo ni presupuesto total del equipo. Una
  temperatura Tcase no se interpreta como temperatura de núcleo/Tjunction.
- Configuración: memoria/procesadores/swap de WSL. No garantiza recursos libres
  ni exclusividad del host ni configura por sí sola un límite térmico del hardware.
- Presupuesto de ensayo: memoria, plazo, concurrencia y escrituras acordadas,
  con condiciones de parada. No derivarlo automáticamente del máximo nominal.
- Estado dinámico: temperatura, presión de memoria, frecuencia efectiva, carga
  del host, latencia de disco y refrigeración disponible. Requiere observación.

El objetivo declarado continúa i3-3240, RAM8GB, WSL6GB, zram2GB y swap8GB;
no son observaciones del hardware presente en el cloud. Modelo/revisión de SSD,
RAM, refrigeración, firmware, salud y sensores no comprobados.

## Modelo causal a contrastar

Esquema térmico simplificado: C_eff*dT/dt = P_generada - Q_disipada.
C_eff en J/K, potencias en W; modelo de capacidad concentrada, no simulación
calibrada de este equipo. Requiere condiciones de ambiente, disipador/ventilación
y acoplamiento entre componentes. No usarlo para predecir temperatura real sin
identificar parámetros y comprobar validez.

- CPU: trabajo produce calor; controles térmicos pueden reducir frecuencia.
  Frecuencia nominal no determina tiempo fijo de Lean/Z3 ni plazo garantizado.
- RAM/zram: presión de memoria puede aumentar compresión, fallos de página y
  movimiento de datos. Zram ocupa RAM y trabajo CPU, no suma capacidad física.
- Swap/disco: paginación puede añadir I/O, latencia, energía y escrituras.
  No afirmar saturación, corrupción o desgaste concreto sin mediciones y ficha.
- SSD: temperaturas y comportamiento bajo carga dependen del modelo/firmware;
  no inferir caché, resistencia de escritura o umbral del SWR256G-N01I por nombre.
- Host Windows/WSL: comparten recursos físicos. CPU y RAM de otros procesos
  afectan disponibilidad; sensores del huésped pueden faltar o no representar
  el dispositivo físico. Comprobar origen y acceso autorizado en el host.

## Datos antes del piloto físico

Inventario/fuente de especificaciones, condiciones ambientales relevantes,
sensores con componente/localización/unidad, cadencia y antigüedad de muestras,
frecuencia efectiva, memoria disponible/presión, actividad swap e I/O y espacio.
Recoger únicamente telemetría necesaria y permitida, sin datos personales.
Ausencia de sensor = UNKNOWN, nunca temperatura cero ni condición favorable.
No exigir sensor irrelevante para una tarea documental; para ensayo que necesita
ese dato, dejar pendiente o usar una alternativa menos exigente justificada.

## Guardas propuestas y estados de trabajo

Estados propuestos: PRECHECK, RUNNING, PAUSED_RESOURCE, STOPPED_LIMIT,
COMPLETED, INCONCLUSIVE. No son estados ya implementados de Gentle AI.
PRECHECK exige presupuesto, condiciones y observación suficientes para el ensayo.
RUNNING debe detener trabajo nuevo al detectar incumplimiento del criterio
acordado o pérdida de observación necesaria. PAUSED_RESOURCE solo reanuda tras
criterio explícito, no por tiempo arbitrario; conservar trazas y autorización.
Establecer histéresis/ventana cuando corresponda para evitar oscilaciones,
sin inventar cifras. STOPPED_LIMIT no significa fallo del requisito de negocio.

Invariante del controlador propuesto: no admitir una unidad de trabajo cuando
la evidencia requerida es desconocida/obsoleta o contradice la envolvente acordada.
Su alcance son decisiones del controlador con muestras válidas; NO demuestra
que la temperatura real nunca excedió un umbral entre muestras. Actuación y
telemetría tienen demora; el margen necesita calibración y criterio de ingeniería.
No reemplazar ni alterar protecciones térmicas del SO/firmware/hardware.
No fijar ni modificar voltajes, frecuencias, ventiladores o políticas del host.

## Bunge, Popper y determinismo

Hipótesis empírica: un caso representativo cabe en la envolvente definida.
Predicción: termina dentro de presupuesto sin activación de parada acordada.
Falsador: registro fiable muestra exceso o parada bajo esas mismas condiciones.
Si falta medición, INCONCLUSIVE; no extrapolar del cloud al equipo físico.
No confundir incumplimiento de presupuesto con prueba automática de daño físico.
La prueba formal solo acredita las reglas abstractas; medir acredita condiciones
materiales bajo el ensayo. Resultados lógicos deben distinguirse de duración:
calor/scheduling pueden cambiar tiempos y provocar timeout sin cambiar la lógica.
Guardar versión/entradas y trazas; no exigir duración idéntica para repetibilidad.

## Diseño inicial y fuentes

Un trabajador, casos pequeños, límites explícitos y terminación/limpieza verificadas;
presupuestos numéricos y margen térmico aún pendientes. No depender de swap para
la carga normal ni inducir saturación para caracterizar el primer piloto.
No alterar documentos anteriormente revisados ni prometer seguridad física universal.

Fuentes primarias consultadas por MCP web:
- Linux kernel, Intel thermal throttle events reporting:
  https://www.kernel.org/doc/html/latest/admin-guide/thermal/intel_thermal_throttle.html
  Documenta reducción adaptativa de consumo y eventos de throttling. Su soporte
  en un Linux físico no demuestra disponibilidad dentro de WSL o en este procesador.
- Microsoft, Advanced settings configuration in WSL:
  https://learn.microsoft.com/en-us/windows/wsl/wsl-config
  Distingue configuración de memoria/procesadores/swap de WSL2.
- Intel, ficha i3-3240 SKU65690, abierta en fuente primaria:
  https://www.intel.com.br/content/www/br/pt/products/sku/65690/intel-core-i33240-processor-3m-cache-3-40-ghz/specifications.html
  No se convierte su cifra Tcase en umbral de sensor de núcleo ni de ensayo.

Estado de contraste: NOT_RUN. RDD documental no acredita sensores, prestaciones,
compatibilidad ni envolvente física. CI diferido, producción bloqueada.
