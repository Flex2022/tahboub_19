# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_barcode = fields.Char(string='Barcode', related='product_id.barcode')
