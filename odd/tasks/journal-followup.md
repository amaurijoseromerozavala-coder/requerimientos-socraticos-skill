# WU-SUP-JOURNAL-002

Resolver review-ef2bb19372d7c729/R4-001 y R3-001. Preservar JournalBlocked y
su causa de persistencia si unlink también falla; registrar diagnóstico secundario
sin liberar bloqueo de instancia. Limpiar únicamente temporal creado por esta
operación. No reset ni recuperación. Añadir pruebas públicas de registros con
clave state duplicada terminando IDLE, schema desconocido y estado/identidad
incoherentes, sin modificar bytes rechazados.

RED doblefallo real inyectado antes de corregir; GREEN y regresiones. La cobertura
de registros puede pasar con implementación actual; control negativo sobre copia
para falsar omisión de claves duplicadas, sin inventar defecto de producción.
RDD exacto antes de publicación. No integrar lanzamiento ni calibrar hardware.

## Log
RED doblefallo observado. GREEN14tests journal y43suite. Mutante de hook permisivo
rechazado por aserción precisa. No cambio a validación de registros de producción.
RDD pendiente; integración con lanzamiento continúa fuera de alcance.
