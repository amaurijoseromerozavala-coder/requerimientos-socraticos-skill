# Integración documental de requisitos, QA y supervisor

Humano solicita integración en esquema existente y aporta ZIP. No es autorización de implementación/CI. Catálogo140requisitos/19grupos conservado;5hashes de archivos válidos. Matriz87locales/44futuros/9opcionales;22ajustes contractuales. Propuestas no ratificadas.

Diseño: docs/requirements/integracion-requisitos-qa-supervisor/diseno-integrado.md. Q-INT-001 dependencias externas pendiente. No modificación de skills activas ni contratos supervisor. Engram resumen de progreso, no autoridad.

Actualización: humano confirmó A+B+C progresivas, supervisor ampliado, adaptadores registrados, revisión y aprobación de versión/permisos, ejecución dentro de tareas autorizadas, secuencial y sin reintentos automáticos. Decisiones registradas con respuestas literales. Pendiente Q-INT-008 espacio de escrituras; no inferir rollback. No implementación.

INT-D08..11: espacio aislado; conservar resultados fallidos; incorporación automática en tarea autorizada tras criterios; cambio de base detiene incorporación y exige reevaluación. No commit/push/deploy ni implementación actual. Q-INT-012 recuperación de incorporación parcial pendiente.

INT-D12..14: recuperación condicionada; presupuesto tarea+global; ajustable con preflight de capacidad antes de pedir ampliación. No cifra fija elegida. Diseño propone revalidación al reanudar y contabilización de reservas; mecanismos pendientes, NOT_RUN. Q-INT-015 alcance de aprobación tarea/global pendiente.

INT-D15..19 confirmadas: aprobación conjunta explícita tarea/global; estimación inicial supervisor; exploración acotada autorizada cuando falta estimación; solo inspección/muestras sin ejecutar proyecto; agotamiento detiene y permite solicitud de ampliación tras preflight.19decisiones registradas; diseño aún incompleto y sin implementación.

INT-D20/21: revocación ordinaria diferida a final de tarea completa con múltiples invocaciones autorizadas; ninguna tarea nueva. Q-INT-022 incorporación al proyecto después de revocar pendiente. Solo diseño.

INT-D22: A conservar resultados aislados tras revocación; incorporar requiere autorización nueva. Excepción explícita a automáticaINT-D10. Permanece abierto caso revocación durante incorporación ya iniciada, sin fingir atomicidad.

INT-D23: humanoB detiene nuevas escrituras de incorporación ante revocación; aplica recuperación condicionadaINT-D12, bloquea si no es verificablemente segura. Política resuelta, mecanismo de recepción y coordinación pendiente. Solo diseño.

Trabajo Gentle iniciado:4.2.0/RDDON/preflightcloud. Candidato-v0.1 contiene23EARS,contratos,gate128valoraciones y proyecciónFSM9/13. InterrogadorT01 real;3hallazgos independientes corregidos. No READY/globalFSM incompleta. RDD13archivos1133líneas medio requiere consentimiento para sha256:551a7a33c412f242c3c2c69437f46ef72ce992dec5ebed848af5af28f98384c2. No implementación.

RDD autorizado mediante Granted: resiliencia y fiabilidad completadas, APPROVED_AND_ACKNOWLEDGED para candidato 551a7a33. 13/13 hashes preservados. Observación R3-001 no bloqueante: falta cobertura automatizada del manejador global de revocación y control negativo. Pendiente posterior, candidato no alterado. Revisión estática sin ejecución de tests. DRAFT y brechas técnicas continúan; ver docs/skill-audit/integration-candidate-01/RESULTADO.md.
