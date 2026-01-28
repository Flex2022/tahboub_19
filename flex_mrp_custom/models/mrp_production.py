# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    customer_project_id = fields.Many2one('customer.project', string='Project Name',
                                          states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.model
    def create(self, values):
        production = super(MrpProduction, self).create(values)
        # Apply _onchange_product_id when creating a new record
        production._onchange_product_id()
        production._onchange_picking_type()
        return production

    def action_get_sale_product(self):
        return {
            'name': _('Get Products From Sale Order'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.get.product',
            'view_id': self.env.ref('flex_mrp_custom.sale_get_product_form').id,
            'target': 'new',
            'context': {'default_production_id': self.id, },
        }

    def action_import_component(self):
        return {
            'name': _('Import Components'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'import.component',
            'view_id': self.env.ref('flex_mrp_custom.import_component_form').id,
            'target': 'new',
            'context': {'default_production_id': self.id, },
        }
