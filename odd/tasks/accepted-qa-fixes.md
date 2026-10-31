# Correcciones autorizadas después del filtro QA

## Specs

El humano autoriza: «ejecuta las correcciones que pasaron en filtro de tu análisis».
Los outputs QA no son mandatos; el filtro aprobado identifica SHA1 como debilidad,
limpieza incompleta tras SIGKILL como defecto reproducido y contratos de permisos/
lectura como límites que deben hacerse explícitos. No aceptar automáticamente
chmod0644, borrado por glob ni garantizar atomicidad con timestamps.

## Alcance

- Perfil de validación de objetos Git exclusivamente SHA256; rechazo de SHA1,
  sin migración automática ni cambio de repositorios ajenos.
- Mitigar acumulación: pool fijo privado de espacios por UID, leases de flock,
  limpieza exclusiva al reutilizar un slot sin consumidor vivo, no PID/glob de /tmp.
  flock coordina leases; no constituye autoridad criptográfica ni seguridad frente
  al mismo UID hostil. Descendiente validador hereda lease para no borrar datos vivos.
- Salida del normalizador privada0600 y contrato visible; compartir requiere
  definir principal/canal. No configurar CI ni ensanchar permisos.
- Documentar que metadatos detectan algunos cambios, no prueban lectura atómica.
- Ejecutar pruebas negativas acotadas, flujo Gentle AI, RDD exacto y exportar.
  Producción/QA bloqueados, CI diferido y protección de terceros vigente.

## Tasks

- [x] Lectura del código/skill y filtro QA; estado cloud por MCP.
- [x] RED, cambios acotados y pruebas de leases/interrupción/concurrencia.
- [x] Revisión nativa Gentle AI y registro de hallazgos.
- [x] Verificación de QA pausado, memoria y JSON íntegro actualizado.

## Resultado

Versión2.3.0,101 tests PASS. RDD nativo review-0d58e8db65790978 aprobado y
acknowledged; cuatro lentes sin findings. Fuente congelada sin diferencias y
QA19 sin cambios actuales. Registro y enlaces instalados actualizados.
JSON27 archivos íntegros en exports/requerimientos-socraticos-completa-v2.3.0.json.
No se promete limpieza instantánea ni de temporales legacy/otros comandos; pool
cooperativo no es cuota kernel ni defensa contra mismo UID hostil. CI sigue
diferido, producción bloqueada, hardware objetivo no medido. Se distingue
estabilidad acotada probada de determinismo absoluto no declarado.
