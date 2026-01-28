# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    is_true = fields.Boolean(compute='_compute_is_true')

    def action_apply_inventory(self):
        res = super(StockQuant, self).action_apply_inventory()
        if not self.env.user.has_group("bi_update_qty_disable.group_onhand_qty_user"):
            raise ValidationError(
                _("You don't have access rights for update on hand quantity!"))
        return res


    @api.depends_context('uid')
    def _compute_is_true(self):
        # 2. Check the group once for efficiency
        is_qty_group = self.env.user.has_group('bi_update_qty_disable.group_onhand_qty_user')
        for record in self:
            # 3. Logic: If in group, set False, otherwise True
            record.is_true = not is_qty_group
