# WU-SUP-GROUP-002 — grupo aún activo tras recolectar al hijo

## Solicitud y alcance

El informe QA pide comprobar la salida temprana del hijo con un descendiente vivo. Un ensayo local acotado sobre el commit df3e2dc observó `status=EXITED`, `returncode=0`, `cleanup=CONFIRMED` y un descendiente del mismo grupo todavía vivo. El núcleo declara que `cleanup` solo acredita al hijo directo, pero el adaptador puede admitir el resultado. Esta unidad cierra esa admisión incorrecta.

Después de recolectar al hijo, si el grupo iniciado para él conserva un miembro no zombi, el núcleo debe devolver `INFRA_LOCK` y `cleanup=UNCONFIRMED`. Solo observa el grupo; no envía señales cuando la identidad del hijo ya no es comprobable. Una observación incompleta también bloquea. Un grupo compuesto solo por zombis no se considera activo. Esto no ofrece recuperación autónoma; el caso de un descendiente que cambió de grupo queda fuera del alcance.

Actualizar el README para reflejar que el journal ya implementa las transiciones RESERVED→ACTIVE→STOPPING, aún sin enlace al lanzamiento, y que el núcleo usa señales de grupo solo mientras verifica el hijo vivo. El RDD del diseño integrado sigue siendo documental y la calibración en el i3/WSL sigue pendiente.

## Criterios de aceptación

- Un hijo con salida 0 y un descendiente vivo del mismo grupo que cierra sus canales no produce un resultado admisible; el núcleo bloquea la instancia.
- Un hijo sin grupo restante conserva el resultado normal y la suite previa sigue pasando.
- La observación fallida o incierta del grupo no se interpreta como limpieza confirmada.
- El README describe los estados implementados y sus límites sin proclamar supervisor completo.

## Tareas y registro

1. RED: añadir prueba acotada con limpieza del descendiente; ejecutar y conservar el resultado. Añadir comprobación documental RED para la tabla del README.
2. GREEN: distinguir grupo restante y corregir README; ejecutar controles específicos y regresión.
3. RDD nativo de Gentle AI sobre el candidato exacto, reconocer recibo, publicar y verificar SHA.

- 2026-11-01: ODD creado antes de editar implementación y README.
- 2026-11-01: RED: dos pruebas fallaron por `EXITED` con descendiente vivo y README obsoleto; el control de tubería retenida también rechazó la semántica anterior. GREEN: prueba focal 2/2. Primer barrido de regresión detectó que un grupo formado solo por zombis no debía bloquear; se acotó la observación a miembros no zombis. Regresión final: 49 pruebas OK. Sin ensayo en el i3/WSL.
