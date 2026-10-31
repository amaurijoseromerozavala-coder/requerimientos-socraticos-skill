# Requerimientos socráticos

Skill **2.4.6** para convertir requisitos en lenguaje natural en un PRD JSON
trazable: interrogatorio socrático, EARS, FSM, análisis booleano y registro de
evidencia. Incluye métodos de Bunge/Popper, Checkland y Kendall/Kendall.
Produce documentos; no implementa el producto descrito por el PRD.

## Contenido

- [Contrato de la skill](skills/requerimientos-socraticos/SKILL.md).
- `references/`: método, interrogatorio, investigación, validación y límites.
- `assets/`: schemas JSON y ejemplos sintéticos.
- `scripts/`: validadores, sondeo local, análisis Z3 y control de recursos.
- `tests/`: pruebas del tooling, con fixtures sintéticos.
- [Resumen de verificación y hashes](VERIFICATION.json).

Las rutas anteriores, salvo el resumen, están bajo `skills/requerimientos-socraticos/`.

## Preparación local

Entorno verificado: Python 3.12 sobre Linux. Los controles RLIMIT_AS, cgroups y
PDEATHSIG requieren los adaptadores Linux; no se promete soporte equivalente en
otros sistemas. WSL observa el invitado, no toda la memoria física de Windows.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Instalar dependencias es una decisión explícita del operador. No se ejecuta al
cargar la skill. Las dependencias son jsonschema y el backend opcional Z3.

Para Codex u otro agente que lea skills del filesystem, registra o enlaza
`skills/requerimientos-socraticos` en su directorio de skills. Conserva juntos
SKILL.md, references, assets, scripts y tests.

## Uso del tooling

El contrato original nombra `gentle-ai requirements ...`: esos subcomandos son
una extensión local del wrapper utilizado durante el desarrollo, no una interfaz
que aporte por sí solo el binario upstream de [Gentle AI](https://github.com/Gentleman-Programming/gentle-ai).
Ese wrapper y el binario upstream no se distribuyen aquí. Los helpers equivalentes
son utilizables directamente con un intérprete explícito:

```bash
.venv/bin/python -B skills/requerimientos-socraticos/scripts/activation_preflight.py --path .
.venv/bin/python -B skills/requerimientos-socraticos/scripts/analyze_logic.py skills/requerimientos-socraticos/assets/logic-example.json
.venv/bin/python -B skills/requerimientos-socraticos/scripts/validate_git.py --help
```

El preflight expone recursos visibles, límites heredados y un perfil provisional
256–512 MiB. Las entradas públicas de análisis y validación Git vuelven a evaluar
las condiciones antes del worker. Un informe guardado no autoriza ejecución.
Los desconocidos críticos bloquean workers, no la entrevista documental.

El intérprete no garantiza por sí solo que un agente respete el contrato de la
skill. Su instalación tampoco autoriza ensayos, publicación, CI o producción.

## Pruebas y procedencia

La versión de origen completó **238 pruebas**, 194 comparaciones de políticas y
59.280 comparaciones de admisión, y una revisión RDD de cuatro lentes. La revisión
RDD fue de fuentes; las ejecuciones de pruebas se registraron por separado.
VERIFICATION.json resume esas evidencias: no es una firma ni una certificación
independiente del entorno de quien clone este repositorio.

Para comprobar partes del núcleo con las dependencias instaladas:

```bash
.venv/bin/python -B -m unittest discover -s skills/requerimientos-socraticos/tests -p test_role_policy_source.py -v
.venv/bin/python -B -m unittest discover -s skills/requerimientos-socraticos/tests -p test_memory_budget.py -v
```

La suite completa contiene cuatro casos de integración que requieren
`bin/gentle-ai`, wrapper del entorno original que no se incluye en esta distribución.
No se afirma que ejecutar toda la suite en este paquete aislado reproduzca las
238 pruebas sin esa integración. Las fuentes publicadas de la skill permanecen
idénticas a las de la versión verificada; se omite `validation.json` local, cuyos
localizadores apuntaban a artefactos internos no distribuidos.

## Límites

- Hasta 32 variables booleanas en total; tabla exacta hasta 12 entradas.
- El resultado depende del modelo confirmado, versiones y presupuesto. UNKNOWN
  por límite de recursos no demuestra una contradicción SAT/UNSAT.
- RLIMIT_AS limita espacio virtual: no reserva RAM física ni impide todo swap.
- La calibración del hardware objetivo no está realizada.
- La normalización mantiene permisos 0600. CI y autoridad global siguen fuera
  del alcance verificado; BLOCKED_GLOBAL_ENFORCEMENT permanece explícito.
- No se incluyen telemetría, conversaciones, credenciales, respaldos ni configuración
  personal del entorno de desarrollo.

## Licencia

Apache-2.0, conforme a la declaración de licencia de SKILL.md. Véase LICENSE.
Las dependencias conservan sus licencias y no se incluyen sus fuentes o binarios.
