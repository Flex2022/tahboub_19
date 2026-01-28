# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Default Fiscal Position')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Default Fiscal Position', check_company=True,
        related='company_id.fiscal_position_id', readonly=False)
