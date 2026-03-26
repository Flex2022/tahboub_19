# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        if not self.env.user.has_group('flex_sale_no_negative.group_exceed_no_stock'):
            for line in self.order_line.filtered(
                    lambda l: l.product_id and l.product_id.type == 'product' and l.product_id.prevent_negative):
                # if line.free_qty_today < line.product_uom_qty:
                # warehouse = line.order_id.warehouse_id
                warehouse = line.sol_warehouse_id
                available_in_warehouse = line.product_id.with_context(warehouse=warehouse.id).qty_available
                if available_in_warehouse < line.product_uom_qty:
                    raise ValidationError(_('There is no enough quantity in the stock of'
                                            '\nProduct: %s'
                                            '\nWarehouse: %s'
                                            '\nAvailable: %s'
                                            '\nRequired: %s')
                                          % (line.product_id.name, warehouse.name, available_in_warehouse, line.product_uom_qty))
        return super(SaleOrder, self).action_confirm()
