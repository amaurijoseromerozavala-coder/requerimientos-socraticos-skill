# Despliegue portable de autoridad RS3

La skill puede **preparar y evaluar** un despliegue. No crea cuentas, emite
códigos reales, controla el navegador ni concede autoridad. La activación
`requirements activate` observa capacidad de trabajo documental y memoria;
**no establece D05**, aun cuando informe `READY_FOR_LIVE_ADMISSION`.
El contrato de perfiles es
[`rs3-authority-deployment.json`](../assets/rs3-authority-deployment.json).

## Perfil elegido y alternativas

El primer destino elegido por el humano es Linux/WSL con **agente y guardián
bajo UIDs distintos**. Es un objetivo de implementación y falsación, no un
estado listo. El perfil de UID único, incluido el cloud env actualmente
observado, queda bloqueado para autoridad real. Un cloud gestionado puede
ejecutar pruebas sintéticas/documentales si carece de cuenta y canal humano
independientes; otro cloud es `TARGET_UNVERIFIED`, no bloqueado por su nombre
ni aprobado por parecerse a este. Windows con cuentas y ACL propias permanece por diseñar y
ensayar; entorno desconocido bloquea.

## Replicar el entorno sin fijarlo a un hardware

La unidad portable es un **runtime lógico versionado**, no una copia de la RAM,
CPU, kernel o permisos de una máquina. Cada instalación debe obtener un commit
de origen identificado, comprobar arquitectura/ABI y Python compatibles,
reconstruir un entorno limpio con dependencias transitivas y herramientas
fijadas por versión **y hash**, ejecutar sus pruebas y sondear recursos del
host. Solo después selecciona presupuestos viables. Un equipo más potente no
eleva automáticamente límites ni autoridad; uno insuficiente devuelve
`INCONCLUSIVE`/`BLOCKED` según el gate. El método de reconstrucción puede
variar por plataforma (venv, paquete o imagen), pero debe satisfacer el mismo
contrato comprobable. Docker no es requisito implícito.

**Brecha actual:** `requirements.txt` fija dependencias directas, pero no
incluye un lock de todas las transitivas con hashes para cada plataforma;
`Dockerfile` tampoco fija el digest de la imagen base. Por tanto, este
repositorio aún no demuestra reproducción byte a byte del runtime en cualquier
hardware. La instalación portable debe registrar exactamente qué artefactos
resolvió y rechazar una variante no verificada; no puede presentar la salida
de CI Ubuntu como calibración de otro host. Las cuentas, ACL, origen de UI y
custodia de claves se prueban **de nuevo** en cada instalación: no viajan con
un venv o una imagen.

La ruta del código de la skill debe ser legible para ambos roles sin hacer
escribible al agente el almacén del guardián. Un clon Git del proyecto bajo
el UID del agente **no** es el Git de autoridad. Un mismo UID puede leer y
alterar archivos `0600/0700` que posee; esos permisos no crean D05.

## Preflight material antes de cualquier instalación real

1. Identificar OS, host, UID real/efectivo, propietarios y rutas reales del
   código, almacén y Git privado. Registrar UNKNOWN cuando no se observe.
2. Exigir cuenta de guardián distinta, sin elevación utilizable por el agente,
   y comprobar desde la cuenta del agente la imposibilidad de leer o escribir
   almacén, clave de recibos y Git privado. Un resultado favorable de
   `rs3_d05_agent_boundary_preflight.py` es solo observación local; también
   requiere pruebas negativas de `sudo`, capacidades, sockets, IPC y control
   del proceso, conforme al entorno autorizado. No intentar elevarse ni crear
   cuentas sin autorización específica.
3. En WSL, comprobar si el agente puede usar interop (`wsl.exe`, PowerShell,
   montajes Windows u otra ruta) para ejecutar como guardián o alterar el
   servicio. Dos UIDs Linux no bastan si existe esa vía. La evaluación del
   host Windows y del navegador queda separada de `/proc` en el guest.
4. Identificar un origen de UI que el humano pueda verificar sin confiar en
   un enlace arbitrario escrito por el agente. Un enlace de un solo uso
   identifica una solicitud, no autentica a la persona. La UI debe mostrar
   pregunta, opciones ordenadas, opción elegida, categoría e identidad antes
   de pedir código. Probar que el agente no puede controlar la sesión o
   sustituir la página. Respuesta personalizada vuelve a propuesta sin
   consumirlo.
5. El guardián recomputa el desafío desde la fuente autorizada, reserva la
   coordenada antes de solicitar el código, emite y consume un nonce propio,
   comprueba expiración con un reloj de confianza y lo gasta
   duraderamente. Un resultado ambiguo, caída o fallo de fsync bloquea; no
   se reutiliza el código para resolver incertidumbre. `expiry` y `nonce` de
   las propuestas sintéticas actuales solo son campos vinculados por hash:
   no acreditan vigencia ni protección contra replay real.
6. El guardián emite un recibo autenticado ligado al desafío y decisión
   exactos. La clave de autenticación permanece fuera del alcance del agente.
   Solo el guardián puede escribir su Git privado; el verificador externo
   comprueba autenticidad, vigencia, revocación y consumo. El SHA o commit Git
   solo identifica bytes y orden de registro; no autentica al escritor.
7. Comparar representación UI y manifiesto/recibo para detectar divergencias.
   Una captura de pantalla no prueba que el humano miró o comprendió la página.
   Confirmación semántica y permiso de operación siguen siendo gates distintos.

Cuando el repositorio completo está disponible, desde su raíz el sondeo local
de solo lectura puede ejecutarse con
`python3 -B supervisor/rs3_d05_agent_boundary_preflight.py --authority-uid <UID> --authority-root <RUTA>`.
Su resultado nunca habilita autoridad por sí mismo. Si el módulo no está
instalado junto a una skill portable, registrar `NOT_RUN`; no inferir PASS.

## Evidencia y transiciones

El orden es: diseño confirmado → fixtures sintéticos → cuentas y custodia
preparadas por el operador → controles negativos desde el agente → UI y
recibos con pruebas de manipulación → recuperación y revocación → ensayo en
hardware objetivo → RDD exacto. Una etapa no ejecutada queda `NOT_RUN`, no
`PASS`. Un control favorable limitado permite continuar pruebas, nunca
`HUMAN_CONFIRMED` por sí solo. Si falta evidencia crítica, permanecer en
`NOT_ESTABLISHED` con `execution_authorized=false`.

La corrida sintética de 2026-11-10 en el cloud env observó al agente UID 1000
leyendo el verificador y escribiendo su almacén temporal, aun con modos
`0600/0700`. Rechazó mutación de nonce y replay, y gastó el código de prueba;
devolvió `authority_verification=NOT_ESTABLISHED` y
`execution_authorized=false`. La UI, Git privado y segundo UID fueron
`NOT_RUN`. Esa observación falsó D05 en **esa topología**, no determina la
capacidad del equipo Linux/WSL del usuario.
