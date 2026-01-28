# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains('order_line')
    def check_category_discount_limit(self):
        # Skip validation if context flag is set or record is a draft and not validated yet
        if self.env.context.get('skip_discount_constraints'):
            return

        exceeded = {}
        for line in self.order_line:
            limit = self.env.user.get_categ_discount_limit(categ=line.categ_type)
            if limit is not False and line.discount >= float(limit):
                category = dict(self.order_line._fields['categ_type']._description_selection(self.env)).get(
                    line.categ_type)
                exceeded[category] = f"- {category} = {limit}%"
        if exceeded:
            message = '\n'.join(exceeded.values())
            raise ValidationError(_('You have a limited discount on categories as below:') + '\n' + message)

    def copy_sale(self):
        # Temporarily set a context flag to skip constraints
        ctx = self.env.context.copy()
        ctx['skip_discount_constraints'] = True

        sale_order = self.with_context(ctx).sudo().copy()
        sale_order.update({
            'name': self.env['ir.sequence'].next_by_code('sale.order'),
            'state': 'draft',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'target': 'current',
        }

    def copy_data(self, default=None):
        # Temporarily set a context flag to skip constraints
        ctx = self.env.context.copy()
        ctx['skip_discount_constraints'] = True

        return super(SaleOrder, self.with_context(ctx)).copy_data(default=default)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends_context('uid')
    @api.constrains('discount')
    def check_category_discount_limit(self):
        # Skip validation if context flag is set
        if self.env.context.get('skip_discount_constraints'):
            return

        # Validate discount against user's general discount limit
        if self.filtered(lambda sol: sol.discount > self.env.user.general_discount_limit):
            raise ValidationError(_(
                f'You have a limited general discount: {self.env.user.general_discount_limit} %'
            ))


#     @api.constrains('discount', 'categ_type')
#     def check_category_discount_limit(self):
#         orders = self.mapped('order_id')
#         exceeded = {}
#         for line in orders.order_line:
#             limit = self.env.user.get_categ_discount_limit(categ=line.categ_type)
#             if limit and line.discount > float(limit):
#                 category = dict(self._fields['categ_type']._description_selection(self.env)).get(line.categ_type)
#                 exceeded[category] = f"- {category} = {limit}%"
#         if exceeded:
#             message = '\n'.join(exceeded.values())
#             raise ValidationError(_('You have a limited discount on categories as below:') + '\n' + message)

