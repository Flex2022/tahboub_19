# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_view_sale_quotation(self):
        action = super(CrmLead, self).action_view_sale_quotation()
        action['context']['creating_from_crm'] = True
        return action

    def action_view_sale_order(self):
        action = super(CrmLead, self).action_view_sale_order()
        action['context']['creating_from_crm'] = True
        return action


