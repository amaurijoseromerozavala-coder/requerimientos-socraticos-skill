# Revisión independiente de la retención corregida

Fecha: 2026-10-30. Agente: `review_supervisor_followup`.
Alcance: coherencia documental de la decisión de conservar stdout/stderr,
capacidad de 32 MiB y borrado Manual, comunicada por el coordinador y preservada
en retention-change.json. Sin implementación ni edición de documentos normativos.

## Resultado

Sin hallazgos bloqueantes pendientes en el alcance revisado. La política vigente
conserva salidas acotadas separadas del recibo, sin caducidad, autopurga ni
reemplazo automático. El presupuesto compartido incluye recibos, salidas,
archivos parciales y reservas; el diario separado conserva su límite de64KiB
y no se elimina ni desbloquea al limpiar salidas. La limpieza manual autorizada
excluye artefactos activos/reservados y exige reconciliar antes de admitir.

Comprobaciones pequeñas ejecutadas con Python -B sobre JSON del workspace:

- Reserva correcta: 262144 + 65536 + 8192 = **335872 bytes**.
  El borrador inicial337920 fue corregido por el coordinador. El revisor también
  lo había aceptado erróneamente en un mensaje preliminar; retiró esa afirmación
  y contrastó la suma ejecutando aritmética. Con tamaños máximos caben99
  ejecuciones en33554432bytes;100plazas es un techo adicional, no una promesa.
- SUP-014 y SUP-015 coinciden en EARS y lógica entre prd-draft.json y prd.json.
- Los diez hashes de fuentes declarados en candidate.sources de prd.json
  corresponden a los bytes leídos al terminar la revisión.
- IR-SCOPE refleja la sustitución de recibos mínimos por la nueva decisión y
  enlaza U1..U7. El resumen del tema T-004 refleja la sustitución, conservando
  los intercambios históricos como historial.

## Interrogación y correcciones contrastadas

El revisor detectó IR-SCOPE y resumen de entrevista todavía expresando la
decisión antigua, y preguntó al coordinador. Este los corrigió; la nueva lectura
lo confirmó. Se preguntó además si la reserva era saldo pendiente y cuándo se
liberaba. El coordinador agregó reservation_lifecycle: transferencia de reserva
a bytes contabilizados bajo bloqueo cooperante, sin doble conteo; parciales
inciertos contados conservadoramente; saldo desconocido bloquea; remanente
liberado solo tras finalización exacta y reconciliación. La nueva lectura
confirma esa precisión. No requiere reinterpretar la preferencia humana.

## Identidad y límites

Hashes SHA-256 de bytes finales leídos (no OID Git ni revisión sellada):

| Documento | SHA-256 |
|---|---|
| closure-proposal.json | `5eb4067f9c7b92f406ce53071d89af3b54f790c01e6869654c5b13798c20a458` |
| prd-draft.json | `07ef83d03886b4e34b517a3c54e2ec0d7921e489027a770674356ed776c80149` |
| prd.json | `347c1ef79799c392cbdde520367efee92663687bbbcfcab6fc46862ea8fc9b64` |
| retention-change.json | `f4a08ab483c2b2677803c0d00657ac682ccbc90e82344ef263d35ff100bf3918` |
| recovery-contract.json | `00bcf1eb5777c0f391e4041103a45125a04636793664aaee5875af0849db772c` |
| interview.json | `418073208d9c4afa8077453cd6f110f1a12ccf2e4b11efe34673625c144197c2` |

Revisión sobre workspace mutable. La inspección cubrió closure-proposal,
retention-change, recovery-contract, PRD Markdown, requisitos draft/canónicos,
IR, resumen de entrevista, propuesta y registro. No equivale a validación
completa de esquemas, FSM, trazabilidad o de un commit sellado. No se ensayaron
persistencia, limpieza, bloqueo real, caída de procesos, CI, producción ni
hardware. La capacidad es lógica y no garantiza espacio físico disponible.
Las declaraciones humanas se contrastaron con el registro documental recibido;
este revisor no participó en esos turnos humanos. La revisión no constituye
aprobación RDD ni autoriza implementar o ejecutar el supervisor.
