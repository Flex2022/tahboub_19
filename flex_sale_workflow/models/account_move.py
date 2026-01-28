# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools


class AccountMove(models.Model):
    _inherit = 'account.move'

    ref_partner_id = fields.Many2one('res.partner', string='Responsible Partner')
    employee_id = fields.Many2one('hr.employee', string='Responsible Employee')

    # New field to control the visibility of the button
    show_ready_kanban_button = fields.Boolean(
        string='Show Ready Kanban Button',
        compute='_compute_show_ready_kanban_button',
        store=True,
    )

    @api.depends('company_id.active_sale_mrp_customization', 'company_id.flex_sale_stock_move_type')
    def _compute_show_ready_kanban_button(self):
        for move in self:
            move.show_ready_kanban_button = move.company_id.active_sale_mrp_customization and move.company_id.flex_sale_stock_move_type

    def action_picking_tree_ready_kanban(self):
        if self.company_id.active_sale_mrp_customization and self.company_id.flex_sale_stock_move_type:
            picking_type = self.company_id.flex_sale_stock_move_type

            if picking_type:
                # Get the action for creating a new picking using the specified picking type
                action = self.env.ref('stock.action_picking_form')._get_action_dict()

                # Optionally, you can set default values for the new picking
                action['context'] = {
                    'default_picking_type_id': picking_type.id,
                    'default_location_dest_id': picking_type.default_location_dest_id.id,
                    'default_location_id': picking_type.default_location_src_id.id,
                }

                return action

        return {
            'warning': {
                'title': _('Warning'),
                'message': _(
                    'The Sale MRP Customization is not activated or the flexible stock move type is not set for the company.'),
            }
        }