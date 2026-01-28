from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_name_triple = fields.Boolean(string='Partner Name Should Be Triple?')
    ab_required_fields_ids = fields.One2many('ab.required.fields', 'res_company_id', string='Required Fields')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_name_triple = fields.Boolean(
        string='Partner Name Should Be Triple?', related='company_id.is_name_triple', readonly=False)

