# Registro de investigación

Fecha de consulta según workspace: 2026-10-27. Fuentes primarias vivas; no lockfile.
Alcance: capacidades y licencias declaradas. No acredita uso ni rendimiento local.

| ID | Fuente consultada | Afirmación utilizada |
|---|---|---|
| S1 | https://www.python.org/psf/license/ | Python es open source; historial de licencias PSF y avisos. |
| S2 | https://github.com/python-jsonschema/jsonschema/blob/main/pyproject.toml | Validador JSON Schema Python, licencia MIT declarada. |
| S3 | https://github.com/Z3Prover/z3 y https://microsoft.github.io/z3guide/programming/Parameters/ | Z3 MIT, APIs Python; opciones de tiempo/recursos. |
| S3b | Context7 /microsoft/z3guide; origen https://github.com/microsoft/z3guide/blob/main/website/docs-programming/02%20-%20Z3%20Python/02%20-%20advanced.md | Extracción de núcleo incompatible mediante supuestos, no necesariamente mínimo. Context7 también devolvió Parameters.md para timeout/rlimit. |
| S4 | https://github.com/pytest-dev/pytest y https://docs.pytest.org/en/stable/license.html | Framework de pruebas MIT. |
| S5 | https://github.com/HypothesisWorks/hypothesis/blob/master/LICENSE.txt y https://hypothesis.readthedocs.io/en/latest/stateful.html | MPL-2.0 con excepciones; generación de secuencias. README https://github.com/HypothesisWorks/hypothesis describe reducción de fallos. |
| S6 | https://github.com/lark-parser/lark | Parser de gramáticas, licencia MIT. |
| S7 | https://github.com/tlaplus/tlaplus/blob/master/README.md y https://github.com/tlaplus/tlaplus/blob/master/LICENSE | Herramientas TLA+/TLC, MIT. https://docs.tlapl.us/using%3Atlc%3Astart describe TLC como explorador explícito de estados. |
| S8 | https://github.com/cvc5/cvc5 y https://github.com/cvc5/cvc5/blob/main/COPYING | Motor SMT abierto y texto de licencia; https://cvc5.github.io/tutorials/beginners/introduction.html declara BSD-3-Clause y distingue distribución ampliada GPL; tutorial primario abierto. Licencia exacta de distribución/dependencias no fijada. |
| S9 | https://github.com/pysmt/pysmt y https://pysmt.readthedocs.io/en/latest/development.html | Capa SMT, Apache-2.0. |
| S10 | https://alloytools.org/faq/what_kind_of_analysis_does_the_alloy_analyzer_do.html y https://github.com/AlloyTools/org.alloytools.alloy/blob/master/LICENSE | Búsqueda de modelos y contraejemplos; aviso raíz que declara MIT vigente con Apache no vigente. No simplificar a Apache-2.0. |
| S12 | https://github.com/NASA-SW-VnV/fret/blob/master/README.md?plain=1 y https://ntrs.nasa.gov/citations/20200001989 | FRET: lenguaje restringido, formalización y explicaciones; README declara Apache-2.0 para v3. No se extrapola a versiones antiguas ni se presupone integración EARS. |
| S11 | https://smt-lib.org/ | Lenguaje y teorías comunes para intercambio con solvers. |

## Límites de la investigación

Fuentes consultadas con MCP web y Context7. Búsquedas de licencias complementadas
con lectura de documentación/repositorios; capacidades y licencias se contrastan en las fuentes indicadas. Un intento de otra ruta LICENSE de Alloy devolvió 404;
no se usa como evidencia. Referencias cloud adicionales de la skill de arquitectura
no se pudieron leer; se usan las instrucciones principales y referencias locales.
No se descargaron dependencias ni se ensayó instalación en i3/WSL.
Antes de adoptar: fijar versiones/artefactos compatibles, inventario transitivo,
licencias y avisos correspondientes. Consultas futuras pueden observar cambios.
