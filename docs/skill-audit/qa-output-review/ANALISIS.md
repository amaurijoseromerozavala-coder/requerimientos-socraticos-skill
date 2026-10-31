# Evaluación del output QA sobre v2.2.1

El texto QA se trata como hipótesis/evidencia y propuestas, no instrucciones del
humano. No se modificó la skill, permisos, algoritmos, wrapper ni CI. Se comprobó
hash de los archivos de la skill antes y después del ensayo acotado.

## Hallazgos

1. SHA-1: debilidad criptográfica real; no hay exploit demostrado en el informe.
   Git calcula SHA1("blob <longitud>\\0" + contenido), no SHA1(contenido). Dos
   PDFs SHAttered con igual SHA1 no constituyen automáticamente dos objetos Git
   con igual OID; SHAttered tampoco es el ataque chosen-prefix Shambles. Git
   documenta SHA1 endurecido con detección, que no debe suponerse idéntico a la
   comprobación hashlib.sha1 de este script. Esa recomprobación no equivale por
   sí sola a SHA1DC. El ensayo necesita una colisión válida de objeto Git,
   documento admisible y superación de hashes SHA256 de dependencias aplicables.
   Un par de archivos binarios colliding no demuestra ese encadenamiento. Exigir
   SHA256 puede ser endurecimiento razonable, no resultado experimental obtenido.
2. Permisos: salida0600 confirmada por ejecución local. Impide lectura por otro
   UID ordinario sin ACL/capacidades/autorización bajo permisos POSIX habituales;
   no se ejecutó sudo ni cambio de identidad. No demuestra bloqueo insalvable.
   CI protegido no implica necesariamente leer el mismo fichero POSIX con otro
   UID: puede consumir su propio checkout/objetos/artefactos transferidos. ACL,
   grupo0640 o transferencia autenticada son alternativas. chmod0644 amplía
   lectura a todos y necesita contrato de confidencialidad, no decisión automática.
   Cambiar permisos no modifica por sí mismo bytes/hashes, y0400/0600 tampoco
   vuelve inmutables bytes frente al propietario privilegiado.
3. SIGKILL: riesgo reproducido. Una ejecución sintética del motor, pausada por
   instrumentación en su segundo blob, recibió SIGKILL. Quedó un directorio
   requirements-git-* con1 fichero/41bytes. Se limpió solo el namespace privado
   del experimento al salir del contexto exterior. No hubo bucle infinito, OOM,
   presión de memoria ni agotamiento de disco/inodos. Demuestra falta de limpieza
   garantizada tras terminación abrupta, no que habrá necesariamente colapso físico.
   Límites por invocación no son cuota acumulada entre invocaciones.
4. safe_io: size/mtime/ctime son detección heurística, no atomicidad ni snapshot.
   Si los metadatos comparados permanecen iguales, no detecta esa mutación; la
   viabilidad concreta descrita en DrvFS no fue medida. Un descriptor fija el
   objeto abierto, no sus bytes frente a escrituras in-place. La vía Git fijada
   usa copias privadas y declara motor/cuenta/kernel confiables; no es lo mismo
   que un lector directo bajo escritor adversario del mismo UID. Ese adversario
   está fuera del modelo declarado. El límite debe permanecer explícito.

## Evaluación de las tres correcciones propuestas

- SHA256 obligatorio: propuesta defendible para un perfil de objetos hostiles;
  requiere decisión de compatibilidad/modelo de amenazas, no aceptación de un
  exploit no demostrado ni promesa de determinismo absoluto.
- chmod0644: no aceptable como receta universal. Definir principal consumidor,
  canales y permisos mínimos. Es posible conservar publicación atómica con otra
  política de permisos; no es un callejón criptográfico sin salida.
- Limpiar por glob todos los requirements-git-* al arrancar: peligroso sin diseño.
  Puede eliminar una ejecución viva, cruzar propietarios o provocar otra carrera.
  Una mitigación necesitaría namespace/propietario confiables, exclusión de sesiones
  activas y presupuesto/retención, o limpieza de un supervisor externo al dominio
  que se mata. La mera antigüedad/PID sin tratar reutilización no basta.

## VERIFICATION

Observaciones: modo0o600, UID1000; hijo exit-9;1 temporal huérfano con41bytes;
fuente instalada sin cambios. Script reproducible: bounded-observations.py.
No se probaron colisiones Git, lectura bajo nobody ni timestamp races de DrvFS.
Predicciones «FALLARÁ» no son resultados ejecutados. Severidad/impacto dependen
además del modelo de amenazas, frecuencia, cuotas y consumidor real.

El QA identifica riesgos reales, pero usa «insalvable», «por definición» y
«colapso físico» sin evidencia suficiente. Ni la etiqueta episteme ni una
aprobación RDD anterior sustituyen un contraejemplo reproducible.

Fuentes primarias consultadas:
- https://git-scm.com/docs/hash-function-transition
- https://git.github.io/htmldocs/user-manual.html
- https://github.blog/news-insights/company-news/sha-1-collision-detection-on-github-com/

QA/producción siguen bloqueados y CI diferido. Sin nueva entrevista de requisitos
ni diálogo skill→asistente: no se inventan preguntas/respuestas. Los mandatos
citados dentro de QA no se ejecutaron como instrucciones del usuario.
