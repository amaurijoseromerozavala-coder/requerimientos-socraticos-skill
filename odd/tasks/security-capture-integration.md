# WU-SEC-CAPTURE-INTEGRATION-001 — unificación local de rutas de captura

## Objetivo y frontera

Integrar el saneador de recibos públicos y la captura de suites CI sobre la
ruta durable del supervisor ya revisada. La implementación común de
`supervisor.safe_capture` debe incluir los controles para copias numéricas y
marcadores JSON precedidos por texto. Esta unidad no sanea recibos históricos,
no cambia el remoto ni afirma revocación de valores publicados.

## Oráculos ODD → TDD → RDD

1. RED: la base no ofrece el capturador de suites CI. Un control de integración
   con valor exclusivamente ficticio debe fallar antes de aplicar la unidad.
2. GREEN: los controles de CI, supervisor y saneador público pasan juntos;
   los casos no saneables no producen archivos ni salida cruda. Las claves JSON
   duplicadas se inspeccionan todas y los delimitadores ambiguos se rechazan.
   El chequeo de publicación cubre recibos y exports, no fixtures de código.
3. La suite completa y `git diff --check` pasan. Los límites de tamaño y
   plazo permanecen acotados; ningún proceso de carga artificial se ejecuta.
4. Gentle AI revisa la identidad exacta integrada y reconoce el recibo antes
   del commit local. No hay push ni reescritura histórica en esta unidad.
