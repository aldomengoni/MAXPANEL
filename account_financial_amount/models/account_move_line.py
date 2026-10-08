##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    financial_amount_residual = fields.Monetary(
        compute='_compute_financial_amounts',
        string='Residual Financial Amount',
        currency_field='company_currency_id',
    )
    financial_amount = fields.Monetary(
        compute='_compute_financial_amounts',
        string='Financial Amount',
        currency_field='company_currency_id',
    )

    @api.depends('debit', 'credit')
    def _compute_financial_amounts(self):
        # res.currency.compute() ya no existe y account.account no tiene
        # company_id (ahora es company_ids): convertimos con _convert() a la
        # moneda de la compañía del apunte, a la tasa del día (como hacía compute)
        date = fields.Date.context_today(self)
        for line in self:
            company_currency = line.company_currency_id
            if line.currency_id and line.currency_id != company_currency:
                financial_amount = line.currency_id._convert(
                    line.amount_currency, company_currency, line.company_id, date)
                financial_amount_residual = line.currency_id._convert(
                    line.amount_residual_currency, company_currency, line.company_id, date)
            else:
                financial_amount = line.balance
                financial_amount_residual = line.amount_residual
            line.financial_amount = financial_amount
            line.financial_amount_residual = financial_amount_residual
