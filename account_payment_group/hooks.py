# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import api, SUPERUSER_ID
_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Create a payment group for every existing payment (no transfers)
    """
    # Buscar pagos que no sean transferencias internas
    payments = env['account.payment'].search([
        ('partner_id', '!=', False),
        ('payment_type', '!=', 'transfer')  # Usar payment_type en lugar de is_internal_transfer
    ])
    
    # Manejo de estados para Odoo 18
    state_mapping = {
        'draft': 'draft',
        'posted': 'posted',
        'sent': 'posted',      # En Odoo 18, 'sent' se considera 'posted'
        'reconciled': 'posted', # 'reconciled' también se considera 'posted'
        'cancelled': 'cancel'
    }
    
    # Crear grupos de pago
    for payment in payments:
        try:
            _logger.info('Creating payment group for payment %s', payment.id)
            
            # Obtener el estado mapeado
            _state = state_mapping.get(payment.state, 'draft')
            
            env['account.payment.group'].create({
                'company_id': payment.company_id.id,
                'partner_type': payment.partner_type,
                'partner_id': payment.partner_id.id,
                'payment_date': payment.date,
                'communication': payment.ref,
                'payment_ids': [(4, payment.id, False)],
                'state': _state,
            })
        except Exception as e:
            _logger.error(
                "Error creating payment group for payment %s: %s",
                payment.id, str(e)
            )