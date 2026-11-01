# WU-SUP-JOURNAL-001 — Candidato para RDD

API interna Journal.initialize/context/inspect/reserve. Directorio nuevo0700,
archivos0600, no recreación implícita, bloqueo flock cooperativo. Lectura16KiB,
rechazo de symlinks/tipos/propietario/modos, schema y claves repetidas. Datos de
identidad suministrados por llamador confiable, no autenticados ni sondeo real.

Escritura temporal+fsync+replace+fsyncdirectorio. Falta/corrupción bloquea; reserva
RESERVED nunca se desbloquea por tiempo/cierre/reinicio del proceso. Fallo de
persistencia bloquea instancia; si replace ya ocurrió la siguiente instancia
observa RESERVED. Antes de replace no hay reserva confirmada ni lanzamiento.
Initialize fallido deja almacén parcial, nunca se repara automáticamente.

12testsGREEN; suite41testsGREEN. RED inicial de API ausente y RED de guardia
interna ausente conservados. Proceso auxiliar real os._exit tras reservar: nueva
instancia bloqueada. Fallos fsync inyectados prueban ramas, no corte físico ni
comportamiento del SSD. Mutex impide reservas simultáneas en una instancia.
El propietario debe serializar apertura/cierre de su contexto respecto al uso.

Sin implementación de ACTIVE/STOPPING/CONFIRMED_TERMINATED, recuperación, reserva
física de capacidad ni integración del journal con QA. Ninguna autorización de
lanzar puede derivarse solo de reserve. flock no protege frente a procesos que
ignoran el protocolo ni cambios de cuenta/root. fsync depende del filesystem;
no prueba durabilidad física universal, hardware i3, CI ni producción.

RDD pendiente; código y pruebas aún no publicados. Logs voluminosos de regresión
referenciados por hash, no incluidos en contexto de revisión estática.
