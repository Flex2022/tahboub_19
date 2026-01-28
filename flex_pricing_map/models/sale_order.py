from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    use_price_map = fields.Boolean(related='company_id.use_price_map')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_map_id = fields.Many2one(comodel_name="price.map", string='Pricing Map')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        return super(SaleOrderLine, self)._onchange_product_id()

    @api.onchange('price_map_id')
    def onchange_price_map(self):
        return self._onchange_product_id()

    def _get_display_price(self, product):
        price = super(SaleOrderLine, self)._get_display_price(product)
        if self.price_map_id:
            price *= self.price_map_id.percent / 100
        return price
