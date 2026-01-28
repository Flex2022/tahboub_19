from odoo import api, fields, models

class ProductTemplate(models.Model):

    _inherit = "product.template"

    available_qty_quant = fields.Float(string="Available Qty Quant", compute="_compute_available_qty_quant")



    def _compute_available_qty_quant(self):
        #bring all available quantities
        for product in self:
            product.available_qty_quant = sum(product.env['stock.quant'].search([('product_id.name', '=', product.name), ('location_id.usage', '=', 'internal')]).mapped('available_quantity'))



class ProductProduct(models.Model):

    _inherit = "product.product"

    available_qty_quant = fields.Float(string="Available Qty Quant", compute="_compute_available_qty_quant")



    def _compute_available_qty_quant(self):
        for product in self:
            product.available_qty_quant = sum(product.env['stock.quant'].search([('product_id', '=', product.id), ('location_id.usage', '=', 'internal')]).mapped('available_quantity'))


