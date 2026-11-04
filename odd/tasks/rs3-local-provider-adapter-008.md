# WU-RS3-LOCAL-PROVIDER-ADAPTER-008

## Objetivo y precedencia

Integrar la compuerta JSON de WU-RS3-WEAK-MODEL-ADMISSION-006 con la supervisión
POSIX existente para un proveedor **local simulado**. No se conectan API,
cuentas, claves, pagos ni modelos externos. Este trabajo prepara una interfaz
sin afirmar portabilidad universal.

## Alcance y contrato

Un comando fijo y confiable, con ejecutable absoluto, recibe como máximo 8 KiB
de solicitud sintética por stdin. El adaptador usa un plazo <=30 s y conserva
como máximo 16 KiB por canal. stdout se analiza solo después de confirmar
salida/limpieza; stderr queda separado y no se publica. Una instancia con
limpieza incierta queda bloqueada. La salida no contiene prompt ni texto bruto
del proveedor y siempre conserva `execution_authorized=false`.

## Oráculos TDD congelados

- Proveedor válido: propuesta únicamente para revisión, sin autoridad.
- stderr con aviso y stdout válido: conservar la propuesta sin mezclar canales.
- Plazo agotado, código no cero, señal, fallo de lanzamiento o limpieza incierta:
  estado de infraestructura explícito, nunca propuesta ni culpa del PRD.
- stdout vacío, truncado o mayor que el presupuesto: rechazo explícito, sin
  analizar un prefijo como JSON válido.
- Tras limpieza incierta, la misma instancia no admite segunda invocación.
- Comando relativo, payload no byte o excesivo y plazo inválido: rechazo antes
  de lanzar un proceso.

RED antes de implementar, GREEN focalizado y suites afectadas, RDD exacto,
respaldo Git tras reconocimiento. No afirmar que tiempos de espera sean tiempo
real ni que los tests simulen el hardware i3/WSL bajo carga.

RED observado: `ModuleNotFoundError: local_provider_adapter`. Tras el primer
GREEN focalizado de cinco tests, dos pruebas adicionales detectaron que un
segundo pedido inválido ocultaba `INFRA_LOCK` y que un registro incompleto del
supervisor lanzaba `KeyError`. Ambas fallaron antes de su corrección. GREEN
focalizado final: siete tests. Las suites completas se registran antes de RDD.
GREEN completo observado: 331 tests de Requerimientos Socráticos y 54 CI
locales pasaron; un test CI dependiente del ZIP externo quedó omitido
explícitamente. El gate de marcadores históricos reportó cero hallazgos.

## Riesgos y límites

El ejecutable es seleccionado por un llamador confiable, nunca por la salida
del LLM. El grupo de procesos no contiene descendientes que se separen; el
núcleo supervisa al hijo directo bajo límites declarados. No hay proveedor
cloud ni evaluación de coste/cuota. D03/D05 y producción siguen bloqueados.
