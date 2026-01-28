# -*- coding: utf-8 -*-
from odoo import api, fields, models, _



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_payment_tax = fields.Boolean(
        string='Tax Entry For Payments',
        related='company_id.use_payment_tax',
        readonly=False
    )

    payment_tax_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.payment_tax_account_id',
        string='Tax Clearing Account',
        readonly=False,
        # Simplified domain for validation; Odoo 19 will automatically
        # filter by company if the field is company_dependent/related.
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]"
    )