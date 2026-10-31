# WU-PORTABLE-001 — Activación local para Gentle Pi/Shell

Solicitud: corregir comando desconocido al activar la skill en el computador del
usuario con Gentle Pi. Permitir continuar diagnóstico/corrección autorizados sin
rutas cloud. ODD/TDD/RDD estricto y respaldo después de revisión.

## Criterios

Entrada autocontenida dentro de la skill, ejecutable por ruta, independiente de
que Gentle AI upstream implemente `requirements`. Resolver helpers respecto al
archivo instalado, incluso con espacios y enlaces. Intérprete explícito o entorno
virtual conocido; no instalar dependencias ni caer silenciosamente a PATH.
Wrapper opcional del repo delega a esa entrada; upstream externo configurado o
binario local, sin recursión ni secuestro de configuración de autenticación.
Ayuda útil aunque falte Python. Todas las operaciones usan el mismo intérprete.

La skill mantiene su rol de requisitos/documentos: Pi coordina correcciones de
producto solo con alcance autorizado y gates; no se convierte cualquier preflight
favorable en permiso. Autodiagnóstico no implica red, cargas, CI ni producción.

## Verificación

RED antes de cambios: nueva entrada ausente y rutas absolutas del wrapper.
Probar copia a directorio temporal con espacios, invocation por symlink, runtime
explícito ausente/vacío, CLI help, rutas de dispatch y delegación upstream sin
recursión. Ejecutar preflight real en cloud y distinguirlo del i3 no observado.
No mezclar candidato pendiente retained-pipe con esta unidad.

## Log
RED inicial 13 fallos/subcasos. Entrada portable y wrapper corregidos; 8 tests nuevos y 9 regresiones de entorno pasan. bash -n y preflight real cloud OK. Skill versionada 2.4.7 y guía Pi actualizada. Sin acceso al i3; RDD pendiente. Candidato separado de retained-pipe.
