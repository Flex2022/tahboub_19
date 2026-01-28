# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    flex_sale_product_category = fields.Many2one(
        'product.category', string='Product Category',
        help='Select the default product category for flexible sales.'
    )

    flex_sale_stock_move_type = fields.Many2one(
        'stock.picking.type', string='Stock Move Type',
        help='Select the default stock move type for flexible sales.'
    )

    active_sale_mrp_customization = fields.Boolean(
        string='Activate Sale MRP Customization',
        help='Activate customization for sales and manufacturing integration.'
    )