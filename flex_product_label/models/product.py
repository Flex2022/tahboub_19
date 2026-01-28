from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'


    warehouse_id_in_stock = fields.Char(string='Warehouse ID in Stock',compute='_compute_warehouse_id_in_stock')

    @api.depends('stock_quant_ids.quantity')
    def _compute_warehouse_id_in_stock(self):
        for product in self:
            warehouse_names = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('quantity', '>', 0)  # Only consider warehouses where stock is available
            ]).mapped('location_id.warehouse_id.name')

            product.warehouse_id_in_stock = ', '.join(set(warehouse_names)) if warehouse_names else ''


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    warehouse_id_in_stock = fields.Char(
        string='Warehouses in Stock',
        compute='_compute_warehouse_id_in_stock',
        store=False
    )

    @api.depends('product_variant_ids.stock_quant_ids.quantity')
    def _compute_warehouse_id_in_stock(self):
        for template in self:
            warehouse_names = self.env['stock.quant'].search([
                ('product_id', 'in', template.product_variant_ids.ids),
                ('quantity', '>', 0)  # Only consider warehouses where stock is available
            ]).mapped('location_id.warehouse_id.name')

            template.warehouse_id_in_stock = ', '.join(set(warehouse_names)) if warehouse_names else ''



