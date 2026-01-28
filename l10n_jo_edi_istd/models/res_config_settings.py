from odoo import models, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_jo_client_id = fields.Char(related='company_id.l10n_jo_client_id', readonly=False)
    l10n_jo_client_secret = fields.Char(related='company_id.l10n_jo_client_secret', readonly=False)
    l10n_jo_send_invoices_at_confirm = fields.Boolean(related='company_id.l10n_jo_send_invoices_at_confirm', readonly=False)

    l10n_jo_tax_company_type = fields.Selection(related='company_id.l10n_jo_tax_company_type', readonly=False
        , string='Tax Company Type', help="The type of the company for tax purposes.",
        selection=[
            ('1', 'Income'),
            ('2', 'sales'),
            ('3', 'Privet'),
        ])

    # l10n_jo_tax_company_type = fields.Selection(related='company_id.l10n_jo_tax_company_type', readonly=False
    #                                             , string='Tax Company Type',
    #                                             help="The type of the company for tax purposes.",
    #                                             selection=[
    #                                                 ('1', 'الفاتورة محلية'),
    #                                                 ('2', 'فاتورة تصدير'),
    #                                                 ('3', 'فاتورة مناطق تنموية'),
    #                                             ])