from odoo import models
from odoo.exceptions import UserError


class ValidateAccountMove(models.TransientModel):
    _inherit = "validate.account.move"

    def validate_move(self):
        # desde v17 el wizard ya tiene los asientos a validar en move_ids
        moves = self.move_ids

        try:
            res = super().validate_move()
        except UserError as error:
            # we consider that an error with "Afip" occurred and we need to pay the invoice with pay now
            if 'AFIP' in repr(error):
                # we try to pay automatic if the pay now journal is setting on the invoice.
                moves.pay_now()
                if not self.env.context.get('l10n_ar_invoice_skip_commit'):
                    self.env.cr.commit()
            raise
        moves.pay_now()
        return res
