# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SetDiscount(models.TransientModel):
    _inherit = "set.discount"

    def action_confirm(self):
        res = super(SetDiscount, self).action_confirm()
        self.sale_id.check_category_discount_limit()
        return res
