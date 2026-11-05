# WU-RS3-SUPERVISED-QUESTION-HANDOFF-029

## Objetivo y precedencias

Continuar WU-028: la entrada que supervisa el analizador debe poder entregar
una sola pregunta estructurada para el siguiente intercambio del interrogatorio,
derivada del mismo informe verificado que alimenta la vista HTML. No aceptar
un informe ni una pregunta libre como sustituto del analizador. Conservar HTML
como salida predeterminada.

## Alcance y límites

Salida JSON de propuesta sin respuesta, selección, confirmación ni escritura
de autoridad. Incluir identidad reproducible de la pregunta y hashes del
modelo y glosario observados, sin atribuir autenticidad externa a esos bytes.
No avanzar a D03/D05, no persistir entrevistas ni abrir navegador. Se conserva
la frontera de proceso y recursos de WU-028. Hardware i3/WSL no disponible.

## Oráculos RED congelados

1. Un modelo y glosario reales entregan exactamente una pregunta estructurada
   y mantienen HTML por defecto.
2. El handoff no contiene respuesta, decisión ni permiso; indica propuesta
   sin autenticidad de fuente establecida.
3. Cambiar una frase propuesta del glosario altera la identidad de la
   pregunta; ejecuciones idénticas conservan la misma identidad.
4. Un informe inválido, timeout o limpieza incierta no emiten handoff parcial.

RED focal → GREEN y regresión → RDD exacto → respaldo Git.

## Evidencia

RED focal: 3 tests fallaron (exit 1): la CLI rechazó `--format`, la salida
estaba vacía y la API no aceptaba `output_format`. GREEN focal: los mismos
3 tests pasaron (exit 0) tras añadir el handoff. Regresión integral
`ci/run_quality.sh`: exit 0, CI 55, supervisor 130, QA 62 y requisitos
387 tests. Calibración física en i3/WSL: NOT_RUN.
