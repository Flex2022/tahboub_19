from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    l10n_type = fields.Selection(selection=[('Z', 'If the good or service is exempt'),
                                                  ('O', 'If the good or service is subject to a zero rating'),
                                                  ('S', 'If the good or service is subject to a percentage of the tax rates'),], string='Type')
