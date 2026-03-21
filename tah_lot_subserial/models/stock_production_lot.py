# -*- coding: utf-8 -*-
from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    sub_serial_ids = fields.One2many(
        "stock.lot.subserial",
        "lot_id",
        string="Sub Serials",
    )
