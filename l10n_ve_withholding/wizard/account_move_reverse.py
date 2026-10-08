# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'


    def _prepare_default_reversal(self, move):
        # llamamos a super para conservar los valores que agrega Odoo 19
        # (invoice_currency_rate, invoice_origin, tipo/número de documento latam, etc.)
        res = super()._prepare_default_reversal(move)
        res.update({
            'ref': _('Reversión de: %s, %s') % (move.name, self.reason) if self.reason else _('Reversión de: %s') % (move.name),
            'date': self.date or move.date,
            'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
            'l10n_ve_document_number': "",
        })
        return res


    #TODO: ver si esto es necesario.
    # def reverse_moves(self):
    #     """ Forzamos el seteo limpio"""
    #     res = super(AccountMoveReversal, self).reverse_moves()
    #     #Nunca esta pasando por aqui.
    #     for rec in self:
    #         self.move_ids.l10n_ve_document_number = ""
    #     return res
