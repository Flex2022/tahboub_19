# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_show_customer_address = fields.Boolean("Show Customer Address", related='company_id.is_show_customer_address')