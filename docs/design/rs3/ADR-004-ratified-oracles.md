# ADR-004 — Requisitos emergentes y pruebas selladas por identidad

**Estado:** decisión humana de diseño registrada; guardián, UI, recibos y gate
de CI aún no implementados. El [contrato](ratified-oracle-contract.json) mantiene
`authority_verification=NOT_ESTABLISHED` y `execution_authorized=false`.

## Regla de autoridad

Una brecha del PRD genera una propuesta de requisito, no una regla canónica.
El agente presenta en la UI la pregunta, significado, opciones, consecuencias
y falsador. La respuesta personalizada retorna al interrogatorio sin recibo.
Cuando el humano elige una opción exacta, la ratificación requiere el guardián
y un recibo vinculado a los bytes canónicos de esa revisión. Un requisito nuevo
no se incorpora por inferencia del agente, por un SHA o por un resultado de QA.

Para cada test, el humano ve el **oráculo legible**: escenario, entrada, salida
esperada, caso negativo, límites y vínculo al requisito ratificado. El agente
puede proponer código de prueba, pero QA debe examinar su correspondencia con
el oráculo. El guardián sella una identidad de test que incluye el SHA-256 de
los bytes del requisito, la especificación del oráculo y el archivo de prueba,
además de los helpers, runner, lock de dependencias y perfil de entorno que
pueden cambiar su comportamiento. El manifiesto referencia el OID del árbol
Git de origen y declara el algoritmo real de ese repositorio; no se presume
que un OID Git sea SHA-256. El recibo autentica el manifiesto exacto, sin
contener su propio hash para evitar circularidad.

El test se sella **antes** de editar la implementación. Se observa RED con ese
test y se distingue un fallo pertinente de una avería de infraestructura. Tras
la implementación se verifica otra vez el manifiesto contra el recibo
independiente, se ejecuta GREEN y se revisa el candidato exacto con RDD.
Cambiar una sola dependencia ejecutable del test invalida ese GREEN de
confianza. Una corrección legítima del test crea nueva revisión con explicación,
selección humana, nuevo recibo, RED/GREEN y RDD; la revisión anterior permanece
trazable. No se edita el oráculo sellado en el lugar para acomodar el código.

## Frontera efectiva y vacíos

Un archivo de manifiesto dentro del worktree editable por el agente no es el
guardián. El futuro gate debe obtener el recibo de una cuenta/almacén separado
y comprobar todos los hashes antes de admitir ejecución. Debe fijar el cierre
transitivo real de helpers y configuración; un import dinámico no identificado
bloquea un GREEN confiable. Para CI remoto falta definir un ancla de confianza
que el cambio bajo prueba no pueda reescribir (por ejemplo un verificador y
clave pública protegidos); `main` y el guardián local no se convierten en ese
ancla mediante este ADR. Las pruebas existentes conservan su valor como
evidencia técnica, pero no se declaran ratificadas retroactivamente.

Un SHA detecta cambios de bytes bajo sus supuestos; no demuestra que el humano
entendió el oráculo, que QA probó su semántica o que la ejecución física fue
correcta. El registro Git protegido puede dar trazabilidad de versiones, pero
sus referencias y permisos deben verificarse; no se presume inmutabilidad
material de un repositorio editable. Ningún resultado de este contrato abre
el gate de producción.
