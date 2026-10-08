from odoo import models


class ValidateAccountMove(models.TransientModel):
    _inherit = "validate.account.move"

    def validate_move(self):
        # desde v17 el wizard ya tiene los asientos a validar en move_ids
        moves = self.move_ids
        try:
            res = super().validate_move()
            moves.with_context(mail_notify_force_send=False).action_send_invoice_mail()
        except Exception as exp:
            # we try to send by email the invoices recently validated
            posted_moves = self.filter_posted_moves(moves)
            posted_moves.with_context(mail_notify_force_send=False).action_send_invoice_mail()
            raise exp

        return res

    def filter_posted_moves(self, moves):
        return moves.filtered(lambda x: x.state == 'posted')
