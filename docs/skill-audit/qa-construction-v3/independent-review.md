# Revisión independiente local de QA Inquisidor 0.1

Revisor real: `/root/qa_requirements_resume`; coordinador: `/root`.
Alcance: instrucciones, criterios, esquema, validador y suite de QA, contrastados
con Q-QA-006–008 y contrato-evidencia.json. No se editó la implementación.
No se ejecutaron comandos de aplicación, red, cargas ni ensayos de hardware.

## Ejecución observada

`timeout 40 /home/agent/.local/share/requerimientos-socraticos/venv/bin/python -B -m unittest discover -s skills/qa-inquisidor/tests -v`

Resultado: exit0, 36 tests OK, 0.137s según unittest. El proceso de revisión
independiente ejecutó la suite; el resultado no se dedujo de logs del coordinador.
Los casos comprueban rechazo de entradas, hashes locales, referencias, resultados
y lectura de archivos pequeños propios. No certifican un sistema objetivo.

Tras autorización del coordinador para explorar concerns específicos, tres
probes mínimos sobre la fixture de la propia suite confirmaron los hallazgos.
Se ejecutaron con plazo exterior de 10s, sin concurrencia/carga, con limpieza de
los archivos temporales propios. No modificaron fuentes ni datos reales.

## Hallazgos

**F1 — alta: juicio sin binding al assessment y conjuntos evaluados.**
`scripts/validate_report.py:119` calcula vigencia comparando cinco strings de
contexto y secuencias. El schema `judgment` no incluye assessment_id,
judgment_id, actor_runtime ni digest de inventario/casos/oráculos/evidencias,
aunque Q-QA-008/K4/contrato proponen esos vínculos. Cambiar solo assessment_id
de la fixture preserva `RECORD_CURRENT_SUCCESS` y `delegation_current=true`
sin emitir otro juicio. No se pide autenticar humanos: falta incluso la
correspondencia de los registros que el contrato promete. Recomendación:
binding explícito al assessment y digest determinista de conjuntos efectivamente
evaluados; cambios deben invalidar el juicio antes de proponer éxito.

**F2 — media: GAP agregado con material_gap=false.**
`scripts/validate_report.py:126` limita `has_gap` a obligaciones/no vacío; las
condiciones de juicio/autoridad en línea129 no se incluyen en la salida
material_gap. Probe: fixture intacta salvo judgment.scope=PENDING produce
`RECORD_GAP_OR_STALE`, `material_gap=false`, `gaps=[]`. Contradice fsm_bridge
de contrato-evidencia.json, donde GAP establece material_gap=true, y puede
confundir a un consumidor que examine esa bandera. Recomendación: conservar
gaps de obligaciones separados y calcular pendiente agregado con juicio/autoridad.

**F3 — media: casos pendientes sin motivo específico.**
`assets/report.schema.json:229` define casos sin razón de NOT_RUN/UNKNOWN/STALE,
aunque SKILL.md exige motivo. Probe NOT_RUN sin evidencia y sin razón por caso
devuelve document_validation=VALID. El rationale de obligación no documenta
por qué un caso no se ejecutó o quedó obsoleto. Recomendación: exigir motivo
no vacío al menos para esos estados y conservarlo en informe.

## Correspondencia y límites

FAIL con otra obligación NOT_RUN se cubre por prueba ejecutada y conserva gap.
Duplicados, referencias huérfanas, contradicción PASS/FAIL, evidencia de tipo
incorrecto, UNKNOWN de aplicabilidad/materialidad y N/A de obligación requerida
tienen controles reales en la suite. No se encontraron otros defectos probados
en ese alcance. Los tres hallazgos anteriores no quedan resueltos por esos PASS.

Dictamen: corregir F1–F3 y repetir regresiones antes de congelar candidato RDD.
No declarar PRD global COMPLETE, ni PASS del sistema, ni calibración física.
La suite y los probes solo aportan evidencia local de implementación documental.
