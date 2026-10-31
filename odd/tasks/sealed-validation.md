# Contraste forense y validación de objetos Git

## Specs

- Usuario exige contrastar concurrencia, symlinks, CRLF y sustituir monitoreo por
  validación sobre commit Git fijado. No asumir resultados proyectados como reales.
- Mantener protección de normas OpenAI/terceros y hardware de terceros; aclarar
  que no prohíbe ensayos propios autorizados con límites. No CI ni producción.
- Lectura sin seguir symlinks/componentes, rechazo de especiales y presupuesto.
- Normalización LF explícita sobre copias antes de crear nuevas evidencias, sin
  reinterpretar silenciosamente hashes históricos de bytes como hashes semánticos.
- Commit/árbol identifica bytes; no equivale a autoría confiable, disponibilidad
  perpetua, permiso de producción ni defensa contra root/kernel comprometido.

## Tasks

- [x] Leer skill/fuentes/código. MCP cloud actual y web Git/Microsoft.
- [x] RED antes de cambios; endurecer lecturas y contratos.
- [x] Añadir validación de commit completo fijado, sin checkout/hooks/filtros.
- [x] Pruebas adversariales acotadas y RDD de candidato exacto.
- [x] Registro, memoria y exportación completa actualizada.

## Log

- WSL2 no implica que todos los archivos estén en DrvFS/9P: falta determinar
  filesystem real objetivo. Linux nativo WSL y /mnt/c son fronteras distintas.
- safe_file actual resuelve y rechaza symlink que escapa a la base, por lo que
  /dev/zero externo no se presume bypass demostrado. Lectura principal directa
  y archivos especiales internos sí requieren límite y rechazo verificable.
- No se reescriben recibos originales ni se ejecuta estrés destructivo cloud.

- Usuario reiteró «Debes usar gentle-ai». CLI real: mode status ON, registro
  refrescado y revisión nativa review-c82a0ca0d69af142 (20 archivos,679 líneas),
  aprobada y acknowledged. Tres lentes sin findings y un WARNING de recuperación
  del normalizador, no falso cero-hallazgos.
- Seguimiento independiente: límite real RLIMIT_FSIZE=1 en subproceso reprodujo
  salida parcial; misma prueba ahora GREEN con temporal/fsync/link sin overwrite.
  21+43+23 =87 pruebas PASS, versión2.2.1; review-f412da4c5db898a9 en curso contra
  snapshot aprobado ed329abb8a6b4a37e434e21bad3f0ae1ec433021 (79 líneas nuevas).
- La regla se aclaró en ambas instrucciones del proyecto: no prohibición general
  de estrés propio autorizado; protección de terceros y normas sigue obligatoria.

- Seguimiento nativo aprobado y acknowledged; R3-001 WARNING retenido: publicación
  privada0600 requiere decisión de permisos si hay futuro consumidor de otra cuenta.
  No se afirma cero findings. Fuente congelada y QA19 sin cambios actuales.
- Export JSON íntegro2.2.1 verificado byte a byte en exports. Resultado y límites
  en docs/skill-audit/sealed-validation/RESULTADO.md. Producción bloqueada, CI
  diferido, hardware i3/WSL no ejecutado. Sin nueva entrevista ni diálogo ficticio.
