# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    flex_sale_product_category = fields.Many2one(
        'product.category', string='Product Category', related="company_id.flex_sale_product_category",
        readonly=False,
        help='Select the default product category for flexible sales.'
    )

    flex_sale_stock_move_type = fields.Many2one(
        'stock.picking.type', string='Stock Picking Type', related="company_id.flex_sale_stock_move_type",
        readonly=False,
        help='Select the default stock move type for flexible sales.'
    )

    active_sale_mrp_customization = fields.Boolean(
        string='Activate Sale MRP Customization', related="company_id.active_sale_mrp_customization",
        readonly=False,
        help='Activate customization for sales and manufacturing integration.'
    )
