# Corrección QA Inquisidor0.1.1
Humano: «Realiza las mejoras usa gentle-ai».
Alcance: separar MemoryError/OSError/RecursionError interceptados de errores de entrada.
Infraestructura: exit3, INFRA_FAILURE, documento NOT_ASSESSED, evento/veredicto null,
diagnóstico tipo/errno, causa no determinada. Datos inválidos conservan exit2/REJECT_INPUT.
No se agregan firmas, supervisor externo, CI, producción ni ensayos de agotamiento.
Salida JSON best effort explícita. No prometer emisión tras terminación abrupta.
## Verify
7 controles nuevos RED:5fallos y2errores porcamposausentes antes de corregir.
50 pruebas GREEN local e independiente. Excepciones controladas mediante mocks;
no simulamos que se haya agotado hardware. Recibos en este directorio.
