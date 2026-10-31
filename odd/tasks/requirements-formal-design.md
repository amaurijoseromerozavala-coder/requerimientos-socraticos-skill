# Propuesta de diseño de formalización de requisitos

## Specs
Usuario solicita investigación profunda de librerías, tecnologías, estructuras,
arquitectura y lenguajes open source para natural→EARS→lógica→combinaciones→
interrogatorio→ensayos trazables y tratamiento de issues.
Solo investigación y propuesta; no instalación ni implementación, CI diferido.

## Tasks
- D1 investigar documentación y licencias primarias; MCP Context7 y web.
- D2 diseñar representación tipada, consultas y oráculos independientes.
- D3 revisión arquitectónica acotada y RDD documental nativo.

## Log
Inicio: contratos de arquitectura, PERT y referencias locales de requisitos leídos.
Dos referencias cloud de arquitectura no se pudieron leer; no se atribuyen gates
completos ni cierre READY. No índice CodeGraph; no instalación de infraestructura.

Investigación completada: fuentes primarias para Python, JSON Schema, Z3, pytest, Hypothesis, Lark, TLC, cvc5, pySMT, Alloy y NASA FRET. Una revisión arquitectónica real detectó 3 precisiones, incorporadas; ejemplos NOT_RUN. No instalaciones, ensayos de rendimiento ni implementación.

RDD review-7fefdd36c985b71b approved/acknowledged sin findings de fiabilidad documental. Propuesta PROPOSED; comparación de 4 documentos con árbol revisado sin diferencias. Export completo exports/propuesta-requisitos-formales-completa.json. Sin instalaciones ni implementación.

Método solicitado explícitamente por humano: Bunge y Popper operacionales. Addendum METODO-CONTRASTE.md separa normativa, definiciones, deducción, hipótesis empírica y observación; matriz NOT_RUN y desconocidos preservados. Límite32 confirmado en variables, unidad aún no decidida; DO-178C confirmado sin equivalencia de cobertura demostrada.

Addendum metodológico: cierre RDD review-fa2926b3c17d2750 approved/acknowledged por ruta automática low risk, sin lentes ni revisor independiente. No acredita gate estricto independiente ni ensayos; propuesta DRAFT.

Filtro solicitado de fundamentos incorporado en FILTRO-FUNDAMENTOS.md: lógica/matemáticas, física aplicable, dominio y hardware, sin promover restricciones empíricas a axiomas incuestionables. Invariantes requieren inicialización/preservación; inducción fallida no siempre implica traza alcanzable. Sin consultas/ensayos nuevos.

RDD review-eb51da084be0197f closed approved/acknowledged por ruta low-risk documental sin lentes; NO revisión independiente ni ensayos nuevos.

Interacción térmica solicitada: ENVOLVENTE-TERMICA.md, fuentes Intel/kernel/Microsoft; distingue nominal/configurado/observado, sensores y presupuestos pendientes. Sin mediciones ni cambios de host.

RDD review-6b91084af3557c74 cierre automático low-risk sin lentes; acknowledged. Telemetría y presupuestos físicos NOT_RUN/pendientes, sin revisión independiente.

Perfil CESM material solicitado: CESM-ENTORNO-MATERIAL.md distingue S-FIS, S-VER y S-CLOUD; composición/entorno/estructura/mecanismos, inventario declarado y UNKNOWN. Configs WSL locales leídas como recetas, no mediciones. Sin ejecución/configuración del PC.

RDD review-18f271eef43839c4 approved/acknowledged por ruta documental sin lentes. Perfil parcial, no observación física. Export cesm-entorno-material.json.

Aclaración humana: hardware agnóstico, eficiente en su equipo y con proceso para conocer alojamiento. PORTABILIDAD-Y-DETECCION.md distingue núcleo portable, adaptadores/perfil de capacidades, política/plan/ejecutor/observación; i3 es objetivo aceptación, no identidad obligatoria. Ensayos NOT_RUN y umbrales pendientes.

RDD review-3ca4573f265ab260 approved/acknowledged por ruta low-risk sin lentes; no revisión independiente ni ejecución.

Objetivo material explícito: operar eficientemente y sin colapso en PC declarado. ACEPTACION-EN-EQUIPO-OBJETIVO.md separa corrección, terminación útil, recursos, recuperación y host. Fuentes de mecanismos kernel/Windows consultadas; sin instalar ni ensayar. Falta baseline/carga/presupuestos para aceptación física.

RDD review-37d9ab6ef04fa197 closed/acknowledged low risk, sin revisión independiente. Aceptación física pendiente.

Sondeo/capacidad/cobertura solicitado: SONDEO-CAPACIDAD-COBERTURA.md separa inventario, calibración acotada y cobertura por propiedad/universo; sin inferir porcentaje de GHz/RAM. Fuentes psutil/PSI consultadas, herramientas no instaladas, PC NOT_RUN.

RDD review-0080894a853ac035 cierre documental automático, acknowledged, sin lentes ni ensayos. Capacidad del PC UNKNOWN y cobertura empírica NOT_RUN.
