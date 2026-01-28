# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # state = fields.Selection([('draft', 'Quotation'), ('sent', 'Quotation Sent'), ('sale', 'Sales Order'),])
    state = fields.Selection(selection_add=[('pre_confirm', 'Pre-Confirm'), ('sale',)],
                             ondelete={'pre_confirm': lambda recs: recs.write({'state': 'draft'})})
    ref_partner_id = fields.Many2one('res.partner', string='Responsible Partner')
    employee_id = fields.Many2one('hr.employee', string='Responsible Employee')

    def button_print_manufacturing_orders(self):
        for order in self:
            # Assuming each Sale Order has only one Procurement Group
            procurement_group = order.procurement_group_id
            if procurement_group:
                manufacturing_orders = procurement_group.mrp_production_ids
                if manufacturing_orders:
                    # Print the Manufacturing Orders (you can customize this part based on your needs)
                    report_name = 'mrp_account_enterprise.mrp_cost_structure'  # Replace with your actual report name
                    report_action = self.env['ir.actions.report'].search([
                        ('report_name', '=', report_name),
                        ('model', '=', 'mrp.production'),
                    ], limit=1)

                    if report_action:
                        return report_action.report_action(manufacturing_orders)
        return False

    def action_review(self):
        self.filtered(lambda so: so.state in ['draft', 'sent']).write({'state': 'pre_confirm'})

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
        # send currency_id
        for move in res:
            move.write({'ref_partner_id': self.ref_partner_id.id})
            move.write({'employee_id': self.employee_id.id})
        return res

    @api.model
    def _create_analytic_account(self, sale_order):
        # Create an analytic account with the specified name
        analytic_account_name = f"{sale_order.name}"
        analytic_account = self.env['account.analytic.account'].create({
            'name': analytic_account_name,
            'partner_id': sale_order.partner_id.id,
        })

        # Link the analytic account to the sale order
        return analytic_account.id

    def create_product(self, sale_order):
        # Create a product template with the same name as the analytic account
        product_template = self.env['product.template'].create({
            'name': f"{sale_order.partner_id.name} - {sale_order.name}",
            'type': 'product',
        })
        if self.company_id.flex_sale_product_category:
            product_template.categ_id = self.company_id.flex_sale_product_category.id

        product_variant = self.env['product.product'].search([('product_tmpl_id', '=', product_template.id)])
        return product_variant

    def _prepare_procurement_group_vals(self):
        return {
            'name': self.name,
            'move_type': self.picking_policy,
            'sale_id': self.id,
            'partner_id': self.partner_shipping_id.id,
        }

    def _create_manufacturing_order(self, sale_order):
        # create a procurement group
        group_id = self.env['procurement.group'].create(self._prepare_procurement_group_vals())
        self.procurement_group_id = group_id

        # create a product
        product = self.create_product(sale_order)

        # create manufacturing
        if product:
            # Create a manufacturing order for the found product
            manufacturing_order = self.env['mrp.production'].create({
                # 'name': f"{sale_order.partner_id.name} - {sale_order.name}",
                'product_id': product.id,
                'product_qty': 1.0,
                'product_uom_id': product.uom_id.id if product.uom_id else 1,
            })
            self.procurement_group_id.mrp_production_ids = [(6, 0, [manufacturing_order.id])]
            manufacturing_order._onchange_product_id()
            manufacturing_order._onchange_move_finished_product()
            return manufacturing_order

    def action_confirm(self):
        # Call the original method
        res = super(SaleOrder, self).action_confirm()
        # Create analytic account after confirming the sale order
        for order in self:
            if order.state == 'sale':
                if order.company_id.active_sale_mrp_customization:
                    order.analytic_account_id = self._create_analytic_account(order)
                    manufacturing_order = self._create_manufacturing_order(order)
                    manufacturing_order.analytic_account_id = order.analytic_account_id.id
        return res

    # def action_draft(self):
    #     res = super(SaleOrder, self).action_draft()
    #     for line in self.filtered(lambda x: x.state == 'draft').order_line:
    #         line.product_uom_change()
    #     return res

    # is_reviewed = fields.Boolean('Sale Order Reviewed?', tracking=1)
    # def mark_as_reviewed(self):
    #     self.filtered(lambda so: not so.is_reviewed).write({'is_reviewed': True})

    # def action_confirm(self):
    #     if self.filtered(lambda so: not so.is_reviewed):
    #         if self.env.user.has_group('flex_sale_workflow.group_sale_review'):
    #             self.mark_as_reviewed()
    #             return super(SaleOrder, self).action_confirm()
    #         else:
    #             raise UserError(_("The sale order should be reviewed first and you don't have permission to review it."))
    #     else:
    #         return super(SaleOrder, self).action_confirm()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    flex_product_uom = fields.Many2one('uom.uom', related='product_id.uom_id')

    # state = fields.Selection([('draft', 'Quotation'), ('sent', 'Quotation Sent'), ('sale', 'Sales Order'),])
    show_on_hand_qty_status_button = fields.Boolean(related='product_id.show_on_hand_qty_status_button')

    # flex_is_deliver is boolean in order line to do a constraint in stock picking if one line with this it will not be to confirmed
    flex_is_deliver = fields.Boolean(string='Deliver?', default=False)
    product_code = fields.Char(string='Internal Reference', related='product_id.default_code')

    def action_open_quants(self):
        action = self.product_id.action_open_quants()
        action['context'].update({'create': 0, 'edit': 0, 'delete': 0})
        return action
