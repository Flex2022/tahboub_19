# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_payment_tax = fields.Boolean(string='Payment Tax Entry')
    payment_tax_account_id = fields.Many2one(comodel_name='account.account', string='Payment Tax Account')
