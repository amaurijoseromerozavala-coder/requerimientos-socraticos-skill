# Sondeo, capacidad estimada y cobertura acreditada

Estado DRAFT. Requisito humano: «Debe hacer un sondeo y calcular la capacidad de
hardware para tener un valor de cobertura». Se separan las magnitudes para no
derivar un porcentaje lógico solamente de GHz/RAM. Sin detector implementado,
sondeo del objetivo ni calibración ejecutados.

## Contrato propuesto

1. Sondeo inicial limitado de lectura: plataforma/versiones, afinidad/cuotas,
límites efectivos y disponibilidad de memoria, rutas/espacio de trabajo y
telemetría necesaria. Usar adaptadores del perfil portable; no descubrir secretos
ni sondear redes o dispositivos ajenos. UNKNOWN si el dato no puede observarse.
2. Presupuesto explícito de recursos y parada, confirmado para el ensayo.
3. Calibración autorizada pequeña con cargas representativas y versiones fijadas;
observar consumo y resultado, sin saturar ni crecer hasta colapso. Reutilizar
mecanismos y autorización suficientemente cubiertos, no pedir permiso redundante.
4. Estimación de capacidad por clase de problema y método, con incertidumbre.
5. Selección reproducible del plan y ejecución según presupuesto.
6. Medición de cobertura real, regiones pendientes y validez del resultado.

Capacidad es vector: tiempo de trabajo disponible, memoria/presión, espacio/I/O,
capacidad de supervisión y estado material relevante. No es un único score.
Concurrencia efectiva no se deduce del número de CPUs nominales; una cuota puede
limitar tiempo CPU aunque la afinidad incluya varias CPUs.

## Instrumentación candidata

psutil: observaciones multiplataforma de CPU/memoria/proceso/disco, BSD-3-Clause
según licencia del proyecto. Sus datos se complementan con límites/capacidades
de plataforma: no tratar virtual_memory como presupuesto infalible de contenedor
ni leer todos los campos/procesos indiscriminadamente. No instalar ahora.
Linux PSI, si está disponible, indica presión CPU/memoria/I/O; no mide por sí
solo temperatura ni todos los requisitos del entorno. WSL puede limitar visibilidad.
Un dato del huésped no se atribuye al host físico sin justificación.
Fuentes primarias abiertas:
https://psutil.io/api/
https://github.com/giampaolo/psutil/blob/master/LICENSE
https://www.kernel.org/doc/html/latest/accounting/psi.html

## Estimar coste sin prometer cobertura

El piloto registra clase de fórmulas, variables, restricciones, densidad/tamaño,
método, versiones, muestras/duración, memoria pico y estado del host.
Proyectar solo dentro de un rango y una clase justificados; casos pequeños no
predicen el peor caso exponencial de SAT/SMT/ROBDD ni coste de una prueba Lean.
Cuando no existe fundamento, coste UNKNOWN y plan conservador.
En enumeración secuencial, RAM no limita directamente el número TOTAL de casos:
pueden procesarse en flujo. Limita estado concurrente, tablas almacenadas y caches.
Evitar fórmulas ingenuas del tipo RAM/bytes_caso como máximo universal de cobertura.

Un ritmo medido puede estimar cuántos casos se procesarían en un presupuesto
similar; se etiqueta ESTIMATED con condiciones. La cobertura lograda se calcula
separadamente después, sin convertir proyección de rendimiento en resultado.

## Definición explícita de cobertura

Para una propiedad p, fijar U_p: universo aplicable y factible bajo dominio y
revisión confirmados. V_p: casos/regiones de U_p para los que se acreditó el
resultado de esa propiedad mediante método declarado. La medida debe ser:
C_p = |V_p| / |U_p|, SOLO si los conteos son exactos y U_p no es vacío.

Sin restricciones, n booleanos admiten 2^n asignaciones; con n=32 son
4.294.967.296. Con restricciones, contar exactamente lo factible es otra tarea
que puede ser costosa; SAT aislado no calcula ese denominador.
Si el conteo no está disponible, reportar UNKNOWN o límites demostrados del
porcentaje, junto con casos verificados y regiones pendientes. Un dominio vacío
es MODEL_INVALID/NOT_APPLICABLE con causa, no cobertura100% por dividir entre cero.
No usar solo casos intentados como denominador ni reducir U_p al vencer tiempo.
Casos duplicados no incrementan cobertura; regiones solapadas no se suman dos veces.
Una exclusión requiere restricción aplicable justificada; UNKNOWN del solver no
se convierte en región imposible. Universo no cuenta estados inalcanzables como
excluidos sin justificación para el alcance temporal.

Mantener medidas distintas:
- Cobertura de requisitos: obligaciones con evidencia adecuada / aplicables.
- Cobertura combinatoria: asignaciones/regiones por propiedad y universo fijo.
- Cobertura temporal: estados/transiciones/trazas según modelo y profundidad.
- MC/DC: obligaciones de independencia de condiciones, con variante y factibilidad.
- Ejecución real: casos realmente ensayados, entorno y oráculo.

No sumar ni promediar automáticamente esas medidas como un porcentaje universal.
En análisis simbólico una prueba válida puede cubrir toda U_p para UNA propiedad
sin ejecutar todas las asignaciones. Registrar alcance y método de acreditación;
no llamarlo cobertura física ni cumplimiento completo de DO-178C. Un resultado
UNSAT en una consulta insuficiente no acredita esa cobertura. Una prueba de
seguridad no acredita progreso ni coste del hardware.

## Salida propuesta, sin cifras ficticias

profile_ref, workload_ref, domain_revision, property_id, method,
resource_budget_ref, capacity_estimate/value/unit/conditions,
coverage/universe_kind/denominator/value/status, verified_regions,
unresolved_regions, execution_receipts, assumptions y limitations.
Hasta medir el PC: capacity=UNKNOWN, coverage_empirical=NOT_RUN.
Un timeout puede dejar evidencia útil de regiones previamente verificadas, pero
el veredicto global del alcance pendiente será INCONCLUSIVE si corresponde.
No convertir «hardware débil» en aprobación con menos requisitos.

## Falsadores documentales especificados NOT_RUN

F1: informe afirma cobertura basándose solo en RAM/GHz → rechazar.
F2: cuenta de nuevo casos duplicados o regiones solapadas → rechazar numerador.
F3: dominio factible sin conteo exacto recibe porcentaje exacto sin prueba → rechazar.
F4: cambia universo al agotar tiempo para presentar100% → invalidar conclusión.
F5: calibración extrapola a fórmulas no comparables sin incertidumbre → UNKNOWN.
F6: cobertura formal de p se presenta como ensayos físicos o MC/DC → rechazar.

Aplicar Bunge/Popper: perfil es observación con límites, proyección es hipótesis,
porcentaje exige definición y evidencia; resultado contrario reabre el modelo.
Presupuestos, primer caso y unidad de límite32 aún necesitan detalle de diseño.
No sondear cloud y afirmar que es PC del usuario; CI e instalación siguen diferidos.
