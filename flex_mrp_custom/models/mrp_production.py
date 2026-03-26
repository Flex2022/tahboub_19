# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    customer_project_id = fields.Many2one('customer.project', string='Project Name')

    @api.model
    def create(self, values):
        production = super(MrpProduction, self).create(values)
        # Apply _onchange_product_id when creating a new record
        production._onchange_product_id()
        production._onchange_picking_type()
        return production

    def action_get_sale_product(self):
        return {
            'name': self.env._('Get Products From Sale Order'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.get.product',
            'view_id': self.env.ref('flex_mrp_custom.sale_get_product_form').id,
            'target': 'new',
            'context': {'default_production_id': self.id, },
        }

    def action_import_component(self):
        return {
            'name': self.env._('Import Components'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'import.component',
            'view_id': self.env.ref('flex_mrp_custom.import_component_form').id,
            'target': 'new',
            'context': {'default_production_id': self.id, },
        }

    def action_open_project(self):
        """Compatibility action used by inherited MRP form buttons."""
        self.ensure_one()

        # Odoo core project_mrp links MOs with project.project via project_id.
        project = self.project_id
        if project:
            return {
                'type': 'ir.actions.act_window',
                'name': self.env._('Project'),
                'res_model': 'project.project',
                'res_id': project.id,
                'view_mode': 'form',
                'target': 'current',
            }

        # Keep backward compatibility with custom customer projects.
        if self.customer_project_id:
            return {
                'type': 'ir.actions.act_window',
                'name': self.env._('Project'),
                'res_model': 'customer.project',
                'res_id': self.customer_project_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': self.env._('Project'),
                'message': self.env._('No project is linked to this manufacturing order.'),
                'type': 'warning',
                'sticky': False,
            },
        }
