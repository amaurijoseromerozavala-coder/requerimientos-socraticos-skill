# Preparación D05: agente y guardián separados en Linux/WSL

**Estado:** procedimiento propuesto; `authority_verification=NOT_ESTABLISHED`,
`execution_authorized=false`. La ejecución en el hardware objetivo está
`NOT_RUN` para esta unidad. Un operador de confianza debe controlar Windows,
la distribución WSL y la configuración inicial. El administrador del host
Windows sigue dentro de la base de confianza: dos UIDs Linux no lo aíslan.

## Puerta 0: instantánea y capacidad

El operador verifica commit exacto, cambios locales, versión WSL/Ubuntu,
identidad de la distribución, espacio libre en el volumen Windows que respalda
su disco virtual y memoria disponible en Windows y WSL. Conserva la evidencia
fuera del Git de autoridad. Si el host no tiene margen comprobado para una
instalación y una reversión, **detiene** el procedimiento. No usa pruebas de
estrés ni crea códigos reales. La cuenta actual que ejecuta el agente, si tiene
una vía sudo utilizable, Docker, WSLInterop o acceso de escritura a un volumen Windows, no
sirve como cuenta de agente del perfil propuesto.

## Puerta 1: topología preparada por el operador

Se requieren tres roles distintos: operador administrador, agente dedicado y
guardián dedicado. Antes de crear cuentas se comprueba que los nombres y UIDs
elegidos estén libres y se registra quién puede restablecerlas. El agente no
pertenece a grupos `sudo`, `docker` ni equivalentes, carece de capacidades
efectivas y no posee un socket de contenedores utilizable. El guardián no usa
el clon del agente como código ejecutable: su código verificado reside en una
ruta cuya escritura está controlada por el operador. Su almacén, llave de
recibos y Git privado se alojan fuera del árbol del agente, en directorios
propiedad del guardián con ancestros no escribibles por el agente. Los modos
`0700/0600` son controles necesarios, no una prueba suficiente de aislamiento.

Para el primer perfil WSL, el operador prepara una distribución sin
interoperabilidad Windows ni montajes automáticos de unidades Windows para la
sesión del agente. En Ubuntu bajo WSL, `/etc/wsl.conf` admite las secciones
`[interop] enabled=false` y `[automount] enabled=false`; aplicar esa
configuración exige reiniciar la distribución desde Windows y afecta a sus
otros procesos. El operador debe comprobar soporte y consecuencias en la
versión instalada antes de hacerlo. Un montaje manual posterior, otra unidad
`drvfs`/`9p` o un socket privilegiado reabre la prueba. No se cambia la
configuración ni se crea una cuenta automáticamente desde esta skill.

## Puerta 2: controles negativos desde el agente real

El operador inicia Pi con la identidad exacta de la cuenta dedicada y registra
UID real/efectivo, grupos, capacidades, commit del código y estado de trabajo.
Ejecuta `python3 -B supervisor/rs3_d05_agent_boundary_preflight.py --agent-only`
con plazo y sin redirección a archivos públicos. Exige que no se observe
Docker escribible, WSLInterop ni escritura en la raíz de un montaje Windows
identificado. El sondeo reconoce `drvfs` y `9p` con `aname=drvfs` en
`mountinfo`, de forma acotada, y no conecta con esos servicios. No descarta
subdirectorios escribibles bajo una raíz no escribible ni rutas Windows
expuestas por otros mecanismos; `NOT_ASSESSED` no equivale a ausencia
demostrada.

Además, desde esa misma cuenta, el operador comprueba sin ejecutar órdenes
elevadas: `sudo -n -l` con salida oculta (registrar solo el código de salida),
grupos privilegiados, accesibilidad del socket Docker y permisos efectivos de
lectura, escritura y travesía sobre el almacén y Git privados. `sudo -n -l`
exit 0 bloquea; exit distinto de 0 no descarta otros mecanismos de elevación.
Debe revisar IPC, capacidades, control de procesos y rutas Windows adicionales.
Una exposición observada devuelve `FAIL`; una vía crítica sin comprobar deja
`NOT_ASSESSED`. Nunca se ejecuta un comando de prueba que eleve privilegios o
modifique el host para intentar demostrar el fallo.

## Puerta 3: pruebas posteriores, todavía no ejecutables

Solo tras una frontera de cuenta/host favorable, una unidad distinta podrá
construir servicio y UI del guardián. Entonces se ensayarán procesos controlados
para comprobar que el agente no puede señalarlos ni alterar la UI; código
impreso de un solo uso, consumo duradero, desafío recomputado, recibo
autenticado, Git privado, expiración, revocación y recuperación. La prueba de
permisos de directorio no sustituye esas pruebas. El `SHA` de Git identifica
bytes, no autentica a quien los escribió ni demuestra que el humano vio la UI.

El resultado de cada puerta conserva `PASS_OBSERVED`, `FAIL`, `NOT_ASSESSED` o
`NOT_RUN` **por control** y la procedencia de la observación. El estado global
de D05 permanece `NOT_ESTABLISHED` hasta que todos los controles materiales
aplicables, el canal humano y el recibo independiente sean probados y revisados.
El resultado de `requirements activate` o de CI no promueve D05.
