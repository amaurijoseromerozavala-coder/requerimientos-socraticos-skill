# WU-RS3-PASSWORD-AUDIT-002 — corrección del alcance D04

## Origen

El maintainer aclaró: «El backend es un auditor que verifica que puse la
contraseña y sepa que fui yo quien decidió». Esto corrige la interpretación
anterior de «Logs para auditar». El registro documental ya publicado no verifica
credenciales ni acredita una decisión humana; continúa como componente separado.

## Unidad actual: corrección documental de la interpretación

Rectificar las afirmaciones publicadas que presentan D04 como resuelta por un
registro sin contraseña. Esta corrección no implementa un verificador ni cambia
la autoridad de ninguna salida. El diseño e implementación del backend quedan
en una unidad posterior, después de decidir el origen de la credencial.

## Objetivo y frontera posteriores

Diseñar e implementar un verificador local que, para cada decisión, compruebe
una credencial introducida por el humano mediante un canal fuera del agente y
vincule el resultado a un digest del contenido decidido. Registrar el resultado
sin contraseña, derivado reutilizable ni texto sensible. Un resultado positivo
demuestra uso de la credencial registrada; no demuestra identidad física por sí
solo. La cuenta local separada D05 y las pruebas negativas en el equipo objetivo
siguen siendo requisitos antes de habilitar autoridad real.

## Criterios observables

- Fallo de credencial, entrada ausente, decisión distinta, nonce reutilizado,
  log no persistible o aislamiento no comprobado no producen confirmación.
- El agente no recibe la contraseña por prompt, argumento, variable de entorno,
  archivo del repositorio, stdout ni registro.
- La confirmación se vincula a snapshot, digest de decisión, propósito y nonce;
  cualquier cambio exige una comprobación nueva.
- Registro de intentos y resultado sin secreto; capacidad y recuperación
  declaradas. Nunca inferir que el usuario material fue quien escribió la
  contraseña solo por un string de actor.
- La selección del origen de credenciales (almacén propio del backend o cuenta
  Ubuntu) debe quedar cerrada antes de fijar interfaz, oráculos y código.

## Oráculo TDD de la unidad actual

El registro estructurado debe declarar D04 como `CLARIFICATION_RECORDED`,
`authentication=NOT_IMPLEMENTED`, `real_authority_gate=SECURITY_BOUNDARY_UNMET`
y `human_confirmation_enabled=false`. README, ADR y SKILL deben distinguir
explícitamente el log ya publicado del verificador solicitado. El control
negativo es la versión anterior con `choice=LOCAL_AUDIT_LOG_ONLY`, que debe
fallar.

## Secuencia posterior

1. Cerrar origen de credenciales y canal de entrada humano.
2. Escribir contrato y oráculos negativos; observar RED.
3. Implementar núcleo acotado; observar GREEN y regresiones.
4. RDD del candidato exacto, reconocimiento, commit y respaldo solo si cumple.
5. Calibración y frontera de cuenta separada en i3/WSL: NOT_RUN en cloud.

## Estado

RED observado: dos controles fallaron en la versión previa (estado D04 y tres
textos públicos). GREEN observado: 2 controles dirigidos y 45 controles CI.
Decisión sobre origen de credenciales pendiente. Ningún gate de autoridad
habilitado. RDD del candidato exacto pendiente.
