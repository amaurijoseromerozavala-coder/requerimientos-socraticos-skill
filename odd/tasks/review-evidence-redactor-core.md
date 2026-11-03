# WU-SEC-REDACTOR-CORE-001 — saneamiento verificable de evidencias

## Objetivo y alcance

Proveer una transformación local determinista para representaciones públicas
de revisión que puedan contener valores sensibles. Esta unidad incorpora solo
el módulo y sus controles con datos ficticios; no modifica recibos existentes,
el historial Git, la captura del runtime ni el CI remoto.

## Oráculos ODD → TDD → RDD

1. El control RED debe fallar por ausencia del módulo.
2. Un valor ficticio duplicado en comando, argumentos y campos anidados debe
   desaparecer por completo de la copia transformada.
3. Las claves directas `token` y `api-key` también se sanean. Los bytes
   ordinarios deben conservarse; JSON inválido con marcador sensible se rechaza.
4. La suite local afectada, `git diff --check` y la revisión RDD del candidato
   exacto deben pasar antes del commit local. Sin recibo nativo no se publica.

Los originales permanecen bajo custodia privada. La transformación no prueba
caducidad ni revocación de valores ya publicados. Ningún valor histórico se
transmite al revisor en esta unidad.
