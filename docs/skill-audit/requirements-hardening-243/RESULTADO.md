# Requerimientos socráticos 2.4.3 — presupuesto de memoria

Fecha: 2026-10-28. Autorización: «Haz las mejoras», referida al pendiente aceptado
de presupuesto, observación y manejo del agotamiento. Cambios en herramientas de
la skill local, con Gentle AI real4.2.0 para RDD; upstream no modificado.

## ANALYSIS

La coordinación de objetos y transporte Git se separó en un proceso dedicado.
Así la API puede acotar el trabajo de datos sin reducir los límites de la
aplicación externa que la invoca. El consumidor y cada comando Git también reciben
RLIMIT_AS antes de exec, mediante la extensión opcional del supervisor compartido.
Los llamadores del supervisor sin esa opción conservan su comportamiento anterior.

Perfil inicial configurable512MiB; rango técnico256..1024 múltiplo8. Es política
provisional, no capacidad medida del PC ni cuota física. Los soft por rol son
CLI64, coordinador256, consumidor128 y Git64MiB. La CLI usa hard256 para que el
hijo pueda establecer su propio límite sin aumentar un hard heredado. Coordinador,
consumidor y Git usan hard igual a su soft. La suma describe el perfil solicitado;
no constituye una cuota agregada kernel ni una garantía de RSS/swap/host.

La CLI comprueba su VmSize antes de reducir su soft; si ya lo supera o es
desconocido, bloquea antes de empezar. Reducir RLIMIT_AS no elimina mappings
existentes. La API conserva límites del llamador y lo declara en su respuesta;
su perfil no limita la memoria total de esa aplicación externa.

La admisión toma un lock privado no bloqueante por cuenta y lo hereda a los
consumidores. Solo coordina clientes cooperantes; no controla procesos ajenos.
Se exige headroom visible >=2x perfil, observando MemAvailable y todos los
ancestros cgroup-v2 visibles. Desconocido, malformado, insuficiente u ocupado
bloquean. Las muestras son secuenciales y parciales; no reservan memoria ni
demuestran salud del host Windows/WSL. No se modifican cgroups ni privilegios.

Los resultados incluyen VmSize, RSS, high-water RSS hasta la muestra y límites
virtuales reales del coordinador/consumidor. No se suman picos no simultáneos como
un pico global. Son muestras anteriores al final de serialización/ejecución.
Ante MemoryError capturado se intenta emitir un registro fijo de fallo; señales
o ausencia de diagnóstico permanecen sin causa demostrada. Nunca se presume que
todo fallo nativo puede convertirse en MemoryError o en un JSON recuperable.

Se conservan OIDs y bytes consumidos, schemas y recibos, límites documentales,
normalización0600, CI diferido y BLOCKED_GLOBAL_ENFORCEMENT. Este perfil se aplica
a validación Git; no declara cuotas de memoria para todas las demás herramientas.

## TEST PLAN

RED previos conservados: helper de política ausente; opción de límite no admitida
en supervisor; API/CLI sin presupuesto. Después se verificaron políticas, límites
heredados, ausencia de mutación del llamador API, admisión ocupada/desconocida,
herencia del lock y diagnósticos explícitos. Los controles negativos deben fallar
por la condición prevista, no por un error cualquiera.

Ensayos pequeños propios: un hijo con límite Vm inicial+4MiB rechazó un único
intento8MiB; otro observó el límite heredado/solicitado con asignación1MiB. No
se llenó RAM/swap ni se ensayó hardware de terceros bajo agotamiento. Cada grupo
tuvo timeout exterior y limpieza de sus procesos de prueba.

La revisión independiente inicial59tests detectó tres bordes. Se conservaron
sus evidencias y se prepararon RED específicos antes de corregir:

1. Rechazo del hard heredado sin normalizar la excepción pública: ahora es
   InvalidGit(RESOURCE_CONTROL_SETUP_FAILED), sin alterar ese límite.
2. Perfil inferior a la memoria virtual ya mapeada: ahora bloquea antes de
   cambiar límites. Un perfil válido no equivale a un runtime admisible.
3. Nuevo salto del coordinador con stdout2MiB podía recortar manifiestos antes
   permitidos: se amplió a8MiB. El contrato se probó con fixtures pequeños; la
   cota frente a cabecera/manifiesto/consumidor se revisó estáticamente, sin
   generar un manifiesto máximo ni llamarlo ensayo de ese máximo.

Las pruebas internas de colección/ciclo de vida se dirigieron al coordinador
dedicado; la entrada pública tiene pruebas separadas de presupuesto. No se
presentan fixtures internos directos como prueba de una cuota global del sistema.

## VERIFICATION

- Regresión final: **195tests OK**,6.921s observados, timeout exterior45s;
  full-tests.log. La duración no se promete para otro entorno/documento.
- Compatibilidad contra2.4.2: **11casos stdout/stderr/exit idénticos**,
  differential.json; no es una exploración exhaustiva de toda la interfaz.
- Revisión independiente posterior: **62tests OK**, con copia y SHA256 propios,
  más comprobaciones pequeñas del hard heredado y perfiles. La evidencia inicial
  permanece como independent-initial-*; las correcciones están en el informe final.
- Caso real pequeño con hard128MiB: API devuelve InvalidGit de configuración y
  conserva128/128. CLI256 bloquea por baseline; CLI512 funciona con roles esperados.
- CLI local Gentle AI sobre documento sintético pequeño: PASS, identidad de bytes
  y avance bloqueado. Muestras RSS: coordinador13271040bytes, consumidor18104320bytes.
  No son máximos del sistema ni calibración i3/WSL; public-git-validation.json.
- RDD nativo, riesgo alto, cuatro lentes: `review-29a23cffb87a1be5`, approved en
  último evento y acknowledgement exacto completado. Candidato:
  `sha256:d42b9b6eb80a5ef2041bbaac3cfbeab4866699af74361a59cce568a85e1f6717`.
- **92 archivos** seleccionados idénticos al árbol revisado
  `545a82b676d16a2979f0dfddf765222b14b9d2f5`, integrity-final.json.

La revisión nativa inspecciona código, contratos y pruebas completas. Los logs
de ejecución son evidencia externa íntegra; no atribuir al RDD la reproducción
de195tests. La reproducción independiente62 tiene su propio alcance y fuente.
validation.json permanece FROZEN_PRE_REVIEW; el cierre está en recibos externos,
sin insertar una autoaprobación que cambie el candidato ya aprobado.

Hardware i3/WSL: NOT_RUN. Lean: NOT_RUN. Cuotas globales, RSS agregado, disponibilidad
física, temperatura y comportamiento de presión externa: NOT_PROVEN. No se ha
habilitado CI, producción, QA Inquisidor ni avance automático del proyecto.

## Registro documental

No hubo nuevas preguntas de intención al humano ni respuestas semánticas
inventadas. Las consultas entre implementadores resolvieron APIs técnicas,
ruta de runtime, métricas y alcance; no crean decisiones de negocio. El perfil
numérico es una elección técnica provisional del implementador, declarada como tal.
Engram conserva el documento ODD y localizadores; el código y recibos en disco
siguen siendo la evidencia actual de esta entrega.
