from odoo import fields, models, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    brand_id = fields.Many2one('brand', string='Brand', related='product_id.brand_id', store=True)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    brand_id = fields.Many2one('brand', string='Brand', related='product_id.brand_id', store=True)


# class StockValuationLayer(models.Model):
#     _inherit = 'stock.valuation.layer'
#
#     brand_id = fields.Many2one('brand', string='Brand', related='product_id.brand_id', store=True)
#

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    brand_id = fields.Many2one('brand', string='Brand', related='product_id.brand_id', store=True)


# class ReportStockQuantity(models.Model):
#     _inherit = 'report.stock.quantity'
#
#     brand_id = fields.Many2one('brand', string='Brand', related='product_id.brand_id', store=True)
