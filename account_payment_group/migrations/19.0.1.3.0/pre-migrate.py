# Migración 18.0 -> 19.0
# En 18 este módulo recreaba en _auto_init el índice account_move_unique_name
# agregando "payment_group_id IS NULL" (los pagos de un mismo grupo comparten
# el número del recibo). En 19 el índice se declara con models.UniqueIndex en
# account.move, pero el ORM conserva cualquier índice existente SIN comentario,
# aunque su definición sea otra. Si durante la actualización el índice quedó con
# la definición estándar del núcleo, lo eliminamos para que el ORM lo vuelva a
# crear con la definición de este módulo al cargarlo.
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        SELECT pg_get_indexdef(i.indexrelid)
          FROM pg_index i
          JOIN pg_class c ON c.oid = i.indexrelid
         WHERE c.relname = 'account_move_unique_name'
    """)
    row = cr.fetchone()
    if row and 'payment_group_id' not in row[0]:
        cr.execute("DROP INDEX IF EXISTS account_move_unique_name")
        _logger.info(
            "account_payment_group: eliminado account_move_unique_name sin la "
            "condición payment_group_id; el ORM lo recreará con la definición del módulo")
