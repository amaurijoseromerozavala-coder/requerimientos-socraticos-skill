# WU-RS3-PRINTED-CODE-VERIFIER-036

## Objetivo y dependencia

Sobre WU-035, añadir un verificador local de códigos **sintéticos** para una
tarjeta ya definida. Solo acepta códigos hexadecimales de 128 bits como
formato provisional; su longitud no demuestra que fueron generados con
entropía real. El emisor, impresión y entrega quedan fuera de alcance.

## Alcance

El almacén privado guarda sal aleatoria y SHA-256 de sal + código por
coordenada, nunca códigos en claro. Cada intento verificable sobre una
coordenada PENDING, acertado o fallido, debe llamar `spend_pending` y obtener
persistencia antes de devolver `code_match`. Un fallo de almacén, fsync,
reconciliación o digest de desafío deja PENDING/SPENT sin respuesta de acierto.
La salida permanece `authority_verification=NOT_ESTABLISHED` y
`execution_authorized=false` incluso si `code_match=true`.

No se crea cuenta, tarjeta física, credencial real, CLI, UI, recibo ni
permiso de operación. Se prohíbe usar esta unidad como autenticador humano;
no controla el origen del desafío, la custodia D05 ni el terminal.

## Oráculos RED congelados

1. Código sintético correcto en PENDING devuelve `code_match=true` solo tras
   SPENT; repetirlo o cambiar digest de desafío bloquea.
2. Código incorrecto o malformado consume la coordenada y devuelve false;
   no admite intentos ilimitados.
3. Dos verificaciones simultáneas no pueden devolver dos resultados admitidos.
4. El archivo 0600 no contiene códigos; symlink, permisos erróneos, contenido
   corrupto, coordenadas ajenas o ausencia de verificador bloquean.
5. Si `spend_pending` falla o queda incierto, no se devuelve acierto.
6. No hay recibo, confirmación humana ni permiso de ejecución en la respuesta.
7. AVAILABLE, desafío distinto o etapa pendiente se rechazan antes de comparar
   el código; un symlink del verificador bloquea sin gastar la coordenada.
8. Dos coordenadas no pueden aprovisionarse con el mismo código. Un fallo de
   fsync del directorio tras crear el archivo deja un marcador bloqueante.

## Evidencia RED/GREEN focal

RED: `python3 -B -m unittest supervisor.tests.test_rs3_printed_code_verifier -q`
ejecutó siete pruebas y falló `test_not_pending_does_not_examine_code`:
`AssertionError: code examined before reservation`. La prueba sustituyó la
comparación por un falsador que solo se activa si se examina el código en
`AVAILABLE`.

GREEN: el mismo comando ejecutó siete pruebas, `OK`, tras comprobar PENDING y
el digest exacto antes de la comparación. El gasto duradero permanece como
última condición antes de devolver el resultado.

Segundo RED de revisión independiente: nueve pruebas; fallaron
`test_duplicate_code_cannot_be_provisioned` y
`test_uncertain_provisioning_blocks_verifier_use`. GREEN posterior: nueve
pruebas `OK`. El marcador de provisión no se elimina hasta sincronizar
el archivo y el directorio. Regresión completa y RDD: pendientes al registrar
esta evidencia.

Regresión: `PATH=/tmp/rs3-wu036-venv/bin:$PATH
REQUIREMENTS_PYTHON=/tmp/rs3-wu036-venv/bin/python bash ci/run_quality.sh`
terminó con exit 0: CI 55, supervisor 154, QA 62 y requisitos 409 pruebas
`OK`. La primera ejecución en este entorno carecía de Z3 y la segunda de
PyYAML; sus fallos de infraestructura no se contabilizan como GREEN ni como
defectos de esta unidad. Se instaló el entorno temporal con `requirements.txt`
y PyYAML 6.0.3, la versión de CI. Equipo i3/WSL: NOT_RUN.

## Proceso

ODD → RED ejecutado → implementación mínima → GREEN/regresión → RDD exacto →
respaldo Git. Pruebas de hardware objetivo y separación de UID: NOT_RUN.
