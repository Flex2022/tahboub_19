# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResUsers(models.Model):
    _inherit = "res.users"

    restrict_pricelist = fields.Boolean(string='Pricelist Restriction In Sale Orders')
    allowed_pricelists = fields.Many2many(
        'product.pricelist', 'user_allowed_pricelist', string='Allowed Pricelists', copy=False)
