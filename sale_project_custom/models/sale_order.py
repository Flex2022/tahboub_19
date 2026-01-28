from odoo import fields, models, api


class SaleOrderLineCustom(models.Model):
    _inherit = 'sale.order.line'

    # Override Method [contain type of product [storable product]]
    @api.depends('product_id.type')
    def _compute_is_service(self):
        res = super(SaleOrderLineCustom,self)._compute_is_service()
        for so_line in self:
            so_line.is_service = so_line.product_id.type in ['service','product']
        return res

    #  Override Method [contain type of product [storable product]]
    @api.depends('product_id.type')
    def _compute_product_updatable(self):
        for line in self:
            if line.product_id.type in ['service','product'] and line.state == 'sale':
                line.product_updatable = False
            else:
                super(SaleOrderLineCustom, line)._compute_product_updatable()