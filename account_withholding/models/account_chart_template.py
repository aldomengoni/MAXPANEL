##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models
import logging
_logger = logging.getLogger(__name__)


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    def _post_load_data(self, template_code, company, template_data):
        """
        En Odoo 19 ya no existe _create_bank_journals; creamos el diario de
        retenciones luego de cargar el plan contable. Se crea con los métodos
        de pago de retención (ver account.journal._default_*_payment_methods)
        y sin cuenta por defecto.
        """
        res = super()._post_load_data(template_code, company, template_data)
        company = company or self.env.company
        if company._localization_use_withholdings():
            self._create_withholding_journal(company)
        return res

    def _create_withholding_journal(self, company):
        payment_method = self.env.ref('account_withholding.account_payment_method_out_withholding')
        existing = self.env['account.journal'].search([
            ('company_id', '=', company.id),
            ('type', 'in', ('bank', 'cash')),
            ('outbound_payment_method_line_ids.payment_method_id', '=', payment_method.id),
        ], limit=1)
        if existing:
            return existing
        journal = self.env['account.journal'].with_context(withholding_journal=True).create({
            'name': 'Retenciones',
            'type': 'cash',
            'company_id': company.id,
        })
        # we dont want this journal to have accounts and we can not inherit
        # to avoid creation, so we delete it
        to_unlink = journal.default_account_id
        journal.default_account_id = False
        to_unlink.unlink()
        return journal
