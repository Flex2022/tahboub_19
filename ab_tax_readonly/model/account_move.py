from odoo import models, api, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_tax_readonly_sale = fields.Boolean(string='Readonly Tax', related='company_id.is_tax_readonly_sale')
    is_tax_readonly_purchase = fields.Boolean(string='Readonly Tax', related='company_id.is_tax_readonly_purchase')
    is_tax_manager = fields.Boolean(compute='_compute_is_tax_manager')

    def _compute_is_tax_manager(self):
        for record in self:
            # This is where you use has_group in Python
            record.is_tax_manager = self.env.user.has_group('ab_tax_readonly.group_edit_tax')
