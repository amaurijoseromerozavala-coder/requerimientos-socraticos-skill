# QA Inquisidor 0.1.3-alpha
Humano: Has las correcciones pertinentes.
Observación de declaraciones FAIL independiente de admisión documental. CLI
examina únicamente evidence[*].outcome de JSON ya decodificado, máximo128 filas,
sin I/O adicional. NOT_ASSESSED si no se decodifica o no se puede interpretar;
exploración parcial no afirma ausencia. No autentica evidencia ni autoridad,
no cambia veredicto ni autorización. Mantener REJECT_INPUT/INFRA_FAILURE.
TDD: 8 tests nuevos RED (9 errores contando subtests); 62 tests GREEN.
Revisión independiente separada en independent.md/log. Sin CI ni estrés físico.
