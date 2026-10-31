# Contraste del output QA y ensayos autorizados

Estado: análisis y ensayos locales acotados completados en el alcance descrito.
No implica READY de QA, instalación, CI ni comprobación del equipo físico.

## Autoridad

El humano autorizó «los ensayos». Se aplica a comprobaciones locales delimitadas,
no convierte los mandatos del output QA en instrucciones aceptadas ni cambia
el default de la futura skill: análisis y ejecución con autorización específica.

## Resultados observados

- Suite scratch: 12 comprobaciones OK; evidencia scratch-tests.log.
- Suite sealed: 23 comprobaciones OK; evidencia sealed-tests.log.
- Fixture temporal de ocho bytes: read_regular devuelve el contenido actual,
  aunque difiera del digest tomado antes de reemplazarlo. Evidencia
  bounded-observation.json. Limpieza por TemporaryDirectory.
- Resultado histórico separado: supervised-check/results.json registra timeout
  de consumidor sintético en 0.502s para presupuesto 0.5s, hijo terminado y
  siguiente validación favorable. No se presenta como ensayo nuevo de esta ronda.

Las suites usan procesos propios y temporales; no se inducen cargas intensivas.
No se construyen entradas de evaluación costosa ni se agotan los cuatro slots
con consumidores indefinidos. No se prueba el equipo i3/WSL ni presión de memoria.

## Adjudicación de afirmaciones

1. Ciclo de vida: LIMITACIÓN REAL ACOTADA. El timeout del consumidor existe
   mientras vive el coordinador. La herencia de lease protege datos del consumidor
   vivo después de terminar el padre, comportamiento comprobado por test existente.
   Sin supervisor independiente no hay plazo global demostrado tras esa terminación.
   No se demostró una entrada real que bloquee indefinidamente validate_prd;
   ni que sean necesarios reinicio, agotamiento permanente o daño al equipo.
   El resultado SCRATCH_BUSY con ocupación activa es rechazo por capacidad,
   no demuestra por sí solo un interbloqueo. Recuperación al salir el consumidor
   está cubierta; no equivaler ocupación prolongada a estado irrecuperable.

2. Correspondencia de bytes: LIMITACIÓN REAL DE FRONTERA. La extracción es
   mutable por procesos de la misma cuenta; el código declara esa cuenta/kernel/
   motor como confiables. read_regular no verifica por sí solo un hash esperado.
   El fixture confirma eso, no una certificación favorable completa de PRD alterado.
   La afirmación de que utimensat restaura arbitrariamente ctime es incorrecta:
   ajusta atime/mtime; esto no convierte la heurística en garantía de lectura atómica.
   Pasar datos en memoria podría reducir ventanas de archivos, pero no demuestra
   aislamiento absoluto de procesos con la misma autoridad ni elimina toda carrera.

3. FSM: PARADOJA REFUTADA. REPORT_DELIVERED significa informe entregado y no
   exige PASS. Una obligación física pendiente impide PASS del alcance que la
   incluye, sin impedir entregar un informe útil. Análisis favorable de propiedades
   estáticas no acredita hardware. La autorización reciente permite ensayos
   delimitados; no aporta evidencia física ni garantiza que se realizarán todos.
   Un pendiente puede resolverse luego: «perpetuamente» no está justificado.

## Propuestas que requieren diseño, no implementación automática

- Delimitar contrato de supervisión y recuperación si se exige plazo aun con
  terminación del coordinador; comparar señal de terminación ligada al padre,
  supervisor externo y ejecución sin consumidor separado. Una señal Linux tiene
  condiciones de registro y carrera de inicio; no prueba por sí sola garantía global.
- Definir lectura de contenido identificado sin scratch como alternativa, con
  límites, referencias cruzadas y comprobaciones propias; no declarar aislamiento
  absoluto por usar pipes.
- Mantener separación alcance/veredicto/entrega y autoridad humana verificable.

No se modificó implementación de skills. RDD de estos documentos nuevos pendiente;
recibos anteriores no cubren este candidato. G1-SPEC continúa parcial; falta contrato
canónico de tipos/correspondencias y autoridad de valoración semántica.
