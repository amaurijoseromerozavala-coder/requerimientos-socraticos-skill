# QA Inquisidor 0.1.2-alpha
Humano: Haz las mejoras usa gentle-ai.
Incluir schema_version y limitations en inputs_digest. Rechazar vigencia de digests
anteriores; no recalcular automáticamente juicios. Declarar authority_verification
NOT_PERFORMED y execution_authorized false en toda salida JSON. Identidad declarada
no autenticada; ningún evento autoriza ejecución. Sin firmas ni CI ni producción.
TDD: 54 tests, cuatro nuevos RED (3 fallos y 1 error) antes de corregir; 54 GREEN.
La revisión independiente se registra separadamente. No garantía RSS/OOM.
