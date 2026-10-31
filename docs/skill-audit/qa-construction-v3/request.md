# Solicitud humana y alcance del candidato

«Carga la skill requerimientos socraticos y ambos y continua la construcción de la skill qa en gentle aí».
«No quiero happy paths quiero la skill funcione en la realidad». «Usa gentle aí».
Decisión: «Delegas esos juicios técnicos a la skill dentro de criterios explícitos; las excepciones vuelven a ti.»

Se construyó skill local alpha ANALYSIS_ONLY y checker de consistencia de reportes.
No autoriza CI, producción, ensayos físicos ni ejecución de casos de aplicación.
Checker no autentica fuentes/humanos ni demuestra verdad de observaciones, completitud o enforcement global.
No promete que un proceso de LLM sea determinista o que validar JSON sea aprobar un sistema.

## Verify

Tres findings independientes: juicio no ligado a assessment/conjuntos; GAP no propagaba material_gap; NOT_RUN sin reason.
Controles añadidos ANTES de corregir:39tests,3fallos pertinentes; después43testsOK local y reejecuciónindependiente43OK.
Cuatro probes independientes confirman F1-F3 corregidos; independent-correction.json y tests-green.log externos al candidato.
Modelo:64 resúmenes,0solapes ni entradas sinregla. Z3 medianteGentle:SATdominio,UNSATgap/no_output,propiedadesentrailed.
Perfil256 rechazado porbaseline,registroINCONCLUSIVE; perfil512admitido. No se afirma calibración i3/WSL.
InterrogatorioQ006-Q008 real,recibos exactos; humano separado. PRDglobal/FSMintegración/aceptaciónaplicación pendientes.

Revisar semántica, autoridad, tipado/referencias, agregaciónFAIL+gaps,mutaciones y límites declarados.
La evidencia de ejecución externa es verificable como archivo local, pero no se atribuye su repetición al proveedor RDD si no la ejecuta.
