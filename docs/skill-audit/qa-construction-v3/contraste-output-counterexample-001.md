# Contraste del output QA-REVIEW-COUNTEREXAMPLE-001

Tipo: revisión estática y lectura de evidencia existente; no ejecución de la misión.
El output QA es una propuesta, no una instrucción humana ni consentimiento RDD.
Gentle AI confirma RDD global ON; el candidato previo espera consentimiento.

## Afirmaciones contrastadas

1. «43 tests no verificados independientemente»: contradice el recibo
   independent-correction.json y su log: revisor /root/qa_requirements_resume,
   43 pruebas, exit0 y cuatro probes. Los cinco hashes registrados coinciden
   con los archivos actuales. Esto acredita repetición en este workspace, no
   reproducción en otro equipo ni verdad universal. Z3 se ejecutó por el
   coordinador; no consta repetición independiente del solver en ese recibo.
2. «Implementación no demostrada»: existe validate_report.py y se probaron
   API/CLI reales. Es un comprobador local de consistencia. La aplicación
   objetivo y la orquestación integral de QA no están validadas.
3. INFRA_FAILURE: hallazgo aceptable en alcance acotado. main() agrupa
   MemoryError/OSError con errores de entrada y emite INVALID/REJECT_INPUT.
   Conviene distinguir ejecución/infraestructura, admisión y conclusión de
   calidad. El analizador Z3 ya devuelve INCONCLUSIVE con código de recurso;
   no debe reinterpretarse como defecto lógico del modelo. Una terminación
   no interceptable no garantiza salida JSON del propio proceso: el observador
   externo tendría que registrar ausencia de resultado/exit/señal. No afirmar
   causa OOM solo por una señal.
4. ulimit -v 2097152: cota de espacio virtual de2GiB en bash/Linux; no reserva
   RAM, no impide paginación del host y no garantiza aislar presión global.
   No se requiere imponer esa cifra para dar validez a la lógica formal.
5. Documento inválido más alerta independiente: mejora de diseño posible,
   no requisito aceptado ni defecto demostrado por el informe. El schema se
   rechaza antes de interpretar evidencia. No existe verificador de firmas
   CURRENT_FAILURE ni contrato de confianza de claves en este alpha. SHA256
   identifica bytes y no equivale a firma. Una observación no verificada no
   puede convertirse en fallo demostrado o entrada aceptada. Un canal de
   diagnóstico separado requeriría contrato y pruebas propios.
6. Estado de oráculo desconocido: el enum actual lo rechaza como entrada
   inválida, sin ejecutar casos. Rechazo no equivale a autoautorización. El
   requisito humano de consultar excepciones no obliga a tratar cada error
   de sintaxis como decisión humana. Debe distinguirse entrada inválida de
   excepción semántica válida. ESCALATE_USER como evento universal es propuesta.
7. Digest: verify_ref calcula SHA256 de raw, los bytes ya leídos en memoria,
   antes de derivar el resultado. La exigencia principal del Test4 ya está
   implementada. No demuestra atomicidad del directorio ni que el archivo
   permanezca igual después de leerse. El alpha declara explícitamente lint
   de archivos mutables, no snapshot global sellado. El test de cambio durante
   lectura propuesto no se ejecutó en esta revisión.

## Resultado

Conservar alpha y ausencia de aprobación de producción. Prioridad técnica:
separar error de infraestructura de invalidez de datos y preservar diagnósticos
sin convertirlos en conclusiones semánticas. Matriz multidimensional y consulta
de excepciones necesitan contrato preciso; no se incorporan automáticamente
porque el output QA las llame obligatorias. No se cambiaron fuentes del
candidato ni se concedió el consentimiento pendiente en nombre del humano.
