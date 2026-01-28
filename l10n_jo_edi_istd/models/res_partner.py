from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_account_position_domain(self):
        company = self.env.company
        return [
            ('company_id', '=', company.id),
            ('l10n_jo_tax_company_type', '=', company.l10n_jo_tax_company_type)
        ]

    property_account_position_id = fields.Many2one(
        'account.fiscal.position', string='Fiscal Position',
        company_dependent=True, domain=lambda self: self._get_account_position_domain(),
        help="The fiscal position will determine taxes and accounts used for the partner.")
    # property_account_position_id = fields.Many2one(
    # domain = "[('company_id', '=', current_company_id)]",
    # [('l10n_jo_tax_company_type', '=', 'company_id.l10n_jo_tax_company_type')]