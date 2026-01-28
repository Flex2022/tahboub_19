from odoo import models, api,fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_tax_readonly_sale = fields.Boolean(string='Readonly Tax', related='company_id.is_tax_readonly_sale')
