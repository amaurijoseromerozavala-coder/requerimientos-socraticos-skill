# Requerimientos socráticos2.4.1 — correcciones aceptadas

## ANALYSIS

Cambios reales sobre la skill local existente; upstream Gentle AI no modificado.
Supervisor separado del motorZ3 y parseo, plazo de trabajo por reloj monotónico,
parada del grupo propio POSIX en vencimiento/interrupción y espera/drenaje acotados.
Linux vincula el worker directo al padre mediante PDEATHSIG y comprueba la carrera
de arranque. Gracia de limpieza1s bajo SO responsivo; si no se confirma limpieza,
cleanup_status=INCOMPLETE. No se promete tiempo real ni contención de descendientes
fuera del grupo o de kernel/cuenta comprometidos.

Preflight JSON iterativo antes del decoder: límite estructural96, cadenas y
escapes respetados; se conservan UTF8/gramática/duplicados y AST32 de las etapas
posteriores. El caso profundo no había demostrado un crash en2.4: esto es defensa
adicional. Se mantiene manejo de errores estructurados.

Sin fallback del intérprete predeterminado. Elección explícita se resuelve o
rechaza. Registro de ejecutable absoluto, SHA256 observado y versiones de
paquetes; módulo Z3 identificado. Eso no autentica ni firma toda la cadena.
El sondeo expone physical_host=NOT_OBSERVED y resource_admission=NOT_ASSESSED:
memoria guest visible no se presenta como capacidad física saludable ni presupuesto.
No se añadió sondeo remoto/Windows host ni calibración física.

## TEST PLAN

Pruebas pequeñas, temporales y de procesos propios; sin cargas intensivas.
Seis casos preflight: profundidad, tamaño, cadenas/escapes, UTF8 y estructura.
Diez casos de supervisión: espera acotada, resultado normal, presupuesto mínimo,
identidad, entorno ausente, JSON profundo, muerte del padre Linux, líder terminado
con pipes heredados, adaptador no soportado y compatibilidad de argumentos.
Regresión de analizador/probe y anteriores validadores incluidas.

El revisor independiente Astra inspeccionó un snapshot acotado y ejecutó28tests
iniciales en copia temporal. Detectó que el líder terminado podía dejar espera
por pipes heredados: RED .82077s frente a presupuesto.1. Corregido y contrastado:
8tests supervisor, fixture original .10049s, limpieza confirmada. Holder fuera del
grupo produjo1.10231s y cleanupINCOMPLETE; harness recogió sus fixtures. Esas
observaciones son Linux local, no prueba del PC objetivo ni plazo milimétrico.
Los manifests indican exactamente qué snapshot cubrió cada revisión.

## VERIFICATION

132 tests locales OK en full-tests.log. El registro contiene fallos RED previos,
no se borran como si nunca hubieran ocurrido. La suite completa final incluye
la corrección posterior del código de error público.

RDD nativo de riesgo alto con cuatro lentes: review-65b72cd5614b2220.
Hallazgo R3-error-contract: error de argumentos devolvía SUPERVISOR_ERROR en vez de
INVALID_INPUT. Reproducido y corregido; prueba pública nueva preserva contrato para
argumentos ausentes, opción desconocida, timeout inválido y tipo incorrecto.
Corrección acotada admitida/validada, cierre approved y acknowledged.
Candidato final: sha256:a587a67b793c15b95c7cf28b20150eef275cf6a8dc7105932adf26e314cf716a.
Todos los archivos seleccionados coinciden con el árbol revisado; recibo completo
en rdd-correction-final.json. No llamar a esa revisión reproducción de132tests:
la ejecución completa es local y la reproducción independiente tiene alcance propio.

Windows nativo no inicia worker: SUPERVISION_UNSUPPORTED_PLATFORM hasta disponer
de adaptador adecuado; WSL usa rutaLinux. macOS NOT_RUN. No extrapolar a Windows
el drenaje POSIX: sus lectores de pipes requieren otro adaptador.
Lean NOT_RUN. Hardware i3/WSL NOT_RUN. Sin CI ni producción. Se conserva
BLOCKED_GLOBAL_ENFORCEMENT y entrevista/autoridad humana, sin aprobar PRD por exit0.
validation.json sigue PRE_REVIEW congelado; recibo exterior registra la aprobación.
Este informe es posterior, no un archivo autoaprobado dentro del candidato.
