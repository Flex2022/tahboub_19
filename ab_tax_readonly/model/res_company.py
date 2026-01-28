from odoo import models, api, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_tax_readonly_sale = fields.Boolean(string='Readonly Tax')
    is_tax_readonly_purchase = fields.Boolean(string='Readonly Tax')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_tax_readonly_sale = fields.Boolean(
        string='Readonly Tax', related='company_id.is_tax_readonly_sale', config_parameter='ab_tax_readonly.is_tax_readonly_sale', readonly=False)

    is_tax_readonly_purchase = fields.Boolean(
        string='Readonly Tax', related='company_id.is_tax_readonly_purchase', config_parameter='ab_tax_readonly.is_tax_readonly_purchase', readonly=False)