# Investigación y propuestas de diseño

Para una duda concreta, descubre MCP y skills pertinentes primero. Lee los
contratos seleccionados y consulta evidencia: Engram es historia; CodeGraph es
topología actual si hay código e índice; Context7 es documentación de APIs y
librerías materiales. Registra ausencia y fallback, no invocaciones ficticias.

Explora la web para las dudas arquitectónicas del ciclo con búsquedas dirigidas
y lectura de fuentes primarias. Conserva consulta, URL, fecha, afirmación y
recibo real. Un resultado de búsqueda no equivale a haber leído la fuente.
No envíes secretos ni datos personales. Si falta una fuente necesaria, conserva
UNKNOWN/BLOCKED. Evidencia local de hash vigente se puede reutilizar con razón.

Cada mejora de diseño debe contener problema, baseline y alternativa, criterios
medibles, restricciones, evidencia, tradeoffs, hipótesis y falsador. Registra
PROPOSED, EVIDENCE_PENDING, ACCEPTED o REJECTED. El silencio, la respuesta del
asistente o RDD no aceptan una política de negocio. No implementes propuestas.
Una recomendación puede ser conservar el diseño si los criterios lo justifican.

Entrega design-proposals.json. Si no hay mejora justificada, registra razón y
evidencia; no inventes un defecto por cuota. Nunca proclames la mejor arquitectura
fuera de criterios definidos ni propongas librerías sin evaluar recursos y contratos.

## Fuentes primarias consultadas

- NASA, Technical Requirements Definition: expectativas, supuestos y criterios
  verificables. https://www.nasa.gov/reference/4-2-technical-requirements-definition/
- CMU SEI, ATAM: Method for Architecture Evaluation, CMU/SEI-2000-TR-004:
  atributos de calidad y tradeoffs.
  https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/

Consultadas 2026-10-26. Son fundamento metodológico, no evidencia de una
tecnología concreta ni autorización sobre políticas de un proyecto.

`requirement_or_topic_ids` admite IDs de topics y requisitos del PRD. Para
resolver referencias a requisitos usa `validate_prd.py`, que aporta su catálogo;
`validate_interview.py --design` aislado solo conoce los topics de la entrevista.
