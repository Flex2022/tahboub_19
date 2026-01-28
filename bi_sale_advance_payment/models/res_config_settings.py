# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    sale_advance_payment_percent = fields.Float(
        string='Sale Advance Payment Percentage',
        help="Percentage of sale order that will be reserved from advance payment"
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_advance_payment_percent = fields.Float(
        string='Sale Advance Payment Percentage',
        help="Percentage of sale order that will be reserved from advance payment",
        related='company_id.sale_advance_payment_percent',
        readonly=False
    )
