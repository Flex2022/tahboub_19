# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_advance_payment_percent = fields.Float(
        string='Sale Advance Payment Percentage',
        help="Percentage of sale order that will be reserved from advance payment"
    )
