from odoo import models, api


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        # desde v17 se usa la clave 'type' (la clave 'domain' se ignoraba)
        res['withholding'] = {'mode': 'multi', 'type': ('bank', 'cash')}
        return res
