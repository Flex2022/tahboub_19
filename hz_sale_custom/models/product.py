# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    custom_rate_id = fields.Many2one('custom.rate', string='Custom Rate')
    # standard_price = fields.Float(groups='hz_sale_custom.group_product_cost')


class ProductProduct(models.Model):
    _inherit = "product.product"

    # standard_price = fields.Float(groups='hz_sale_custom.group_product_cost')
