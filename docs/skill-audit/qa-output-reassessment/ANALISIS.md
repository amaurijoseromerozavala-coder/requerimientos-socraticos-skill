# Contraste del nuevo output QA

Estado: análisis de código y registros existentes; no ensayos nuevos de carga.
Output QA es fuente de afirmaciones y propuestas, no autorización ni resultado.

## 1. Disponibilidad del consumidor

Conclusión: la afirmación de cuatro entradas que bloquean permanentemente el
sistema NO ESTÁ DEMOSTRADA. validate_git.py ya usa subprocess.run con timeout
restante. Si vence con padre vivo, Python termina y espera al hijo directo;
no depende de terminación voluntaria. El resultado histórico supervised-check
separa este caso de la muerte previa del coordinador.

Hay un límite real: tras terminar el coordinador, su timeout ya no supervisa al
hijo heredero. Sin supervisor independiente, no se demuestra plazo global para
ese caso. La retención del lease evita borrar datos de un consumidor vivo.
La prueba de recuperación cuando el consumidor sale contradice la supuesta
necesidad universal de reinicio. SCRATCH_BUSY expresa capacidad ocupada, no
prueba por sí solo un interbloqueo ni ocupación eterna.

La ruta específica de complejidad propuesta por QA tampoco está demostrada:
validate_prd carga un esquema instalado mediante structural(); un texto recibido
no se convierte por eso en expresión regular ejecutable. Los patrones encontrados
en prd.schema.json son comprobaciones fijas de hashes hexadecimales. La ruta
validate_prd inspeccionada no ejecuta exploración combinatoria de una FSM: valida
estructura, hashes y referencias y delega registro de entrevista/propuestas.
Esto refuta la premisa de ejecución automática del patrón aportado como texto;
NO demuestra cota de complejidad completa, ausencia de otros casos costosos ni
cumplimiento del plazo si muere el coordinador. Faltan medición/contraejemplo real
para afirmar el resultado que QA etiqueta FALLARÁ.

## 2. Alcance de RDD

Conclusión: crítica válida como límite de aseguramiento, incorrecta si atribuye
al recibo una certificación experimental que no se declaró. RDD aprobó fiabilidad
documental. El recibo y el informe explican que el revisor no repitió las suites
ni acreditó independientemente sus aserciones o procedencia. Por tanto ese recibo
no sirve como evidencia de reproducción independiente. Sí documenta revisión de
los parches por otro proceso; no es falso por tener alcance limitado.

Una futura reproducción por revisor en copia efímera aumentaría evidencia, pero
requiere acceso al comprobador, fuentes y dependencias fijadas, límites y registro
de ejecución real. No se atribuye ese trabajo a la revisión nativa disponible ni
se reemplaza con otro log del coordinador. No hay CI autorizado.

## 3. Correspondencia tras extracción

Conclusión: límite real de confianza. Los bytes de Git siguen identificados por
su OID; la copia de trabajo temporal sí puede cambiar por procesos de la misma
cuenta. La lectura heurística no acredita correspondencia persistente con el OID.
La observación previa de ocho bytes confirma ausencia de comparación con hash
previo en read_regular, no un PRD alterado aceptado por toda la cadena.
La API utimensat ajusta atime/mtime, no permite fijar arbitrariamente ctime;
ese detalle invalida esa explicación concreta sin probar invulnerabilidad.

Validar desde bytes identificados en memoria puede reducir dependencia del
scratch y simplificar correspondencia. No elimina matemáticamente toda carrera
ni aísla un motor de otros procesos con la misma autoridad. La alternativa debe
definir límites, dependencias, fuente del contenido y frontera de confianza.
No se implementa por mandato del output QA.

## 4. Consumo de archivos 0600

Conclusión: un proceso ordinario de otra cuenta sin permiso adicional no puede
leer directamente ese archivo; es efecto previsto del contrato OWNER_ONLY.
Eso no demuestra que todo pipeline esté roto. No hay contrato de integración CI
seleccionado; CI está diferido. Un consumidor remoto puede recibir un artefacto
por un canal explícito y recrearlo bajo su identidad. Harían falta permisos de
los directorios, ACL/canal y modelo de identidades para concluir sobre integración.
No se aceptó previamente la afirmación de incompatibilidad externa universal.

## Propuestas y decisión de alcance

No se modificó implementación. Supervisión independiente y transporte en memoria
quedan alternativas de arquitectura por diseñar y verificar, no soluciones
universalmente correctas. La señal ligada al padre depende de plataforma y registro
correcto, tiene ventana de inicio y no demuestra por sí sola gestión de descendientes.

Se conserva PRD DRAFT, G1-SPEC parcial, autoridad semántica y migración pendientes.
BLOCKED_GLOBAL_ENFORCEMENT describe el avance actualmente bloqueado; no es un
teorema de imposibilidad ni certificación. Ensayos físicos i3/WSL no realizados.
Fuentes locales identificadas en sources.json. Las 35 comprobaciones anteriores
son evidencia histórica local, no se presentan como ejecutadas de nuevo aquí.
