# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def default_get(self, fields_list):
        res = super(ResPartner, self).default_get(fields_list)
        if 'property_account_position_id' in fields_list:
            if self.env.user.restrict_pricelist:
                res['property_account_position_id'] = self.env.company.fiscal_position_id.id
        return res

    property_account_position_id = fields.Many2one('account.fiscal.position', groups='flex_account.group_fiscal_position')
