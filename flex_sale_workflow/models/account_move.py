# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Compatibility field kept for legacy views still using this expression in invisibility attrs.
    is_sale_installed = fields.Boolean(compute='_compute_is_sale_installed')
    # Odoo 19 uses `duplicated_ref_ids`; keep old boolean alias for legacy views.
    is_draft_duplicated_ref_ids = fields.Boolean(compute='_compute_is_draft_duplicated_ref_ids')
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

    @api.depends_context('uid')
    def _compute_is_sale_installed(self):
        sale_installed = 'sale.order' in self.env
        for move in self:
            move.is_sale_installed = sale_installed

    @api.depends('state', 'duplicated_ref_ids')
    def _compute_is_draft_duplicated_ref_ids(self):
        for move in self:
            move.is_draft_duplicated_ref_ids = move.state == 'draft' and bool(move.duplicated_ref_ids)

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

    def action_delete_duplicates(self):
        """Legacy compatibility hook for removed duplicate cleanup button."""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Duplicate Check'),
                'message': _('Use the duplicate warning links to review duplicated documents.'),
                'type': 'warning',
                'sticky': False,
            },
        }

    def sh_import_journal_item(self):
        """Legacy compatibility hook for journal-item import button."""
        action = self.env.ref('sh_import_journal_entry.action_journal_entry_view', raise_if_not_found=False)
        if action:
            return action._get_action_dict()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Import Journal Items'),
                'message': _('Journal import module is not available.'),
                'type': 'warning',
                'sticky': False,
            },
        }

    def sh_import_ail(self):
        """Backward-compatible alias for legacy view buttons."""
        return self.sh_import_journal_item()
