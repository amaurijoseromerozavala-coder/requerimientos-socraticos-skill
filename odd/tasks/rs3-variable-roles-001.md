# RS3-WU-VARIABLE-ROLES-001

## Intención y alcance

El paquete RS3 confirmado por el maintainer exige validar roles antes de Z3.
Esta unidad distingue referencias desconocidas de salidas usadas en el dominio
o en guardas del modelo booleano vigente. Conserva la forma JSON, los límites
y el código de salida existentes; no migra modelos antiguos ni decide RS3-D02.
`production_ready` significa elegibilidad para revisión documental (D01),
sin autoridad de despliegue.

## Oráculos RED

- Una salida declarada en `domain` o `rules[].guard` produce el diagnóstico
  estable `WRONG_VARIABLE_ROLE` antes de construir consultas Z3.
- Un nombre no declarado produce `UNKNOWN_VARIABLE`, distinto de un rol
  equivocado, tanto en guardas como en respuestas.
- Una salida declarada en `response` o `properties[].expression` sigue válida.
- La CLI conserva `INVALID_INPUT` y exit 2, con diagnóstico tipado en el mensaje;
  las consultas y tests anteriores deben conservar su comportamiento.

## Tareas y cierre

Ejecutar RED de casos de rol, implementar el cambio mínimo en el validador
preexistente, ejecutar GREEN y regresiones, RDD del candidato exacto y respaldo
normal en GitHub después del recibo aprobado y reconocido. Sin pruebas de carga.
