# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_show_customer_address = fields.Boolean("Show Customer Address", )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_show_customer_address = fields.Boolean(
        "Show Customer Address", related='company_id.is_show_customer_address', readonly=False)