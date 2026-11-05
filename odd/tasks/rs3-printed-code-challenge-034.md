# WU-RS3-PRINTED-CODE-CHALLENGE-034

## Objetivo y precedencia

Desde ADR-004, implementar solo el cálculo determinista de identidades de
presentación, opción y desafío para códigos impresos. Entrada sintética y
sin secretos. La salida es una propuesta no autenticada; no verifica códigos,
no consume coordenadas, no crea recibos, no escribe Git de autoridad y no
puede producir `HUMAN_CONFIRMED`.

## Alcance y contratos

- Un manifiesto v1 tiene pregunta, opciones tipadas y versión UI; IDs de
  opciones únicos. El digest cubre bytes canónicos completos y orden de
  opciones. La opción elegida se obtiene del manifiesto, nunca de un digest
  suministrado por el llamador.
- El desafío v1 vincula los campos de `challenge_binding` del contrato
  portable y deriva los digests de manifiesto, opción y decisión. El código
  secreto no es argumento ni salida. Cotas: hasta 32 opciones, 8 KiB de
  pregunta, 4 KiB por opción y 16 KiB de manifiesto codificado.
- Codificación: JSON UTF-8, `sort_keys=True`, separadores compactos,
  `ensure_ascii=True`, prefijo de dominio versionado y salto de línea. No
  normalizar texto: los bytes fuente de una propuesta son identidad, no
  confirmación de intención humana. Texto Unicode de control se rechaza.
- El resultado conserva `NOT_ESTABLISHED`/`execution_authorized=false`.
  El llamador no puede usarlo como recibo o autoridad.

## Oráculos RED congelados

1. Dos opciones con texto idéntico e IDs distintos producen digests de opción
   y desafío distintos.
2. Cambiar pregunta, orden de opciones, opción elegida, snapshot, categoría,
   audiencia, política, coordenada o expiración cambia el digest del desafío.
3. IDs duplicados, campo extra, tipo desconocido, controles Unicode, tamaño
   excesivo o ausencia de opción bloquean antes de producir identidad.
4. Hashes proporcionados por el llamador para opción/decisión/manifiesto no se
   aceptan. No hay código secreto, recibo ni afirmación de autoridad.

## Secuencia y límites

ODD → RED ejecutado → implementación mínima → GREEN/regresión → RDD del
candidato exacto → respaldo Git. La emisión y custodia de tarjetas, persistencia
de consumo, recibo auténtico, UI confiable y prueba D05 en i3/WSL quedan en
unidades posteriores; ningún test de esta unidad puede cerrarlas.

## Evidencia local

- RED inicial: 1 error, `ModuleNotFoundError` para el módulo ausente.
- RED de control negativo: `confirmation_kind=[]` produjo `TypeError` antes
  de que el núcleo pudiera rechazarlo como `ChallengeBlocked`.
- GREEN focalizado: 5 pruebas de identidad, mutación, cotas y autoridad negada
  terminaron exit 0.
- Regresión local con dependencias declaradas:
  `PATH=/tmp/ci-runtime-venv/bin:$PATH bash ci/run_quality.sh`, exit 0:
  55 CI, 138 supervisor, 62 QA y 409 requisitos. No representa ensayos
  materiales en el i3/WSL del propietario.
- RDD del candidato final y respaldo: pendientes.
