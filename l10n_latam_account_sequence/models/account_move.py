from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Desde Odoo 19 los índices únicos "account_move_unique_name" y
    # "account_move_unique_name_latam" los define el propio núcleo en
    # l10n_latam_invoice_document (models.UniqueIndex) con la misma definición
    # que antes creaba este módulo en _auto_init, por lo que ya no es necesario
    # recrearlos aquí. El método _check_unique_vendor_number tampoco existe en 19.
    # Se conserva el módulo como puente para no romper dependencias
    # (account_payment_group) en bases ya instaladas.
