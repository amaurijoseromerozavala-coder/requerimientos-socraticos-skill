# Activación portable en Gentle Pi y Gentle Shell (Linux/WSL)

## Qué se instala

Una skill es un contrato y sus helpers; instalarla no añade subcomandos al binario
upstream de Gentle AI. `gentle-ai requirements activate` solo existe cuando se
usa nuestro wrapper opcional. La ruta fiable para Pi es la entrada propia:

```bash
bash "<skill_root>/scripts/requirements" --help
```

`<skill_root>` es la ubicación real del SKILL.md cargado, no un texto que se copia
literalmente ni una ruta cloud asumida. Mantener scripts, referencias y assets
juntos. Las rutas con espacios y symlinks son admitidas en Linux/WSL.

## Preparar el intérprete una vez

Desde la raíz del repositorio clonado, si el operador autoriza preparar el entorno:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
REQUIREMENTS_PYTHON="$PWD/.venv/bin/python" \
  bash skills/requerimientos-socraticos/scripts/requirements activate --path "$PWD"
```

Python 3.12 es la versión de referencia comprobada. No se promete compatibilidad
con todas las versiones ni disponibilidad de dependencias en todos los equipos.
Desde 2.4.8, conservar el clon oficial y configurar Pi para cargar la skill desde
él; una copia aislada sin repositorio no acredita source_checkout y bloquea
workers. REQUIREMENTS_PYTHON selecciona el intérprete, no sustituye el clon. No hay instalador automático de paquetes.

Orden sin selección explícita: `.venv/bin/python` de la skill, `.venv/bin/python`
del repositorio y entorno configurado en XDG_DATA_HOME para la skill. No hay
fallback implícito a python3 del PATH. Un REQUIREMENTS_PYTHON definido pero
inválido/vacío se rechaza, aunque exista otro entorno. La ayuda no necesita Python.

## Aplicar a otro proyecto

Pi debe obtener la ubicación instalada de la skill y conservar el proyecto actual
como destino `--path`. Invocar la entrada por su ruta absoluta con el intérprete
seleccionado. No cambiar el proyecto objetivo por el repositorio de la skill.
Si faltan intérprete/helpers, informar INTERPRETER_UNAVAILABLE/HELPER_UNAVAILABLE;
continuar solo con entrevista/documentos, sin inventar sondeo ni autorización.

## Diagnóstico y correcciones con Pi

1. Leer AGENTS.md del proyecto y confirmar alcance existente antes de editar.
2. Ejecutar el preflight por la entrada propia; registrar JSON y errores. No
   repetir un subcomando upstream desconocido ni declararlo instalado.
3. La skill toma requisitos, interroga, contrasta y documenta. Si el humano ya
   autorizó correcciones, el agente de desarrollo puede implementarlas dentro
   de ese alcance y de los gates del proyecto, sin convertir al archivo SKILL.md
   en un supervisor de comandos.
4. Aplicar ODD, RED/GREEN y RDD al candidato exacto. Si el runtime pide nuevo
   consentimiento, reenviarlo. Con RDD ausente/no aprobado no cerrar ni publicar.
5. Publicar tras RDD solo si el usuario autorizó ese destino. En este proyecto
   existe autorización permanente de respaldo por unidad, no de CI/producción.

`READY_FOR_LIVE_ADMISSION` no reserva RAM, no calibra el i3 ni limita todo comando
que ejecute Gentle Shell. Solo los helpers con admisión implementada vuelven a
verificar condiciones. El supervisor integrado sigue incompleto. Cualquier
ensayo de carga necesita su alcance y límites; no se deduce del preflight.

## Wrapper opcional

Desde el repo: `./bin/gentle-ai requirements activate --path "$PWD"`.
Para delegar otras operaciones, establecer GENTLE_AI_UPSTREAM a la ruta absoluta
del binario real (no al wrapper). El wrapper no altera PATH ni credenciales.
No reemplazar globalmente el Gentle AI existente para poder usar esta skill.

## Evidencia WSL y capacidad anfitriona

Para trabajo que depende de ampliar disco, pasar `--storage-required-bytes N`
con bytes positivos. El recolector Windows aún no está implementado: host_volume
es UNKNOWN y ese trabajo queda bloqueado, incluso si Linux muestra mucho espacio
y el perfil de memoria es viable. Un dato pegado por el usuario se conserva como
histórico. No se reutiliza como disponibilidad actual. No se cambia swap ni zRAM.
El schema de activación es ahora 1.1.0; registros antiguos 1.0.0 no contienen estas
obligaciones y no deben presentarse como evidencia del nuevo contrato.
