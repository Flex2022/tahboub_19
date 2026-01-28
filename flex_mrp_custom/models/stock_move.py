from odoo import models, fields


class StockMoveInherited(models.Model):
    _inherit = 'stock.move'

    description_pickingout = fields.Text(
        'Description on Delivery Orders', related="product_id.description_pickingout"
    )
