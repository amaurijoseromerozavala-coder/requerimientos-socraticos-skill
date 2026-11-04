# WU-RS3-GAP-QUESTION-MODEL-BINDING-024

## Objetivo y alcance

Después de WU-020..023, impedir que un paquete de escenario con testigo
alterado produzca una pregunta que afirme una brecha de guardas inexistente.
Revalidar mecánicamente dominio y guardas contra el modelo explícito antes
de formular. Vincular la pregunta a las frases correspondientes del glosario
sin inferir significado humano ni confirmar una decisión. El modelo lógico
permanece la fuente de la comprobación booleana; el glosario sigue siendo una
propuesta no autenticada.

No modificar el solver, la semántica de `NO_OUTPUT`, los gates D03/D05 ni
autorizar ejecución. No ensayar el hardware i3/WSL inaccesible.

## Oráculos RED congelados

1. Paquete con `status=NEEDS_HUMAN_INTERPRETATION`, digest y tipos correctos,
   pero asignación que viola el dominio: ningún texto de pregunta emitido.
2. Paquete con asignación de una guarda activa: ningún texto de pregunta.
3. Paquete legítimo: pregunta propuesta y frases correspondientes a cada
   valor booleano, con autoridad `NOT_GRANTED`.
4. Modelo/glosario obsoletos y fuente no verificada conservan sus bloqueos.

RED pertinente → GREEN → regresión → RDD exacto → respaldo Git.

## Evidencia RED/GREEN

RED focal: 3 pruebas; el constructor no aceptaba `model` (errores de interfaz)
y sin modelo emitía `PROPOSED_UNVERIFIED` en vez de bloquear. Por ello, la
falsación material de paquetes alterados se verificó tras introducir el
parámetro y no se atribuye al error de interfaz por sí solo. GREEN focal:
4 pruebas, OK; regresión acotada de brechas: 14 pruebas, OK.
Regresión integral `ci/run_quality.sh`: exit 0; CI 55, supervisor 130,
QA 62 y requisitos 371 pruebas, OK. Calibración i3/WSL: NOT_RUN.
