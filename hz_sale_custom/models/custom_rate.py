# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CustomRate(models.Model):
    _name = "custom.rate"
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence')
    description = fields.Text(string='Description')
