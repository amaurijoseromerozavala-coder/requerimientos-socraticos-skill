# WU-RS3-PROPOSAL-BINDING-003

## Fuente y precedencia

RS3-REQ-036, RS3-REQ-041 y RS3-REQ-047 del paquete propuesto, junto con la
regla vigente de no conceder autoridad al LLM. Requiere CandidateIR provisional
existente. La fuente no convierte el paquete en PRD ratificado.

## Alcance

Añadir un digest canónico de la propuesta admitida completa, incluyendo
referencia, texto, modalidad, dirección, contexto y estado. Propagarlo al
borrador EARS. Conservar `source_sha256` como hash del texto literal por
compatibilidad y mantener `authority=NOT_GRANTED`.

## Oráculo TDD congelado

RED: cambiar únicamente `source_ref`, `condition`, `modality`, `assumptions` o
`exceptions` debe cambiar `proposal_sha256`; el borrador EARS debe repetir el
digest del IR para exactamente la misma propuesta. Antes de implementar, el
campo está ausente. Observado: dos `KeyError: proposal_sha256` en las pruebas
CandidateIR y EARS antes de modificar el código.

GREEN: digest SHA-256 de JSON UTF-8 ordenado, sin espacios y sin normalizar el
texto; entradas inválidas siguen rechazadas. Regresiones: CandidateIR, EARS,
suite Requerimientos Socráticos y CI afectado. RDD exacto y respaldo Git.
Observado: 316 pruebas de Requerimientos Socráticos y 51 de CI pasaron; la
única omisión CI es el caso que requiere el ZIP externo.

## Riesgos y límites

Un digest identifica bytes, no certifica intención humana, procedencia real,
semántica ni permiso. No se crea una firma, credencial o gate de confirmación.
La migración a un IR canónico confirmado permanece fuera de esta unidad.
