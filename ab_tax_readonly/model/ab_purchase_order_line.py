from odoo import models, api,fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_tax_readonly_purchase = fields.Boolean(string='Readonly Tax', related='company_id.is_tax_readonly_purchase')
