# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class PriceMap(models.Model):
    _name = "price.map"
    _description = "Price Map"

    name = fields.Char(string="Name", required=True)
    percent = fields.Float(string="Price Percent %", default=100)
