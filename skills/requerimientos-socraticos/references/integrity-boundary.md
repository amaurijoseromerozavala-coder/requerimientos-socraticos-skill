# Vía principal vigente desde 2.2

Usar [objetos Git fijados y política de codificación](sealed-validation.md).
El contenido siguiente describe los diagnósticos históricos sobre worktree;
inotify/flock no se usan como autoridad para aceptar un candidato.
`requirements validate` ahora requiere repo + --commit OID_COMPLETO + --prd.
El antiguo comando validate sobre directorio se llama `requirements lint`.

# Integridad, alcance y frontera de confianza

## Estados y afirmaciones

COMPLETE en interview.json significa cobertura de las dimensiones declaradas,
no completitud del sistema global. Antes de cerrar un PRD, revisar límites del
sistema, interfaces, entorno, consumidores, amenazas, recuperación y riesgos de
composición. Dos respuestas técnicas no cierran esos dominios por sí solas.
Un READY escrito, un hash o PASS sintético no constituye autoridad ejecutable.

La validación semántica y los recibos RDD auténticos siguen siendo obligaciones
externas. Los validadores actuales comprueban documentos y ficheros retenidos;
no autentican la procedencia nativa de todo recibo declarado. No presentar su
exit 0 como autorización de implementación, despliegue o siguiente fase.

## Comandos locales instalados

La extensión del launcher local de Gentle AI permite:

```sh
gentle-ai requirements snapshot /ruta/directorio > /ruta/externa/baseline.json
gentle-ai requirements verify /ruta/directorio --baseline /ruta/externa/baseline.json
gentle-ai requirements validate /ruta/directorio --prd prd.json --timeout 15
gentle-ai requirements advance /ruta/directorio --prd prd.json --timeout 15
```

No guardar salida/baseline dentro del árbol observado. `snapshot` enumera todo,
incluidos archivos añadidos y directorios vacíos; compromete rutas, tipos,
permisos, tamaños y SHA-256 de contenidos en un hash canónico del árbol completo.
No es el formato Git tree ni un Merkle incremental. No hay exclusiones ocultas.
`verify` exige igualdad del inventario completo y raíz; una referencia base
puede ser falsificada por quien controle su almacenamiento, por lo que no es
firma ni origen autenticado. Symlinks, FIFO y entradas especiales se rechazan.

Durante cada invocación se registran primero los watches de todos los directorios
existentes, sin leer contenidos. Solo después comienza la ventana declarada de
observación/lectura. La preparación de watches no está cubierta como historia
continua; los timestamps del recibo delimitan la ventana posterior. Se rechaza
cualquier evento relevante, overflow, pérdida de watch o fallo de registro. Crear
un subdirectorio provoca rechazo; no se presume cobertura de sus contenidos.
También se vigila el padre: cambios de hermanos pueden bloquear por prudencia.
El intervalo termina en el último check antes de devolver el resultado, no
abarca el pasado ni el futuro, ni demuestra ausencia de todo cambio posible.
No reconstruye los 16 minutos de la auditoría histórica. Soporta exclusivamente
la hipótesis de un filesystem Linux local con kernel/cuenta/validador confiables;
WSL sobre /mnt/c y recursos remotos requieren verificación específica.

`validate` crea una copia privada acotada y ejecuta el validador sobre ella,
manteniendo observación del origen hasta el último check. Un lock exclusivo
fcntl.flock externo al árbol serializa invocaciones cooperativas por raíz.
Hay timeout de espera de lock y del subproceso; límites 32 MiB/4096 entradas y profundidad máxima de 64 niveles.
Bases JSON no objeto o mal formadas se rechazan con BLOCKED estructurado.
No son deadlines duros de I/O del kernel. Escritores que no respeten el lock,
administradores o código hostil con el mismo UID quedan fuera de esa garantía.
No se agregan locks a cada fichero: eso tampoco obligaría a esos escritores ni
haría atómica una transacción multiarchivo.

## Avance fail-closed y trabajo pendiente

`advance` **siempre bloquea**, incluso con documento validado: no existe un
consumidor de siguiente fase configurado y confiable. Estado operativo:
BLOCKED_GLOBAL_ENFORCEMENT. No afirmar que se implementó una integración global
ineludible; únicamente queda bloqueada esta entrada local.

Para habilitar avance hará falta integrar el consumidor real para que use el
snapshot exacto, autentique revisión nativa de su identidad y rechace documentos
sueltos, recibos autofabricados y revisiones obsoletas. Su política debe vivir
fuera del alcance de escritura del autor (servicio/cuenta separada o CI protegido
con reglas efectivas). Un hook pre-commit local admite --no-verify y no satisface
esa frontera. Una firma con clave accesible al mismo autor tampoco la satisface.
No hay remoto/CI protegido ni ese consumidor configurado en este proyecto;
no se inventan credenciales, firmas ni configuración de protección.

## Oráculos y evidencia

Congelar falsador y criterio antes de ejecutar. Un fixture positivo debe tener
hash vigente para alcanzar la condición que se intenta probar. Cambiar su estado
sintético exige recalcular dependencias; se conserva además el control negativo
que deja el hash obsoleto y exige STALE_CANDIDATE. Corregir preparación de datos no
equivale a demostrar corrección semántica. No modificar el criterio para ocultar
un contraejemplo real. Conservar fallos y distinguir error del fixture de RED
específico; revisar cambios de tests y código en el mismo candidato RDD.

No ejecutar stress-ng hasta agotar RAM/swap del host compartido como sustituto
de medir el hardware objetivo. Cinco validadores concurrentes con entradas
pequeñas no implican thrashing; medir RSS, latencia, filesystem, cuotas y presión
en el WSL real. Hardware declarado no equivale a entorno observado.

Fuentes primarias consultadas 2026-10-26:
- https://man7.org/linux/man-pages/man7/inotify.7.html
- https://man7.org/linux/man-pages/man2/flock.2.html
- https://git-scm.com/docs/githooks
