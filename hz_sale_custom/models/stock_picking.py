# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        if self.sale_id:
            if self.sale_id.partner_id.credit_check:
                return super(StockPicking, self).button_validate()
            # if self.sale_id.order_line.filtered(lambda l: not l.display_type and l.product_uom_qty > l.qty_invoiced):
            #     message = _('The current transfer is related to a sale order that is not fully invoice.')
            #     raise ValidationError(message)
            # elif any(self.sale_id.invoice_ids.filtered(lambda inv: inv.state != 'cancel').mapped('amount_residual')):
            #     message = _('The current transfer is related to a sale order that is not fully paid.')
            #     raise ValidationError(message)

            paid_product_ids = self.sale_id.invoice_ids.filtered(lambda inv: inv.state != 'cancel' and inv.payment_state == 'paid').mapped('invoice_line_ids').filtered(lambda inv_line: inv_line.product_id in self.move_ids.product_id).mapped('product_id')
            list_of_not_paid_product = []
            message = """"""
            counter = 0
            for operation in self.move_ids:
                if operation.product_id not in paid_product_ids:
                    list_of_not_paid_product.append(operation.product_id.name)
                    counter = counter + 1
                    message += "\n" + str(counter) + "- (" + str(
                        operation.product_id.name) + ")"

            if len(list_of_not_paid_product) >= 1:
                message = _('The current transfer have products Not Paid like:' + "\n" + message)
                raise ValidationError(message)

        return super(StockPicking, self).button_validate()
