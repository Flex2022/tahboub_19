# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_jo_activity_number = fields.Char(string='Activity Number', help='Activity Number In ISTD Portal')

    l10n_jo_client_id = fields.Char(string='Client ID')
    l10n_jo_client_secret = fields.Char(string='Client Secret')
    l10n_jo_send_invoices_at_confirm = fields.Boolean(string='Send Invoices At Confirm')
    l10n_jo_tax_company_type = fields.Selection(string='Tax Company Type', readonly=False,
                                                help="The type of the company for tax purposes.",
                                                selection=[
                                                    ('1', 'Income'),
                                                    ('2', 'sales'),
                                                    ('3', 'Privet'),
                                                ])
    # l10n_jo_tax_company_type = fields.Selection(string='Tax Company Type', readonly=False,
    #                                             help="The type of the company for tax purposes.",
    #                                             selection=[
    #                                                 ('1', 'الفاتورة محلية'),
    #                                                 ('2', 'فاتورة تصدير'),
    #                                                 ('3', 'فاتورة مناطق تنموية'),
    #                                             ])