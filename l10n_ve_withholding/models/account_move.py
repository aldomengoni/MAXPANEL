# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_ve_document_number = fields.Char(
        'Control Number', size=80,
        help="Number used to manage pre-printed invoices, by law you will"
             " need to put here this number to be able to declarate on"
             " Fiscal reports correctly.",store=True)
    applied_withholding_tax = fields.Boolean(
        'Retencion de IVA aplicada', compute='_compute_applied_withholding',
        store=True, copy=False, default=False)
    applied_withholding_islr = fields.Boolean(
        'Retencion de ISLR aplicada', compute='_compute_applied_withholding',
        store=True, copy=False, default=False)

    @api.depends('amount_residual', 'amount_residual_signed',)
    def _compute_applied_withholding(self):
        for rec in self:
            applied_withholding_tax = False
            applied_withholding_islr = False
            if rec.move_type in ['in_invoice'] and rec.payment_group_ids:
                if rec._get_reconciled_payments().mapped(
                        'payment_group_id').filtered(lambda x: x.iva == True):
                    applied_withholding_tax = True
                if rec._get_reconciled_payments().mapped(
                        'payment_group_id').filtered(lambda x: x.islr == True):
                    applied_withholding_islr = True
            rec.applied_withholding_tax = applied_withholding_tax
            rec.applied_withholding_islr = applied_withholding_islr
            
    def _post(self, soft=True):
        # se debe devolver el resultado de super (los asientos publicados)
        posted = super(AccountMove, self)._post(soft)
        for rec in self:
            if (rec.state == 'posted' and rec.\
                l10n_ve_document_number == False) or rec.\
                    move_type == 'out_refund' and rec.l10n_ve_document_number == '':
                if rec.move_type in ['out_invoice', 'out_refund']:
                    if rec.journal_id.sequence_control_id:
                        l10n_ve_document_number = rec.env[
                            'ir.sequence'].next_by_code(rec.journal_id.\
                                sequence_control_id.code)
                        rec.write({
                            'l10n_ve_document_number': l10n_ve_document_number})
                    else:
                        raise ValidationError(
                    _("El diario por el cual está emitiendo la factura no"+
                        " tiene secuencia para número de control"))
        return posted
