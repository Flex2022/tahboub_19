# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    warehouse_id = fields.Many2one(related='location_id.warehouse_id', store=True)
