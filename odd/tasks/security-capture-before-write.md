# WU-SEC-CAPTURE-001 — saneamiento previo a captura durable

## Objetivo y alcance

El núcleo de procesos recibe stdout/stderr del hijo; el `Journal` de una
instancia local escribe `runs/<slot>/stdout.bin`, `stderr.bin` y `receipt.json`.
Esta unidad cubre exclusivamente esa ruta durable, incluida la llamada directa
a `Journal.store_capture`. La frontera de seguridad está antes de `os.mkdir` y
`os.open` del slot, no después de escribir. El recibo debe resumir los bytes
efectivamente retenidos; el resultado devuelto por el núcleo, cuando usa
journal, no debe volver a exponer los bytes crudos.

No controla capturas nativas de herramientas externas, logs escritos por el
hijo antes de llegar al pipe, ni los originales forenses. Ningún recibo externo
se presenta como protegido por esta unidad.

## Oráculo y casos RED

Con valores exclusivamente ficticios, el archivo retenido y el retorno del
núcleo no deben contener un valor pasado como `--token=...` ni `--token ...`.
Un JSON anidado con argumento de capacidad y una copia del mismo valor debe
mantener estructura y datos ordinarios, pero ocultar todas las copias. El
recibo conserva esquema y hashes de los bytes saneados.

Si el saneador falla, el journal no crea el slot ni escribe datos crudos; el
estado terminal no se reconcilia. Si falla la escritura después del saneamiento,
los archivos parciales no pueden contener los valores crudos y el estado queda
bloqueado. Errores visibles se expresan mediante tipos/códigos sin incluir la
entrada. Una entrada ordinaria se conserva byte a byte.

## Contratos y límites

Mantener límites de tamaño, reserva, estado y fsync del journal, además de
preservar sus originales privados y el candidato de la unidad anterior. El
escaneo es acotado a formatos reconocidos; un marcador sensible ambiguo cierra
la admisión. No se afirma seguridad de canales ajenos al journal.

## Tareas

1. Registrar controles negativos y RED real en tests del journal.
2. Integrar un único saneador en `store_capture` antes de cualquier escritura.
3. Devolver al núcleo los bytes retenidos, probar fallos, GREEN y regresiones.
4. Revisar el candidato exacto mediante Gentle AI; sin RDD no cerrar la unidad.
