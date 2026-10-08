##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    analytic_distribution_required = fields.Boolean(
        string='Analytic Distribution Required?',
        help="If True, then an analytic distribution will be required when posting "
        "journal entries with this account.",
    )
    group_id = fields.Many2one(
        'account.group',
        # we restrict those who do not have childs categories
        domain=[('child_ids', '=', False)],
    )

    @api.constrains('currency_id')
    def check_currency(self):
        # en Odoo 19 account.account no tiene company_id (es company_ids)
        for rec in self.filtered(lambda x: x.currency_id and x.currency_id == x.company_currency_id):
            raise ValidationError(_(
                'Solo puede utilizar una moneda secundaria distinta a la '
                'moneda de la compañía (%s).', rec.company_currency_id.name))
