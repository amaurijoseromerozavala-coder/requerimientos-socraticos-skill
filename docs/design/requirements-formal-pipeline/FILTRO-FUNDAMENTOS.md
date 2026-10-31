# Filtro de fundamentos y derivación de invariantes

Estado: ampliación documental DRAFT; sin implementación, demostración ni ensayos.
Petición humana literal: «Usar axiomas como filtro iniciando por los axiomas de
las matemáticas axiomas de la lógica axiomas de la física axiomas del dominio y
axiomas del hardware para definir las invariables de manera correcta».
Se conserva el propósito; «invariables» se normaliza aquí a invariantes sin
atribuir una confirmación humana adicional de cada decisión técnica propuesta.

## Clases de fundamentos: no mezclar autoridad y evidencia

| Capa | Representación propuesta | Condición para usarla |
|---|---|---|
| Lógica y matemáticas | Lógica elegida, tipos, teorías y axiomas declarados | Semántica compatible, procedencia y dependencias auditables |
| Física | Ley/modelo aplicable, hipótesis y condiciones de validez | Referente material definido, fuente y aplicabilidad justificada; contraste cuando corresponda |
| Dominio | Definiciones, reglas normativas y restricciones empíricas separadas | Autoridad humana para políticas; evidencia para hechos; alcance explícito |
| Hardware/entorno | Capacidades, configuración, contratos de plataforma y presupuestos | Distinguir dato declarado de medición; versión, unidad, fecha y procedencia |

No existe un único conjunto de «todos los axiomas matemáticos» que se añade
indiscriminadamente. Lean usa una teoría de tipos; Z3 usa las teorías de cada
consulta. La traducción entre ambos debe preservar el significado. No afirmar
que se probó consistencia global de los fundamentos mediante una llamada SAT.
Las leyes físicas y características del hardware son conocimiento/modelos y
restricciones de ingeniería revisables, no axiomas incuestionables del mundo.
Se incluyen solo capas aplicables; no añadir física decorativa a una regla booleana.
El orden solicitado sirve como revisión de fundamentos, no como permiso para
que una premisa sin fuente anule automáticamente un requisito o una decisión.

## Registro mínimo de premisas

Cada premisa identifica id, clase, expresión, referente, fuente/autoridad, ámbito,
tipos/unidades, versión, supuestos, estado de evidencia y criterio de revisión.
Clasificación: declarado, observado, hipótesis, decisión o resultado formal.
Un dato desconocido no se rellena con una constante conveniente. Las conclusiones
que dependan de él deben conservar esa condición o quedar inconclusas.

Separar D (restricciones de entrada), T (transiciones) e I (propiedad que se
quiere demostrar). Una obligación de respuesta no puede introducirse en D para
eliminar justamente las entradas donde el sistema la incumpliría.
El límite de 32 booleanos es límite del proyecto, no axioma matemático ni prueba
de cobertura. No obligar a llegar a 32, ni recortar semántica para encajar.

## Derivación y contraste del invariante

1. Precisar la propiedad requerida y el estado observable al que se refiere.
2. Identificar premisas aplicables y cuestionar su fuente y supuestos.
3. Comprobar tipos/unidades, compatibilidad y factibilidad de un estado inicial.
   Dominio vacío o inconsistencia detectada bloquean conclusiones dependientes;
   no utilizar verdad por vacuidad como resultado favorable.
4. Definir Init(s), T(s,s') e I(s) por separado, con trazabilidad al requisito.
5. Obligaciones de inducción: Init(s) implica I(s), y
   I(s) y T(s,s') implican I(s'). Si falla la segunda, revisar contraejemplo:
   podría ser estado inalcanzable y requerir fortalecer el invariante de apoyo,
   no demostrar por sí solo una ejecución real incorrecta.
6. Buscar también trazas alcanzables y contraejemplos, con límites declarados.
7. Revisión semántica humana: que la fórmula exprese la necesidad confirmada.
8. Ensayos autorizados comprueban correspondencia con implementación/entorno.

No introducir I como axioma para declarar que quedó demostrado. Una propiedad
que solo vale en el momento de inicio se formula sobre el evento/transición;
no se transforma sin permiso en condición permanente de todo estado posterior.
Progreso, plazos y recuperación requieren propiedades temporales y supuestos
adicionales; no quedan cubiertos por invariantes de estado solamente.

## Ejemplos y controles negativos especificados, NOT_RUN

- Una transición de inicio debe satisfacer sus condiciones necesarias conforme
  al requisito confirmado. Cambiar esas condiciones después no se interpreta
  automáticamente como violación retroactiva: semántica temporal explícita.
- Sumar cantidades con unidades distintas debe rechazarse o exigir conversión
  definida. No identificar enteros matemáticos con enteros de máquina sin modelar
  desbordamiento; tampoco confundir aritmética exacta con flotante.
- 6GB de WSL son configuración declarada, no memoria libre garantizada. Zram y
  swap no se suman como RAM física disponible. Un presupuesto necesita medición
  y acuerdo; no se deriva un plazo de ejecución de la frecuencia del CPU.
- Premisas contradictorias, exclusión sin fuente o I asumido como axioma deben
  impedir presentar una demostración como cumplimiento independiente.

Aplicación Bunge/Popper: justificar referentes y mecanismos; formular predicciones
contrarias; contrastar instrumento y supuestos antes de atribuir causalidad.
Una prueba formal demuestra consecuencia respecto de premisas, no su verdad
empírica ni toda intención humana. Conservar falsadores, casos adversos e historial.

## Límites y cierre

Documento especificado, sin prueba Lean, consultas Z3 ni ensayo de hardware nuevo.
La política de axiomas aceptados en Lean, mapeo de teorías y criterios de evidencia
requiere diseño detallado y revisión antes de implementarse. No instalar ni
modificar skills de producto por este addendum. RDD documental no sustituye esas
obligaciones y no autoriza CI ni producción.
