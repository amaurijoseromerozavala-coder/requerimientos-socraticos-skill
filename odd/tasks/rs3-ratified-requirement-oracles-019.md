# WU-RS3-RATIFIED-REQUIREMENT-ORACLES-019

## Objetivo y autoridad

Decisión humana: los requisitos nuevos necesarios para cerrar brechas del PRD
se someten a selección y ratificación; cada prueba se vincula al SHA exacto de
su requisito y a sus propios bytes antes de modificar código. El agente no
puede cambiar una prueba sellada para fabricar GREEN. Continúa la UI de WU-018
y el protocolo portable de WU-017. Esta unidad solo diseña el contrato; D03/D05
no están materialmente verificados y la ratificación runtime no existe.

## Alcance y criterios de aceptación

Definir identidad separada para requisito, oráculo legible, archivo de prueba,
helpers, runner y entorno. La autoridad debe residir fuera de los archivos que
el agente puede editar. Cada test se vincula a una revisión de requisito y un
snapshot Git; una revisión de prueba crea nueva identidad y exige nueva
ratificación, RED/GREEN y RDD. El digest protege bytes; no prueba intención ni
autenticación. Las pruebas históricas no se promueven retroactivamente.

## Oráculos RED congelados

1. Una transición desde requisito propuesto o respuesta libre hasta requisito
   ratificado exige selección explícita y recibo del guardián.
2. Un test no se admite como sellado sin identidad de requisito, oráculo y
   cierre transitivo del harness, vinculados a bytes SHA-256.
3. Alterar test, helper, runner o dependencias tras sellar bloquea GREEN y
   requiere una nueva revisión; el viejo test permanece trazable.
4. El agente no puede emitir ratificación, sustituir recibo o usar un manifiesto
   bajo su control como autoridad; CI/RDD sin guardián son evidencias técnicas
   acotadas, no autoridad humana.

RED → contrato documental → GREEN/regresión → RDD exacto → Git.

## Evidencia RED

Cuatro controles fallaron con `FileNotFoundError` para el contrato ausente,
exit 1, antes de escribir el contrato. No hubo ratificación runtime ni prueba
de un guardián físico.

## Evidencia GREEN y regresión

Cuatro controles focalizados, exit 0. La regresión
`PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh` terminó exit 0:
55 CI, 130 supervisor, 62 QA y 354 requisitos. Este resultado prueba la
coherencia documental y el árbol actual, no sella retroactivamente esas pruebas.
